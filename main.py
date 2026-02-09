import customtkinter as ctk
import os
import sys
from PIL import Image
import config_manager
import queue 
import threading
import time

# --- Import Modules ---
try:
    from app import HybridTranscriberApp
except ImportError as e:
    print(f"Error importing app: {e}")
    HybridTranscriberApp = None

try:
    from study_gui import StudyAssistantGUI
except ImportError as e:
    print(f"Error importing study gui: {e}")
    StudyAssistantGUI = None

# Check if critical modules failed to import
if HybridTranscriberApp is None or StudyAssistantGUI is None:
    print("\n⚠️  MISSING DEPENDENCIES DETECTED")
    print("Please ensure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    print("\nTo verify installation, run:")
    print("  python -c \"import torch; import whisper; import vosk; import pptx; print('✅ All dependencies installed!')\"")
    print()

class MainMenuApp(ctk.CTk): 
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
        
        # Start download in background
        self.start_model_download()

    def init_loading_ui(self):
        """Initializes the loading screen widgets."""
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
        """Starts the background thread for downloading models."""
        def download_thread_target():
            # Pass our queue-based callback to the config manager logic
            success = config_manager.download_models(progress_callback=self.queue_gui_update)
            # Signal completion via queue
            self.queue_gui_update("DONE", 1.0 if success else -1.0)

        threading.Thread(target=download_thread_target, daemon=True).start()
        # Start polling the queue
        self.check_download_queue()

    def queue_gui_update(self, message, percentage):
        """Callback for the download thread to enqueue updates."""
        self.gui_update_queue.put((message, percentage))

    def check_download_queue(self):
        """Polls the queue for updates on the main thread."""
        try:
            while True:
                message, percentage = self.gui_update_queue.get_nowait()
                
                if message == "DONE":
                    if percentage >= 0:
                        self.transition_to_main_menu()
                    else:
                        self.loading_label.configure(text="Model download failed. Check console.", text_color="#F63049")
                    return # Stop polling if done

                # Update UI
                self.loading_label.configure(text=message)
                self.loading_progress.set(percentage)
                
        except queue.Empty:
            pass
        
        # Schedule next check
        self.after(50, self.check_download_queue)

    def transition_to_main_menu(self):
        """Destroys loading UI and builds the main menu."""
        self.loading_frame.destroy()
        self.init_main_ui()

    def init_main_ui(self):
        """Initializes the main menu UI (Background, Buttons, etc.)."""
        # No background image, use solid color
        self.main_bg = ctk.CTkFrame(self, fg_color="#312C51")
        self.main_bg.place(x=0, y=0, relwidth=1, relheight=1)

        # --- 2. HEADER ---
        self.title_label = ctk.CTkLabel(
            self.main_bg, 
            text="⚡ NOTEFORGE", 
            font=("Segoe UI", 42, "bold"),
            text_color="#F1AA9B",
            fg_color="transparent"
        )
        self.title_label.place(relx=0.5, rely=0.2, anchor="center")

        self.subtitle_label = ctk.CTkLabel(
            self.main_bg,
            text="Real-Time Transcription & Intelligent Note Summarization",
            font=("Segoe UI", 16),
            text_color="gray",
            fg_color="transparent"
        )
        self.subtitle_label.place(relx=0.5, rely=0.28, anchor="center")

        # --- 3. BUTTONS AREA ---
        btn_width = 340
        btn_height = 55
        btn_font = ("Segoe UI", 16, "bold")
        btn_corner_radius = 20

        # Elevated Card for Buttons
        self.button_frame = ctk.CTkFrame(
            self.main_bg, 
            fg_color="#48426D", 
            corner_radius=30,
            border_width=2,
            border_color="#312C51"
        )
        self.button_frame.place(relx=0.5, rely=0.6, anchor="center")
        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_rowconfigure((0, 1, 2, 3), weight=0)
        # Extra padding inside the card
        container_pady = 25
        container_padx = 30

        # 1. Transcription
        self.btn_transcriber = ctk.CTkButton(
            self.button_frame,
            text="   🎤   Real-Time Transcription   ",
            font=btn_font,
            width=btn_width,
            height=btn_height,
            fg_color="#F0C38E",
            hover_color="#DEB17E",
            text_color="#312C51",
            border_width=2, 
            border_color="#48426D",
            corner_radius=btn_corner_radius,
            command=self.open_voice_transcriber
        )
        self.btn_transcriber.grid(row=0, column=0, pady=(container_pady, 10), padx=container_padx)

        # 2. Summarization
        self.btn_study = ctk.CTkButton(
            self.button_frame,
            text="   📝   Note Summarization   ",
            font=btn_font,
            width=btn_width,
            height=btn_height,
            fg_color="#F1AA9B",
            hover_color="#DD998A",
            text_color="#312C51",
            command=self.open_study_assistant,
            border_width=2, 
            border_color="#48426D",
            corner_radius=btn_corner_radius
        )
        self.btn_study.grid(row=1, column=0, pady=10, padx=container_padx)

        # 3. Settings
        self.btn_settings = ctk.CTkButton(
            self.button_frame,
            text="   ⚙️   Settings   ",
            font=btn_font,
            width=btn_width,
            height=btn_height,
            fg_color="transparent",
            border_width=2,
            border_color="#48426D",
            text_color="#F0C38E",
            corner_radius=btn_corner_radius,
            command=self.open_settings
        )
        self.btn_settings.grid(row=2, column=0, pady=10, padx=container_padx)

        # 4. Exit
        self.btn_exit = ctk.CTkButton(
            self.button_frame,
            text="   ❌   Exit   ",
            font=btn_font,
            width=btn_width,
            height=btn_height,
            fg_color="#48426D",
            hover_color="#5A547F",
            command=self.exit_app,
            border_width=2, 
            border_color="#F1AA9B",
            corner_radius=btn_corner_radius
        )
        self.btn_exit.grid(row=3, column=0, pady=(10, container_pady), padx=container_padx)

        # --- 4. FOOTER ---
        self.footer_label = ctk.CTkLabel(
            self.main_bg,
            text="v2.1 AI Edition | Powered by Vosk, Whisper & Spacy",
            font=("Segoe UI", 12),
            text_color="gray",
            fg_color="transparent"
        )
        self.footer_label.place(relx=0.5, rely=0.95, anchor="center")

    # --- FUNCTIONALITY ---
    def open_voice_transcriber(self):
        if HybridTranscriberApp is None:
            print("App module not found")
            return
        self.withdraw()
        self.current_child = HybridTranscriberApp(self)
        self._setup_child_window(self.current_child)

    def open_study_assistant(self):
        if StudyAssistantGUI is None:
            print("Study GUI module not found")
            return
        self.withdraw()
        self.current_child = StudyAssistantGUI(self)
        self._setup_child_window(self.current_child)

    def _setup_child_window(self, child_window):
        def on_child_close():
            child_window.destroy()
            self.current_child = None
            self.deiconify()
            
        child_window.protocol("WM_DELETE_WINDOW", on_child_close)
        child_window.focus()

    def open_settings(self):
        settings_toplevel = ctk.CTkToplevel(self)
        settings_toplevel.geometry("400x350")
        settings_toplevel.title("Settings")
        settings_toplevel.focus()
        settings_toplevel.attributes("-topmost", True)
        
        settings_toplevel.grid_columnconfigure(0, weight=1)
        settings_toplevel.grid_columnconfigure(1, weight=1)
        settings_toplevel.grid_rowconfigure((0, 1, 2, 3), weight=0)
        settings_toplevel.grid_rowconfigure(4, weight=1)

        # Whisper Model Size
        ctk.CTkLabel(settings_toplevel, text="Whisper Model Size:", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        whisper_model_sizes = ["tiny", "base", "small", "medium", "large"]
        current_whisper_size = config_manager.get_setting("whisper_model_size")
        
        self.whisper_size_optionmenu = ctk.CTkOptionMenu(
            settings_toplevel, 
            values=whisper_model_sizes, 
            command=self._on_whisper_size_change,
            font=("Segoe UI", 14)
        )
        self.whisper_size_optionmenu.set(current_whisper_size)
        self.whisper_size_optionmenu.grid(row=0, column=1, padx=20, pady=(20, 5), sticky="ew")

        # Separator
        ctk.CTkFrame(settings_toplevel, height=2, fg_color="gray", corner_radius=0).grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 10), sticky="ew")

        # Reinstall Models
        ctk.CTkLabel(settings_toplevel, text="Model Management:", font=("Segoe UI", 14, "bold")).grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        self.reinstall_models_button = ctk.CTkButton(
            settings_toplevel, 
            text="Reinstall Models", 
            command=self._reinstall_models_action,
            font=("Segoe UI", 14),
            fg_color="#F63049",
            hover_color="#D02752"
        )
        self.reinstall_models_button.grid(row=2, column=1, padx=20, pady=(10, 5), sticky="ew")

        # Clear All Models
        self.clear_all_models_button = ctk.CTkButton(
            settings_toplevel,
            text="Clear All Models",
            command=self._clear_all_models_action,
            font=("Segoe UI", 14),
            fg_color="#CC0000",
            hover_color="#FF0000"
        )
        self.clear_all_models_button.grid(row=3, column=1, padx=20, pady=(5, 10), sticky="ew")

        # Status Label
        self.settings_status_label = ctk.CTkLabel(settings_toplevel, text="", text_color="green", wraplength=350, justify="left")
        self.settings_status_label.grid(row=4, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

    def _on_whisper_size_change(self, new_size):
        config_manager.set_setting("whisper_model_size", new_size)
        if hasattr(self, 'settings_status_label'):
            self.settings_status_label.configure(text=f"Whisper model set to '{new_size}'. Restart app to apply.", text_color="orange")

    def _reinstall_models_action(self):
        self.reinstall_models_button.configure(state="disabled", text="Deleting...")
        if hasattr(self, 'settings_status_label'):
            self.settings_status_label.configure(text="Deleting models...", text_color="orange")
        
        def reinstall_thread():
            result_delete = config_manager.delete_models()
            if result_delete:
                self._update_settings_status("Models deleted. Re-downloading...", "orange")
                result_download = config_manager.download_models(progress_callback=self._update_settings_download_progress)
                if result_download:
                    self._update_settings_status("Models reinstalled successfully. Restart app to apply.", "green")
                else:
                    self._update_settings_status("Error re-downloading models. Check console.", "red")
            else:
                self._update_settings_status("Error deleting models. Check console.", "red")
            
            self.reinstall_button_reset()

        threading.Thread(target=reinstall_thread).start()

    def _update_settings_status(self, text, color):
        # Helper to update label safely from thread (CTkiner is mostly thread-safe for configure but better to be safe)
        # For simplicity in this method, we rely on CTk's handling or use after if needed. 
        # But to be robust like the main loader:
        self.after(0, lambda: self.settings_status_label.configure(text=text, text_color=color) if hasattr(self, 'settings_status_label') else None)

    def reinstall_button_reset(self):
        self.after(0, lambda: self.reinstall_models_button.configure(state="normal", text="Reinstall Models"))

    def _update_settings_download_progress(self, message, percentage):
        self._update_settings_status(message, "orange")

    def _clear_all_models_action(self):
        self.clear_all_models_button.configure(state="disabled", text="Clearing...")
        if hasattr(self, 'settings_status_label'):
            self.settings_status_label.configure(text="Deleting all models...", text_color="orange")

        def clear_thread():
            success = config_manager.clear_all_models()
            if success:
                self._update_settings_status("All models cleared. Restart app to re-download.", "green")
            else:
                self._update_settings_status("Error clearing models. Check console.", "red")
            
            self.after(0, lambda: self.clear_all_models_button.configure(state="normal", text="Clear All Models"))
        
        threading.Thread(target=clear_thread).start()

    def exit_app(self):
        self.quit()
        sys.exit()

if __name__ == "__main__":
    app = MainMenuApp()
    app.mainloop()