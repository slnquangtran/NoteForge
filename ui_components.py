import customtkinter as ctk
import tkinter as tk
from datetime import datetime
import threading
import time

class AudioLevelMeter(ctk.CTkProgressBar):
    """
    Visual audio level meter with smooth decay.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.set(0)
        self.target_level = 0.0
        self.current_level = 0.0
        self.decay_factor = 0.2
        self.smoothing_factor = 0.5
        
        self.running = True
        self.animate()

    def update_level(self, level):
        """Update the target level (0.0 to 1.0)"""
        self.target_level = max(0.0, min(1.0, level))

    def animate(self):
        if not self.running: return

        # Smooth interpolation
        diff = self.target_level - self.current_level
        if diff > 0:
            self.current_level += diff * self.smoothing_factor # Fast attack
        else:
            self.current_level += diff * self.decay_factor   # Slow decay
            
        self.set(self.current_level)
        self.after(20, self.animate) # 50 FPS

    def destroy(self):
        self.running = False
        super().destroy()

class TranscriptionBox(ctk.CTkTextbox):
    """
    Enhanced Texbox for displaying Draft (Gray) vs Final (White) text.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(state="disabled")
        
        # Tags for styling
        self.tag_config("draft", foreground="gray")
        self.tag_config("final", foreground="white") # Or theme text color
        self.tag_config("timestamp", foreground="#2CC985") # Greenish

        self.last_draft_start = None

    def add_final(self, text):
        self.configure(state="normal")
        
        # Remove previous draft if any
        if self.last_draft_start:
            self.delete(self.last_draft_start, "end")
            self.last_draft_start = None

        timestamp = datetime.now().strftime("[%H:%M:%S] ")
        self.insert("end", timestamp, "timestamp")
        self.insert("end", text + "\n", "final")
        
        self.see("end")
        self.configure(state="disabled")

    def update_draft(self, text):
        self.configure(state="normal")
        
        if self.last_draft_start:
             self.delete(self.last_draft_start, "end")
        else:
             self.last_draft_start = self.index("end-1c") # Mark start of draft area
             # Check if we are at start of line? simpler to just append.
             self.insert("end", "\n") # New line for draft
             self.last_draft_start = self.index("end-1c")

        self.insert(self.last_draft_start, f"[Draft] {text}", "draft")
        self.see("end")
        self.configure(state="disabled")

    def get_full_text(self):
        return self.get("1.0", "end")
    
    def clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.last_draft_start = None
        self.configure(state="disabled")

class SummaryPanel(ctk.CTkFrame):
    """
    Collapsible panel for displaying summaries.
    """
    def __init__(self, master, on_summarize=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_summarize = on_summarize
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        self.title_lbl = ctk.CTkLabel(self.header_frame, text="AI Summary", font=("Segoe UI", 16, "bold"))
        self.title_lbl.pack(side="left")
        
        self.summ_btn = ctk.CTkButton(self.header_frame, text="Generate Summary", command=self._trigger_summary, width=150)
        self.summ_btn.pack(side="right")

        # Content
        self.text_area = ctk.CTkTextbox(self, height=150, font=("Segoe UI", 14))
        self.text_area.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.text_area.configure(state="disabled")
        
    def _trigger_summary(self):
        if self.on_summarize:
            self.summ_btn.configure(state="disabled", text="Thinking...")
            self.on_summarize()
            
    def display_summary(self, text):
        self.text_area.configure(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", text)
        self.text_area.configure(state="disabled")
        self.summ_btn.configure(state="normal", text="Regenerate Summary")

    def show_error(self, err):
        self.display_summary(f"Error: {err}")
        self.summ_btn.configure(state="normal", text="Retry")
    
    def set_loading(self):
        self.summ_btn.configure(state="disabled", text="Processing...")

class ControlPanel(ctk.CTkFrame):
    """
    Main controls: Record, Mic, Config.
    """
    def __init__(self, master, on_record_toggle=None, on_mic_change=None, devices=[], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_record_toggle = on_record_toggle
        self.on_mic_change = on_mic_change
        
        # Record Button
        self.record_btn = ctk.CTkButton(self, text="Start Recording", command=self._toggle, 
                                        font=("Segoe UI", 16, "bold"), height=40, fg_color="#2CC985", hover_color="#36D491")
        self.record_btn.pack(side="left", padx=(0, 20))
        
        # Mic Selector
        self.mic_var = ctk.StringVar(value=devices[0] if devices else "Default")
        self.mic_menu = ctk.CTkOptionMenu(self, values=devices, command=self._mic_changed, variable=self.mic_var, width=250)
        self.mic_menu.pack(side="right")
        
        ctk.CTkLabel(self, text="Microphone:").pack(side="right", padx=10)
        
    def _toggle(self):
        if self.on_record_toggle:
            is_recording = self.on_record_toggle() # User func returns new state
            self.update_state(is_recording)

    def _mic_changed(self, choice):
        if self.on_mic_change:
            self.on_mic_change(choice)

    def update_state(self, is_recording):
        if is_recording:
            self.record_btn.configure(text="Stop Recording", fg_color="#FF5252", hover_color="#FF867F")
        else:
            self.record_btn.configure(text="Start Recording", fg_color="#2CC985", hover_color="#36D491")
