import customtkinter as ctk
import os
import sys
import platform
import queue 
import threading
import time
from .config import settings
from .models.manager import ModelManager

# --- Lazy Imports for Sub-apps ---
def get_transcriber_app():
    from app import HybridTranscriberApp
    return HybridTranscriberApp

def get_study_gui():
    from study_gui import StudyAssistantGUI
    return StudyAssistantGUI

class NoteForgeLauncher(ctk.CTk): 
    """Main entrypoint UI for NoteForge."""
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("NoteForge")
        self.geometry("800x600")
        self.resizable(False, False)
        self.configure(fg_color="#312C51")
        
        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        self.geometry(f"800x600+{x}+{y}")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue") 
        
        self.current_child = None
        self.gui_update_queue = queue.Queue()

        # Start cleanly with the Loading UI
        self.init_loading_ui()
        self.start_model_download()
    
    def init_loading_ui(self):
        self.loading_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.loading_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.loading_label = ctk.CTkLabel(
            self.loading_frame, 
            text="Checking models...", 
            font=("Segoe UI", 20, "bold"),
            text_color="#F0C38E"
        )
        self.loading_label.pack(pady=(0, 20))

        self.loading_progress = ctk.CTkProgressBar(self.loading_frame, width=400)
        self.loading_progress.set(0)
        self.loading_progress.pack()

    def start_model_download(self):
        def download_thread_target():
            # Use the new ModelManager for centralized checks
            try:
                # Check/Download Vosk
                self.queue_gui_update("Ensuring Vosk model...", 0.2)
                ModelManager.get_vosk_model()
                
                # Check/Download Whisper
                size = settings.get("whisper_model_size", "base")
                self.queue_gui_update(f"Ensuring Whisper {size} model...", 0.5)
                ModelManager.get_whisper_model(size)
                
                # Check/Download BART
                self.queue_gui_update("Ensuring BART model...", 0.8)
                ModelManager.get_bart_pipeline()
                
                self.queue_gui_update("DONE", 1.0)
            except Exception as e:
                print(f"Model initialization error: {e}")
                self.queue_gui_update("DONE", -1.0)

        threading.Thread(target=download_thread_target, daemon=True).start()
        self.check_download_queue()

    def queue_gui_update(self, message, percentage):
        self.gui_update_queue.put((message, percentage))

    def check_download_queue(self):
        try:
            while True:
                message, percentage = self.gui_update_queue.get_nowait()
                if message == "DONE":
                    if percentage >= 0:
                        self.transition_to_main_menu()
                    else:
                        self.loading_label.configure(text="Initialization failed. Check logs.", text_color="#F63049")
                    return
                self.loading_label.configure(text=message)
                self.loading_progress.set(percentage)
        except queue.Empty:
            pass
        self.after(50, self.check_download_queue)

    def transition_to_main_menu(self):
        self.loading_frame.destroy()
        self.init_main_ui()

    def init_main_ui(self):
        self.main_bg = ctk.CTkFrame(self, fg_color="#312C51")
        self.main_bg.place(x=0, y=0, relwidth=1, relheight=1)

        self.title_label = ctk.CTkLabel(
            self.main_bg, 
            text="⚡ NOTEFORGE", 
            font=("Segoe UI", 42, "bold"),
            text_color="#F1AA9B"
        )
        self.title_label.place(relx=0.5, rely=0.2, anchor="center")

        btn_frame = ctk.CTkFrame(self.main_bg, fg_color="#48426D", corner_radius=30)
        btn_frame.place(relx=0.5, rely=0.6, anchor="center")
        
        # Buttons
        ctk.CTkButton(btn_frame, text="🎤 Transcription", command=self.open_transcriber, width=300, height=50).pack(pady=10, padx=20)
        ctk.CTkButton(btn_frame, text="📝 Study Assistant", command=self.open_study, width=300, height=50).pack(pady=10, padx=20)
        ctk.CTkButton(btn_frame, text="❌ Exit", command=self.destroy, width=300, height=50, fg_color="gray").pack(pady=10, padx=20)

        ctk.CTkLabel(self.main_bg, text="v3.0 Modular Alpha", text_color="gray").place(relx=0.5, rely=0.95, anchor="center")

    def open_transcriber(self):
        app_cls = get_transcriber_app()
        if app_cls:
            self.withdraw()
            child = app_cls(self)
            self._setup_child(child)

    def open_study(self):
        app_cls = get_study_gui()
        if app_cls:
            self.withdraw()
            child = app_cls(self)
            self._setup_child(child)

    def _setup_child(self, child):
        child.protocol("WM_DELETE_WINDOW", lambda: [child.destroy(), self.deiconify()])

def main():
    app = NoteForgeLauncher()
    app.mainloop()
