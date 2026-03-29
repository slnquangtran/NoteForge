# Wrapper for the new package-based transcription system
import sys
import os

# Ensure src is in path
repo_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from noteforge.transcription.recorder import AudioRecorder
from noteforge.transcription.processor import VADProcessor
from noteforge.transcription.engine import TranscriptionEngine
from noteforge.config.paths import get_recordings_dir
import config_manager
import torch
import numpy as np
import threading
import queue
import time
import json
import random
import wave
import collections
from datetime import datetime
from tkinter import filedialog, messagebox

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
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Configuration
        self.SAMPLE_RATE = 16000
        self.FRAME_DURATION_MS = 20
        self.FRAME_SIZE = int(self.SAMPLE_RATE * self.FRAME_DURATION_MS / 1000)
        self.FRAME_BYTES = self.FRAME_SIZE * 2
        
        # Transcription Logic
        self.recorder = AudioRecorder(self.SAMPLE_RATE, self.FRAME_DURATION_MS)
        self.vad_processor = VADProcessor(self.SAMPLE_RATE)
        self.engine = TranscriptionEngine(self.SAMPLE_RATE)
        
        self.WHISPER_MODEL_SIZE = config_manager.get_setting("whisper_model_size")

        # State
        self.is_recording = False
        self.recording_buffer = []
        self.recordings_dir = get_recordings_dir()
        
        # Queues
        self.vad_queue = queue.Queue(maxsize=100)
        self.vosk_queue = queue.Queue(maxsize=500)
        self.whisper_queue = queue.Queue()
        self.display_queue = queue.Queue()
        self.meter_queue = queue.Queue()

        self.last_queue_sizes = []
        self.device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
        print(f"INFO: Using device for transcription: {self.device}")
        
        # Audio Devices
        self.devices_list = self.recorder.get_devices()
        self.selected_mic_index = None

        # --- UI Layout ---
        self.summarize_btn = None # Init in create_widgets
        self.create_widgets()
        self.update_ui_loop()

    def get_available_devices(self):
        # Compatibility wrapper
        self.devices_list = self.recorder.get_devices()

    def _find_model_path(self):
        """Search for the Vosk model in multiple logical locations"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        possible_paths = [
            os.path.join(base_dir, "model"),                     # NoteForge/model
            os.path.join(os.path.dirname(base_dir), "model"),    # Exp/model
            os.path.join(os.path.dirname(os.path.dirname(base_dir)), "model") # Desktop/model (fallback)
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.isdir(path):
                # Check for characteristic Vosk folder content (am/conf/graph)
                if os.path.exists(os.path.join(path, "am")):
                    print(f"DEBUG: Found valid Vosk model at: '{path}'")
                    return path
                    
        print(f"WARNING: Could not find valid Vosk model folder in: {possible_paths}")
        return possible_paths[1] # Default to Exp/model if not sure

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Allow textbox to expand

        # --- 1. Top Controls Card ---
        top_card = ctk.CTkFrame(self, fg_color="#48426D", corner_radius=25)
        top_card.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        top_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=15)
        top_frame.grid_columnconfigure(0, weight=0) # Record button
        top_frame.grid_columnconfigure(1, weight=1) # Status label (expands)
        top_frame.grid_columnconfigure(2, weight=0) # "Mic:" label
        top_frame.grid_columnconfigure(3, weight=0) # Mic selector menu
        
        # Record Button
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
        self.record_btn.grid(row=0, column=0, padx=(0, 20), pady=0, sticky="w") # Pad to the right

        # Status Label
        self.status_label = ctk.CTkLabel(top_frame, text="Ready", font=("Segoe UI", 14), text_color="gray")
        self.status_label.grid(row=0, column=1, padx=0, pady=0, sticky="w") # Aligned to left of its column

        # Mic Selector
        mic_label = ctk.CTkLabel(top_frame, text="Mic:", font=("Segoe UI", 14))
        mic_label.grid(row=0, column=2, padx=(10, 5), pady=0, sticky="e") # Pad to the left for separation
        
        mic_vals = [x[1] for x in self.devices_list]
        self.mic_menu = ctk.CTkOptionMenu(top_frame, values=mic_vals, command=self.change_mic, width=200, font=("Segoe UI", 14))
        if mic_vals: self.mic_menu.set(mic_vals[0])
        self.mic_menu.grid(row=0, column=3, padx=(0, 0), pady=0, sticky="e") # Aligned to right of its column


        # --- 2. Level Meter ---
        self.level_bar = ctk.CTkProgressBar(self, height=12, corner_radius=8, fg_color="#48426D", progress_color="#F0C38E")
        self.level_bar.grid(row=1, column=0, padx=25, pady=(0, 20), sticky="ew")
        self.level_bar.set(0)

        # --- 3. Transcription Area (Textbox) ---
        self.textbox = ctk.CTkTextbox(self, font=("Segoe UI", 16), wrap="word", padx=15, pady=15, corner_radius=20, border_width=2, border_color="#48426D")
        self.textbox.grid(row=2, column=0, padx=20, pady=0, sticky="nsew")
        self.textbox.tag_config("gray", foreground="gray")
        self.textbox.tag_config("black", foreground="white") # Dark mode white
        self.textbox.configure(state="disabled") # Start disabled

        # --- 4. Bottom Controls Card ---
        bot_card = ctk.CTkFrame(self, fg_color="#48426D", corner_radius=25)
        bot_card.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        
        bot_frame = ctk.CTkFrame(bot_card, fg_color="transparent")
        bot_frame.pack(fill="x", padx=20, pady=15)
        bot_frame.grid_columnconfigure(0, weight=0) # Clear button
        bot_frame.grid_columnconfigure(1, weight=0) # Save button
        bot_frame.grid_columnconfigure(2, weight=1) # Mode label (expands)
        
        # Clear Button
        ctk.CTkButton(bot_frame, text="Clear", command=self.clear_text, width=100, font=("Segoe UI", 14), corner_radius=12, fg_color="#312C51", hover_color="#48426D").grid(row=0, column=0, padx=(0,10), pady=0, sticky="w")
        # Save Button
        ctk.CTkButton(bot_frame, text="Save", command=self.save_text, width=100, font=("Segoe UI", 14), corner_radius=12, fg_color="#F1AA9B", hover_color="#DD998A", text_color="#312C51").grid(row=0, column=1, padx=0, pady=0, sticky="w")
        
        # Summarize Button
        self.summarize_btn = ctk.CTkButton(
            bot_frame, 
            text="Summarize 🪄", 
            command=self.summarize_text,
            width=120,
            font=("Segoe UI", 14),
            corner_radius=12,
            fg_color="#F1AA9B",
            hover_color="#DD998A",
            text_color="#312C51"
        )
        self.summarize_btn.grid(row=0, column=2, padx=(10,10), pady=0, sticky="w")
        
        # Mode Label
        ctk.CTkLabel(bot_frame, text="Mode: Hybrid (Vosk Real-time -> Whisper Correction)", font=("Segoe UI", 12), text_color="gray").grid(row=0, column=3, padx=(20,0), pady=0, sticky="e") # Pad to the left

    def summarize_text(self):
        """Trigger summarization of current transcription"""
        text = self.textbox.get("1.0", ctk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No text to summarize!")
            return

        self.summarize_btn.configure(state="disabled", text="Summarizing...")
        self.status_label.configure(text="Summarizing text...")
        
        # Start background thread
        self.summarization_thread = threading.Thread(target=self.run_summarization, args=(text,))
        self.summarization_thread.start()

    def run_summarization(self, text):
        """Background thread for BART summarization"""
        try:
            from transformers import pipeline
            if self.bart_model == None:
                # Load model naturally (transformers handles downloading/caching)
                model_name = config_manager.get_setting("bart_model_name", "facebook/bart-large-cnn")
                self.bart_model = pipeline("summarization", model=model_name)
            
            # Simple chunking for very long text to avoid index errors
            max_chunk = 3000 # chars ~ 750 tokens
            chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
            
            summaries = []
            for chunk in chunks:
                 if len(chunk) < 50: continue
                 # Use default BART parameters as requested
                 res = self.bart_model(chunk, max_length=130, min_length=30, do_sample=False)
                 summaries.append(res[0]['summary_text'])
            
            full_summary = " ".join(summaries)
            
            # Schedule UI update
            self.after(0, lambda: self.show_summary_popup(text, full_summary))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Summarization Error", str(e)))
        finally:
            self.after(0, lambda: self.summarize_btn.configure(state="normal", text="Summarize 🪄"))
            self.after(0, lambda: self.status_label.configure(text="Ready"))

    def show_summary_popup(self, original_text, summary):
        """Display summary in modal popup"""
        popup = ctk.CTkToplevel(self)
        popup.title("Summary")
        popup.geometry("600x500")
        
        # Setup popup UI
        orig_count = len(original_text.split())
        summ_count = len(summary.split())
        ctk.CTkLabel(popup, text=f"Original: {orig_count} words | Summary: {summ_count} words", font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        txt = ctk.CTkTextbox(popup, font=("Segoe UI", 14), wrap="word")
        txt.pack(fill="both", expand=True, padx=20, pady=10)
        txt.insert("1.0", summary)
        
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(summary)
            messagebox.showinfo("Copied", "Summary copied to clipboard!")
            
        def insert_to_main():
            self.textbox.configure(state="normal")
            self.textbox.insert(ctk.END, f"\n\n[SUMMARY]\n{summary}\n\n", "black")
            self.textbox.configure(state="disabled")
            popup.destroy()

        ctk.CTkButton(btn_frame, text="Copy", command=copy_to_clipboard).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Insert", command=insert_to_main).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Close", command=popup.destroy, fg_color="gray").pack(side="left", padx=10)

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
        self.record_btn.configure(text="Stop Recording", fg_color="#F1AA9B", text_color="#312C51")
        self.status_label.configure(text="Connecting to Mic...")
        self.recording_buffer = [] # Clear buffer for new session
        
        # Clear queues robustly
        for q in [self.vad_queue, self.vosk_queue]:
            while not q.empty():
                try: q.get_nowait()
                except queue.Empty: break
            
        with self.whisper_queue.mutex: self.whisper_queue.queue.clear()
        
        time.sleep(0.1) # Ensure clean state

        # Start Threads
        self.capture_thread = threading.Thread(target=self.audio_capture_loop)
        self.vad_thread = threading.Thread(target=self.vad_processing_loop)
        self.vosk_thread = threading.Thread(target=self.vosk_processing_loop)
        self.whisper_thread = threading.Thread(target=self.whisper_processing_loop)
        
        self.capture_thread.start()
        self.vad_thread.start()
        self.vosk_thread.start()
        self.whisper_thread.start()
        
        self.monitor_queues()

    def monitor_queues(self):
        """Monitors queue sizes and warns if near capacity"""
        if not self.is_recording:
            return

        # Monitor VAD queue (the entry point bottleneck)
        vad_qsize = self.vad_queue.qsize()
        
        # Track last 10 samples
        self.last_queue_sizes.append(vad_qsize)
        if len(self.last_queue_sizes) > 10:
            self.last_queue_sizes.pop(0)
        
        # Warn if queue consistently near capacity
        if vad_qsize > 80: # 80% of 100
            avg_size = sum(self.last_queue_sizes) / len(self.last_queue_sizes)
            if avg_size > 80:
                 self.display_queue.put(("status", f"System Overloaded! Skipping frames... ({vad_qsize}/100)"))
        
        # Schedule next check (1s)
        self.after(1000, self.monitor_queues)

    def stop_recording(self):
        self.is_recording = False
        self.record_btn.configure(text="Start Recording", fg_color="#F0C38E", text_color="#312C51")
        self.level_bar.set(0)
        
        # Export recording to WAV and Text
        if self.recording_buffer:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_filename = f"recording_{timestamp}.wav"
                text_filename = f"transcript_{timestamp}.txt"
                
                # Ensure recordings directory exists
                os.makedirs(self.recordings_dir, exist_ok=True)
                
                # 1. Save Audio
                audio_path = os.path.join(self.recordings_dir, audio_filename)
                with wave.open(audio_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2) # 16-bit
                    wf.setframerate(self.SAMPLE_RATE)
                    wf.writeframes(b"".join(self.recording_buffer))
                
                # 2. Save Text
                text_path = os.path.join(self.recordings_dir, text_filename)
                transcript = self.textbox.get("1.0", ctk.END).strip()
                with open(text_path, "w", encoding="utf-8") as f:
                    f.write(transcript)
                
                self.status_label.configure(text=f"Saved: Audio & Transcript", text_color="#F0C38E")
                print(f"DEBUG: Saved {audio_filename} and {text_filename}")
            except Exception as e:
                print(f"DEBUG: Error saving session: {e}")
                self.status_label.configure(text="Error saving files", text_color="red")
        else:
            self.status_label.configure(text="Stopped (No Audio)")

    def audio_capture_loop(self):
        """Captures raw audio using the new AudioRecorder."""
        def callback(indata):
            frame_bytes = indata.tobytes()
            self.monitor.log('captured')
            q_size = self.vad_queue.qsize()
            
            if q_size > 60:
                drop_prob = 0.3 if q_size < 80 else 0.8
                if random.random() < drop_prob:
                    self.monitor.log('dropped_capture')
                    return

            self.recording_buffer.append(frame_bytes)
            
            if len(frame_bytes) == self.FRAME_BYTES:
                try:
                    self.vad_queue.put_nowait(frame_bytes)
                except queue.Full:
                    pass

            # Update Meter
            audio_data = indata.astype(np.float32).flatten()
            peak = np.max(np.abs(audio_data))
            self.meter_queue.put(float(peak / 20000.0))

        self.display_queue.put(("status", "Mic Connected. Listening..."))
        self.capture_thread = self.recorder.start(self.selected_mic_index, callback)

    def vad_processing_loop(self):
        while self.is_recording or not self.vad_queue.empty():
            try:
                data = self.vad_queue.get(timeout=0.1)
                is_active = self.vad_processor.is_speech(data)
                self.monitor.log('processed_vad')
                self.vosk_queue.put_nowait((data, is_active))
            except queue.Empty:
                continue
            except queue.Full:
                self.monitor.log('dropped_vad')

    def vosk_processing_loop(self):
        try:
            rec = self.engine.get_vosk_recognizer()
            sentence_buffer = collections.deque()
            silence_frames = 0
            is_speech = False
            batch_audio = []
            batch_size_frames = 5
            
            while self.is_recording or not self.vosk_queue.empty():
                try:
                    data, is_active = self.vosk_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                batch_audio.append(data)
                self.monitor.log('processed_vosk')
                
                if len(batch_audio) >= batch_size_frames:
                    joined = b"".join(batch_audio)
                    if rec.AcceptWaveform(joined):
                        result = json.loads(rec.Result())
                        text = result.get("text", "")
                        if text:
                            self.display_queue.put(("draft", text))
                    else:
                        partial = json.loads(rec.PartialResult())
                        p_text = partial.get("partial", "")
                        if p_text:
                            self.display_queue.put(("partial", p_text))
                    batch_audio = []

                # Whisper Buffering logic
                MIN_SILENCE_FRAMES = 25
                if is_active:
                    if not is_speech:
                        is_speech = True
                        silence_frames = 0
                        while len(sentence_buffer) > 3:
                            sentence_buffer.popleft()
                    silence_frames = 0
                    sentence_buffer.append(data)
                else:
                    if is_speech:
                        silence_frames += 1
                        sentence_buffer.append(data)
                        if silence_frames > MIN_SILENCE_FRAMES:
                            full_audio = b"".join(sentence_buffer)
                            if len(full_audio) > self.SAMPLE_RATE * 0.5 * 2:
                                self.whisper_queue.put_nowait(full_audio)
                                self.display_queue.put(("status", "Improving accuracy..."))
                            sentence_buffer.clear()
                            is_speech = False
                    else:
                        sentence_buffer.append(data)
                        while len(sentence_buffer) > 10:
                            sentence_buffer.popleft()
        except Exception as e:
            self.display_queue.put(("error", f"Vosk Error: {e}"))

    def whisper_processing_loop(self):
        while self.is_recording or not self.whisper_queue.empty():
            try:
                audio_bytes = self.whisper_queue.get(timeout=1)
                text = self.engine.transcribe_whisper(audio_bytes, self.WHISPER_MODEL_SIZE)
                if text:
                    self.display_queue.put(("final", text))
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Whisper Error: {e}")

    def update_ui_loop(self):
        try:
            # 1. Handle Display Updates
            while not self.display_queue.empty():
                try:
                    msg_type, content = self.display_queue.get_nowait()
                    
                    if msg_type == "status":
                        self.status_label.configure(text=content)
                    elif msg_type == "error":
                        messagebox.showerror("Error", content)
                    elif msg_type == "partial":
                        pass 
                    elif msg_type == "draft":
                        self.insert_text(f"[Draft] {content}\n", "gray")
                    elif msg_type == "final":
                        self.replace_last_draft_with_final(content)
                except queue.Empty:
                    break
                except Exception as e:
                    print(f"DEBUG: UI Update Error (msg={msg_type}): {e}")

            # 2. Handle Meter
            try:
                if not self.meter_queue.empty():
                    level = self.meter_queue.get_nowait()
                    level = max(0.0, min(1.0, float(level)))
                    self.level_bar.set(level)
            except Exception as e:
                # print(f"DEBUG: Meter UI Error: {e}")
                pass
            
            # 3. Debug Stats
            if self.is_recording and random.random() < 0.05:
                 print(f"FPS: Cap={self.monitor.get_fps('captured')} VAD={self.monitor.get_fps('processed_vad')} Vosk={self.monitor.get_fps('processed_vosk')}")

        except Exception as e:
            print(f"DEBUG: Global UI Loop Error: {e}")
        
        # Always reschedule to prevent hang
        interval = 50 if self.is_recording else 200
        self.after(interval, self.update_ui_loop)

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
    # Create a dummy root for standalone execution
    root = ctk.CTk()
    root.withdraw() # Hide the root window used for the mainloop
    
    app = HybridTranscriberApp(root)
    
    # Ensure closing the app closes the script
    def on_close():
        app.destroy()
        root.destroy()
        os._exit(0) # Force exit threads
        
    app.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()