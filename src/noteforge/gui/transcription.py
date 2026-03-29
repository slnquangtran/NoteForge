import customtkinter as ctk
import torch
import numpy as np
import threading
import queue
import time
import json
import random
import wave
import collections
import os
from datetime import datetime
from tkinter import messagebox

from ..transcription.recorder import AudioRecorder
from ..transcription.processor import VADProcessor
from ..transcription.engine import TranscriptionEngine
from ..config.paths import get_recordings_dir
from ..config.settings import get_setting

class PerformanceMonitor:
    def __init__(self):
        self.stats = {
            'captured': 0,
            'dropped_capture': 0,
            'processed_vad': 0,
            'dropped_vad': 0,
            'processed_vosk': 0
        }
        self.start_time = time.time()
    
    def log(self, key):
        self.stats[key] = self.stats.get(key, 0) + 1
        
    def get_fps(self, key):
        elapsed = time.time() - self.start_time
        if elapsed < 1: return 0
        return int(self.stats.get(key, 0) / elapsed)

    def reset(self):
        self.stats = {k:0 for k in self.stats}
        self.start_time = time.time()

class HybridTranscriberApp(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        
        self.monitor = PerformanceMonitor()
        self.title("NoteForge - Real-Time Transcription")
        self.configure(fg_color="#312C51")
        
        # Configuration
        self.SAMPLE_RATE = 16000
        self.FRAME_DURATION_MS = 20
        self.FRAME_SIZE = int(self.SAMPLE_RATE * self.FRAME_DURATION_MS / 1000)
        self.FRAME_BYTES = self.FRAME_SIZE * 2
        
        # Transcription Logic
        self.recorder = AudioRecorder(self.SAMPLE_RATE, self.FRAME_DURATION_MS)
        self.vad_processor = VADProcessor(self.SAMPLE_RATE)
        self.engine = TranscriptionEngine(self.SAMPLE_RATE)
        
        self.WHISPER_MODEL_SIZE = get_setting("whisper_model_size")

        # State
        self.is_recording = False
        self.recording_buffer = []
        self.recordings_dir = get_recordings_dir()
        self.bart_model = None # Lazy load
        
        # Queues
        self.vad_queue = queue.Queue(maxsize=100)
        self.vosk_queue = queue.Queue(maxsize=500)
        self.whisper_queue = queue.Queue()
        self.display_queue = queue.Queue()
        self.meter_queue = queue.Queue()

        self.last_queue_sizes = []
        self.device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
        
        # Audio Devices
        self.devices_list = self.recorder.get_devices()
        self.selected_mic_index = None

        # --- UI Layout ---
        self.summarize_btn = None
        self.create_widgets()
        self.update_ui_loop()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Top Controls
        top_card = ctk.CTkFrame(self, fg_color="#48426D", corner_radius=25)
        top_card.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        top_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=15)
        top_frame.grid_columnconfigure(1, weight=1)
        
        self.record_btn = ctk.CTkButton(
            top_frame, 
            text="Start Recording", 
            command=self.toggle_recording, 
            font=("Segoe UI", 16, "bold"), 
            height=40,
            corner_radius=15,
            fg_color="#F0C38E",
            hover_color="#DEB17E",
            text_color="#312C51"
        )
        self.record_btn.grid(row=0, column=0, padx=(0, 20), sticky="w")

        self.status_label = ctk.CTkLabel(top_frame, text="Ready", font=("Segoe UI", 14), text_color="gray")
        self.status_label.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(top_frame, text="Mic:", font=("Segoe UI", 14)).grid(row=0, column=2, padx=(10, 5), sticky="e")
        mic_vals = [x[1] for x in self.devices_list]
        self.mic_menu = ctk.CTkOptionMenu(top_frame, values=mic_vals, command=self.change_mic, width=200)
        if mic_vals: self.mic_menu.set(mic_vals[0])
        self.mic_menu.grid(row=0, column=3, sticky="e")

        # Level Meter
        self.level_bar = ctk.CTkProgressBar(self, height=12, corner_radius=8, fg_color="#48426D", progress_color="#F0C38E")
        self.level_bar.grid(row=1, column=0, padx=25, pady=(0, 20), sticky="ew")
        self.level_bar.set(0)

        # Textbox
        self.textbox = ctk.CTkTextbox(self, font=("Segoe UI", 16), wrap="word", corner_radius=20, border_width=2, border_color="#48426D")
        self.textbox.grid(row=2, column=0, padx=20, pady=0, sticky="nsew")
        self.textbox.tag_config("gray", foreground="gray")
        self.textbox.tag_config("white", foreground="white")
        self.textbox.configure(state="disabled")

        # Bottom Controls
        bot_card = ctk.CTkFrame(self, fg_color="#48426D", corner_radius=25)
        bot_card.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        
        bot_frame = ctk.CTkFrame(bot_card, fg_color="transparent")
        bot_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(bot_frame, text="Clear", command=self.clear_text, width=100, fg_color="#312C51").grid(row=0, column=0, padx=(0,10), sticky="w")
        ctk.CTkButton(bot_frame, text="Save", command=self.save_text, width=100, fg_color="#F1AA9B", text_color="#312C51").grid(row=0, column=1, sticky="w")
        
        self.summarize_btn = ctk.CTkButton(
            bot_frame, 
            text="Summarize 🪄", 
            command=self.summarize_text,
            width=120,
            fg_color="#F1AA9B",
            text_color="#312C51"
        )
        self.summarize_btn.grid(row=0, column=2, padx=10, sticky="w")
        
        ctk.CTkLabel(bot_frame, text="Hybrid Mode Active", font=("Segoe UI", 12), text_color="gray").grid(row=0, column=3, sticky="e")

    def summarize_text(self):
        text = self.textbox.get("1.0", ctk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No text to summarize!")
            return

        self.summarize_btn.configure(state="disabled", text="Summarizing...")
        threading.Thread(target=self.run_summarization, args=(text,), daemon=True).start()

    def run_summarization(self, text):
        try:
            from ..models.manager import ModelManager
            if not self.bart_model:
                self.bart_model = ModelManager.get_bart_pipeline()
            
            # Simple chunking
            chunks = [text[i:i+3000] for i in range(0, len(text), 3000)]
            summaries = []
            for chunk in chunks:
                if len(chunk) < 50: continue
                res = self.bart_model(chunk, max_length=130, min_length=30, do_sample=False)
                summaries.append(res[0]['summary_text'])
            
            self.after(0, lambda: self.show_summary_popup(text, " ".join(summaries)))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Summarization Error", str(e)))
        finally:
            self.after(0, lambda: self.summarize_btn.configure(state="normal", text="Summarize 🪄"))

    def show_summary_popup(self, original_text, summary):
        popup = ctk.CTkToplevel(self)
        popup.title("Summary")
        popup.geometry("600x500")
        
        ctk.CTkLabel(popup, text=f"Summary Result", font=("Segoe UI", 14, "bold")).pack(pady=10)
        txt = ctk.CTkTextbox(popup, font=("Segoe UI", 14), wrap="word")
        txt.pack(fill="both", expand=True, padx=20, pady=10)
        txt.insert("1.0", summary)
        
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Copy", command=lambda: [self.clipboard_clear(), self.clipboard_append(summary), messagebox.showinfo("Copied", "Copied to clipboard!")]).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Close", command=popup.destroy).pack(side="left", padx=10)

    def change_mic(self, choice):
        for idx, name in self.devices_list:
            if name == choice:
                self.selected_mic_index = idx

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_btn.configure(text="Stop Recording", fg_color="#F1AA9B")
        self.status_label.configure(text="Recording...")
        self.recording_buffer = []
        
        threading.Thread(target=self.audio_capture_loop, daemon=True).start()
        threading.Thread(target=self.vad_processing_loop, daemon=True).start()
        threading.Thread(target=self.vosk_processing_loop, daemon=True).start()
        threading.Thread(target=self.whisper_processing_loop, daemon=True).start()

    def stop_recording(self):
        self.is_recording = False
        self.recorder.stop()
        self.record_btn.configure(text="Start Recording", fg_color="#F0C38E")
        self.level_bar.set(0)
        
        if self.recording_buffer:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = os.path.join(self.recordings_dir, f"recording_{timestamp}.wav")
            with wave.open(audio_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.SAMPLE_RATE)
                wf.writeframes(b"".join(self.recording_buffer))
            
            transcript_path = os.path.join(self.recordings_dir, f"transcript_{timestamp}.txt")
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(self.textbox.get("1.0", ctk.END).strip())
            
        self.status_label.configure(text="Ready")

    def audio_capture_loop(self):
        def callback(indata):
            frame_bytes = indata.tobytes()
            self.monitor.log('captured')
            self.recording_buffer.append(frame_bytes)
            try:
                self.vad_queue.put_nowait(frame_bytes)
            except queue.Full: pass
            
            audio_data = indata.astype(np.float32).flatten()
            peak = np.max(np.abs(audio_data))
            self.meter_queue.put(float(peak / 20000.0))

        self.recorder.start(self.selected_mic_index, callback)

    def vad_processing_loop(self):
        while self.is_recording:
            try:
                data = self.vad_queue.get(timeout=0.1)
                is_active = self.vad_processor.is_speech(data)
                self.vosk_queue.put_nowait((data, is_active))
            except (queue.Empty, queue.Full): continue

    def vosk_processing_loop(self):
        rec = self.engine.get_vosk_recognizer()
        sentence_buffer = collections.deque()
        silence_frames = 0
        is_speech = False
        
        while self.is_recording:
            try:
                data, is_active = self.vosk_queue.get(timeout=0.1)
                if rec.AcceptWaveform(data):
                    text = json.loads(rec.Result()).get("text", "")
                    if text: self.display_queue.put(("draft", text))
                
                # Whisper logic
                if is_active:
                    is_speech = True
                    silence_frames = 0
                    sentence_buffer.append(data)
                else:
                    if is_speech:
                        silence_frames += 1
                        sentence_buffer.append(data)
                        if silence_frames > 25:
                            full_audio = b"".join(sentence_buffer)
                            if len(full_audio) > self.SAMPLE_RATE:
                                self.whisper_queue.put_nowait(full_audio)
                            sentence_buffer.clear()
                            is_speech = False
            except: continue

    def whisper_processing_loop(self):
        while self.is_recording:
            try:
                audio_bytes = self.whisper_queue.get(timeout=1)
                text = self.engine.transcribe_whisper(audio_bytes, self.WHISPER_MODEL_SIZE)
                if text: self.display_queue.put(("final", text))
            except: continue

    def update_ui_loop(self):
        while not self.display_queue.empty():
            try:
                msg_type, content = self.display_queue.get_nowait()
                if msg_type == "draft":
                    self.insert_text(f"[Draft] {content}\n", "gray")
                elif msg_type == "final":
                    self.replace_last_draft_with_final(content)
            except: break

        if not self.meter_queue.empty():
            try:
                level = self.meter_queue.get_nowait()
                self.level_bar.set(max(0.0, min(1.0, float(level))))
            except: pass
        
        self.after(50 if self.is_recording else 200, self.update_ui_loop)

    def insert_text(self, text, tag):
        self.textbox.configure(state="normal")
        self.textbox.insert(ctk.END, text, tag)
        self.textbox.see(ctk.END)
        self.textbox.configure(state="disabled")

    def replace_last_draft_with_final(self, text):
        self.textbox.configure(state="normal")
        last_index = self.textbox.search("[Draft]", "end-1c", backwards=True)
        if last_index:
            line_end = self.textbox.index(f"{last_index} lineend + 1c")
            self.textbox.delete(last_index, line_end)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.textbox.insert(ctk.END, f"[{timestamp}] {text}\n", "white")
        self.textbox.see(ctk.END)
        self.textbox.configure(state="disabled")

    def clear_text(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", ctk.END)
        self.textbox.configure(state="disabled")

    def save_text(self):
        path = messagebox.asksaveasfilename(defaultextension=".txt")
        if path:
            with open(path, "w") as f: f.write(self.textbox.get("1.0", ctk.END))
