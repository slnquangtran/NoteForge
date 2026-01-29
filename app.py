import customtkinter as ctk
import threading
import queue
import time
import os
import json
import numpy as np
import sounddevice as sd
import pyaudio
import webrtcvad
import collections
from datetime import datetime
from tkinter import filedialog, messagebox

# --- Dependencies Check ---
try:
    import vosk
except ImportError:
    vosk = None

try:
    import whisper
except ImportError:
    whisper = None

class HybridTranscriberApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Hybrid Voice Transcriber (Vosk + Whisper)")
        self.geometry("1100x850")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # --- Configuration ---
        self.SAMPLE_RATE = 16000
        self.FRAME_DURATION_MS = 20
        self.FRAME_SIZE = int(self.SAMPLE_RATE * self.FRAME_DURATION_MS / 1000)
        self.VOSK_MODEL_PATH = "model"
        self.WHISPER_MODEL_SIZE = "base"

        # --- State ---
        self.is_recording = False
        self.audio_queue = queue.Queue()       # Raw audio chunks (bytes)
        self.whisper_queue = queue.Queue()     # Completed sentences (numpy array)
        self.display_queue = queue.Queue()     # UI updates (type, text)
        self.meter_queue = queue.Queue()       # Audio level updates

        self.vosk_model = None
        self.whisper_model = None
        self.vad = webrtcvad.Vad(2) # Mode 2: Aggressive

        # Load Vosk Model immediately (fast)
        if vosk and os.path.exists(self.VOSK_MODEL_PATH):
            try:
                self.vosk_model = vosk.Model(self.VOSK_MODEL_PATH)
            except Exception as e:
                print(f"Vosk Load Error: {e}")

        # Threads
        self.capture_thread = None
        self.vosk_thread = None
        self.whisper_thread = None
        
        # Audio Devices
        self.devices_list = []
        self.get_available_devices()
        self.selected_mic_index = None

        # --- UI Layout ---
        self.create_widgets()
        
        # --- Start Main Loop ---
        self.update_ui_loop()

    def get_available_devices(self):
        self.devices_list = []
        try:
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            default_input = p.get_default_input_device_info()['index']
            
            for i in range(0, numdevices):
                dev = p.get_device_info_by_host_api_device_index(0, i)
                if dev.get('maxInputChannels') > 0:
                    name = dev.get('name')
                    is_def = " (Default)" if i == default_input else ""
                    self.devices_list.append((i, f"{i}: {name}{is_def}"))
            p.terminate()
        except:
             self.devices_list = [(None, "Default Device")]

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Top Controls
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.record_btn = ctk.CTkButton(top_frame, text="Start Recording", command=self.toggle_recording, font=("Arial", 16, "bold"), height=40)
        self.record_btn.pack(side="left", padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(top_frame, text="Ready", font=("Arial", 14))
        self.status_label.pack(side="left", padx=10)

        # Mic Selector
        mic_vals = [x[1] for x in self.devices_list]
        self.mic_menu = ctk.CTkOptionMenu(top_frame, values=mic_vals, command=self.change_mic, width=250)
        if mic_vals: self.mic_menu.set(mic_vals[0])
        self.mic_menu.pack(side="right", padx=10)
        ctk.CTkLabel(top_frame, text="Mic:").pack(side="right")

        # 2. Level Meter
        self.level_bar = ctk.CTkProgressBar(self, height=15)
        self.level_bar.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.level_bar.set(0)

        # 3. Transcription Area
        self.textbox = ctk.CTkTextbox(self, font=("Segoe UI", 16), wrap="word", padx=10, pady=10)
        self.textbox.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.textbox.tag_config("gray", foreground="gray")
        self.textbox.tag_config("black", foreground="white") # Dark mode white
        
        # 4. Bottom Controls
        bot_frame = ctk.CTkFrame(self, fg_color="transparent")
        bot_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        ctk.CTkButton(bot_frame, text="Clear", command=self.clear_text, width=80).pack(side="left", padx=5)
        ctk.CTkButton(bot_frame, text="Save", command=self.save_text, width=80).pack(side="left", padx=5)
        ctk.CTkLabel(bot_frame, text="Mode: Hybrid (Vosk Real-time -> Whisper Correction)", text_color="gray").pack(side="right", padx=10)

    def change_mic(self, choice):
        for idx, name in self.devices_list:
            if name == choice:
                self.selected_mic_index = idx
                print(f"Selected Mic Index: {idx}")

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        if not self.vosk_model:
            messagebox.showerror("Error", "Vosk model not found! Please run download_models.py")
            return

        self.is_recording = True
        self.record_btn.configure(text="Stop Recording", fg_color="red")
        self.status_label.configure(text="Initializing Whisper...")
        
        # Clear queues
        with self.audio_queue.mutex: self.audio_queue.queue.clear()
        with self.whisper_queue.mutex: self.whisper_queue.queue.clear()

        # Start Threads
        self.capture_thread = threading.Thread(target=self.audio_capture_loop)
        self.vosk_thread = threading.Thread(target=self.vosk_processing_loop)
        self.whisper_thread = threading.Thread(target=self.whisper_processing_loop)
        
        self.capture_thread.start()
        self.vosk_thread.start()
        self.whisper_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.record_btn.configure(text="Start Recording", fg_color="#2CC985") # Default green-ish
        self.status_label.configure(text="Stopped")
        self.level_bar.set(0)

    def audio_capture_loop(self):
        """Captures raw audio from PyAudio"""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=self.SAMPLE_RATE,
                            input=True,
                            input_device_index=self.selected_mic_index,
                            frames_per_buffer=self.FRAME_SIZE)
            
            self.display_queue.put(("status", "Listening..."))
            
            while self.is_recording:
                data = stream.read(self.FRAME_SIZE, exception_on_overflow=False)
                self.audio_queue.put(data)
                
                # Update Meter
                try:
                    # Simple RMS
                    audio_np = np.frombuffer(data, dtype=np.int16)
                    volume = np.linalg.norm(audio_np) / 1000
                    self.meter_queue.put(min(volume / 50, 1.0))
                except:
                    pass

            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            self.display_queue.put(("error", f"Mic Error: {e}"))
            self.stop_recording()

    def vosk_processing_loop(self):
        """Processes buffer for Real-time (Vosk) + VAD segmentation"""
        rec = vosk.KaldiRecognizer(self.vosk_model, self.SAMPLE_RATE)
        
        # Audio buffer for the current sentence
        sentence_buffer = collections.deque()
        silence_frames = 0
        is_speech = False
        
        while self.is_recording or not self.audio_queue.empty():
            try:
                data = self.audio_queue.get(timeout=1)
            except queue.Empty:
                continue

            # 1. VAD Check
            try:
                is_active = self.vad.is_speech(data, self.SAMPLE_RATE)
            except:
                is_active = False # Frame size mismatch safety

            # 2. Vosk Recognition (Streaming)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    # Final result from Vosk -> Send to display as "Draft"
                    # But we actually rely on VAD for true sentence end to trigger Whisper
                    # So we show this as gray text
                    self.display_queue.put(("draft", text))
            else:
                partial = json.loads(rec.PartialResult())
                p_text = partial.get("partial", "")
                if p_text:
                    self.display_queue.put(("partial", p_text))

            # 3. Buffer Management for Whisper
            if is_active:
                if not is_speech:
                    is_speech = True # Speech started
                    # Potential logic: Start new buffer, maybe rewind a bit?
                silence_frames = 0
                sentence_buffer.append(data)
            else:
                if is_speech:
                    silence_frames += 1
                    sentence_buffer.append(data) # Keep trailing silence
                    
                    # Sentence End Detection logic
                    # 25 frames * 20ms = 500ms silence
                    if silence_frames > 25: 
                        is_speech = False
                        
                        # Package up for Whisper
                        full_audio = b"".join(sentence_buffer)
                        # Only transcribe if decent length (>0.5s)
                        if len(full_audio) > self.SAMPLE_RATE * 1: # 1 sec bytes (2 bytes per sample)
                            self.whisper_queue.put(full_audio)
                            self.display_queue.put(("status", "Improving accuracy..."))
                        
                        sentence_buffer.clear()
                else: 
                     # Keeping a ring buffer of silence before speech could be good, 
                     # but for simplicity we ignore pure silence.
                     pass

    def whisper_processing_loop(self):
        """Loads Whisper (once) and processes sentences for accuracy"""
        if not whisper:
            self.display_queue.put(("error", "Whisper module not found."))
            return

        try:
            if self.whisper_model is None:
                self.display_queue.put(("status", "Loading Whisper Model (takes time)..."))
                self.whisper_model = whisper.load_model(self.WHISPER_MODEL_SIZE)
                self.display_queue.put(("status", "Whisper Ready. Listening..."))
        except Exception as e:
            self.display_queue.put(("error", f"Whisper Load Error: {e}"))
            return

        while self.is_recording or not self.whisper_queue.empty():
            try:
                audio_bytes = self.whisper_queue.get(timeout=1)
            except queue.Empty:
                continue

            try:
                # Convert bytes to float32 numpy array for Whisper
                audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Transcribe
                result = self.whisper_model.transcribe(audio_np, fp16=False, language="english")
                text = result.get("text", "").strip()
                
                if text:
                    self.display_queue.put(("final", text))
                    
            except Exception as e:
                 print(f"Whisper Error: {e}")

    def update_ui_loop(self):
        # 1. Handle Display Updates
        try:
            while not self.display_queue.empty():
                msg_type, content = self.display_queue.get_nowait()
                
                if msg_type == "status":
                    self.status_label.configure(text=content)
                elif msg_type == "error":
                    messagebox.showerror("Error", content)
                elif msg_type == "partial":
                    # For partial, we might want to update a "preview" line
                    # For now, let's just log or ignoring to avoid cluttering if we have draft
                    pass 
                elif msg_type == "draft":
                    # Vosk final result (Gray)
                    self.insert_text(f"[Draft] {content}\n", "gray")
                elif msg_type == "final":
                    # Whisper result (Black/White - Final)
                    # Ideally, we would replace the "Draft" line. 
                    # For simplicity, we append "Final".
                    # A better UI would replace the last line if it was draft.
                    self.replace_last_draft_with_final(content)

        except queue.Empty:
            pass

        # 2. Handle Meter
        try:
            if not self.meter_queue.empty():
                level = self.meter_queue.get_nowait()
                self.level_bar.set(level)
        except:
            pass

        self.after(50, self.update_ui_loop)

    def insert_text(self, text, tag):
        self.textbox.configure(state="normal")
        self.textbox.insert(ctk.END, text, tag)
        self.textbox.see(ctk.END)
        self.textbox.configure(state="disabled")

    def replace_last_draft_with_final(self, text):
        self.textbox.configure(state="normal")
        
        # Check if last line is draft
        # This is tricky in Tkinter without strict line management
        # Simplified: Just append Final with a timestamp like a chat
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        final_line = f"[{timestamp}] {text}\n"
        
        # Delete the last "Draft" line if possible? 
        # A simple approach: Just print Final text clearly.
        # User requested accuracy.
        
        # Search for last [Draft] and delete it?
        # Let's search back from end
        last_index = self.textbox.search("[Draft]", "end-1c", backwards=True)
        if last_index:
            line_end = self.textbox.index(f"{last_index} lineend + 1c")
            self.textbox.delete(last_index, line_end)
        
        self.textbox.insert(ctk.END, final_line, "black")
        self.textbox.see(ctk.END)
        self.textbox.configure(state="disabled")

    def clear_text(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", ctk.END)
        self.textbox.configure(state="disabled")

    def save_text(self):
        text = self.textbox.get("1.0", ctk.END)
        filename = filedialog.asksaveasfilename(defaultextension=".txt")
        if filename:
            with open(filename, "w") as f:
                f.write(text)

if __name__ == "__main__":
    app = HybridTranscriberApp()
    app.mainloop()
