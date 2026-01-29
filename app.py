import customtkinter as ctk
import speech_recognition as sr
import threading
import queue
import time
from datetime import datetime
from tkinter import filedialog, messagebox

class VoiceTranscriberApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("Real-Time Voice Transcriber")
        
        self.geometry("800x600")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- State Variables ---
        self.is_recording = False
        self.recording_thread = None
        self.transcription_queue = queue.Queue()
        self.start_time = 0
        self.selected_language = "en-US"

        # --- UI Components ---
        self.create_widgets()

        # --- Main Loop ---
        self.update_transcription_display()

    def create_widgets(self):
        # --- Configure Grid Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Top Frame for Controls ---
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        top_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # --- Start/Stop Button ---
        self.record_button = ctk.CTkButton(
            top_frame,
            text="Start Recording",
            command=self.toggle_recording,
            width=140
        )
        self.record_button.grid(row=0, column=0, padx=5)

        # --- Clear Button ---
        self.clear_button = ctk.CTkButton(
            top_frame,
            text="Clear",
            command=self.clear_text,
            width=100
        )
        self.clear_button.grid(row=0, column=1, padx=5)

        # --- Save Button ---
        self.save_button = ctk.CTkButton(
            top_frame,
            text="Save to .txt",
            command=self.save_text,
            width=120
        )
        self.save_button.grid(row=0, column=2, padx=5)
        
        # --- Copy Button ---
        self.copy_button = ctk.CTkButton(
            top_frame, text="Copy to Clipboard", command=self.copy_to_clipboard
        )
        self.copy_button.grid(row=0, column=3, padx=5)


        # --- Transcription Display Area ---
        self.text_display = ctk.CTkTextbox(
            self,
            font=("Helvetica", 14),
            wrap="word"
        )
        self.text_display.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.text_display.configure(state="disabled")

        # --- Bottom Frame ---
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
        bottom_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)


        # --- Language Selection ---
        language_label = ctk.CTkLabel(bottom_frame, text="Language:")
        language_label.grid(row=0, column=0, padx=(10, 0), sticky="w")
        
        languages = {
            "English": "en-US",
            "Spanish": "es-ES",
            "French": "fr-FR",
            "German": "de-DE",
            "Italian": "it-IT",
            "Portuguese": "pt-PT",
            "Russian": "ru-RU",
            "Japanese": "ja-JP",
            "Chinese (Mandarin)": "zh-CN",
        }
        self.language_menu = ctk.CTkOptionMenu(
            bottom_frame,
            values=list(languages.keys()),
            command=lambda choice: self.set_language(languages[choice])
        )
        self.language_menu.set("English")
        self.language_menu.grid(row=0, column=1, padx=5, sticky="w")

        # --- Status Bar ---
        self.status_label = ctk.CTkLabel(bottom_frame, text="Status: Stopped", anchor="e")
        self.status_label.grid(row=0, column=3, padx=10, sticky="e")
        
        # --- Word Count & Timer ---
        self.info_label = ctk.CTkLabel(bottom_frame, text="Words: 0 | Duration: 00:00:00", anchor="center")
        self.info_label.grid(row=0, column=2, padx=10, sticky="ew")


    def set_language(self, lang_code):
        self.selected_language = lang_code
        print(f"Language set to: {self.selected_language}")

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_button.configure(text="Stop Recording", fg_color="red")
        self.status_label.configure(text="Status: Listening...")
        self.start_time = time.time()
        self.update_timer()

        self.recording_thread = threading.Thread(target=self.listen_in_background)
        self.recording_thread.daemon = True
        self.recording_thread.start()

    def stop_recording(self):
        self.is_recording = False
        if self.recording_thread:
            # The thread will stop on its own when is_recording is False
            self.recording_thread.join(timeout=1)
        self.record_button.configure(text="Start Recording", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        self.status_label.configure(text="Status: Stopped")

    def listen_in_background(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)

        while self.is_recording:
            try:
                with microphone as source:
                    # self.status_label.configure(text="Status: Listening...")
                    audio = recognizer.listen(source, phrase_time_limit=5)
                
                # self.status_label.configure(text="Status: Processing...")
                text = recognizer.recognize_google(audio, language=self.selected_language)
                
                if text:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    self.transcription_queue.put(f"[{timestamp}] {text}\n")
            except sr.UnknownValueError:
                # Speech was unintelligible
                self.transcription_queue.put("[...] ")
            except sr.RequestError as e:
                # API was unreachable or unresponsive
                self.transcription_queue.put(f"[API Error: {e}]\n")
            except Exception as e:
                self.transcription_queue.put(f"[Error: {e}]\n")
                self.stop_recording() # Stop on major error
                messagebox.showerror("Microphone Error", f"An error occurred with the microphone: {e}")
                break
        print("Listening thread stopped.")


    def update_transcription_display(self):
        while not self.transcription_queue.empty():
            transcription = self.transcription_queue.get()
            self.text_display.configure(state="normal")
            self.text_display.insert(ctk.END, transcription)
            self.text_display.see(ctk.END) # Auto-scroll
            self.text_display.configure(state="disabled")
            self.update_word_count()
        self.after(100, self.update_transcription_display)

    def update_timer(self):
        if self.is_recording:
            elapsed_time = time.time() - self.start_time
            hours, rem = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(rem, 60)
            timer_str = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            
            # Update info label with timer
            current_text = self.info_label.cget("text")
            word_count_part = current_text.split(" | ")[0]
            self.info_label.configure(text=f"{word_count_part} | Duration: {timer_str}")

            self.after(1000, self.update_timer)

    def update_word_count(self):
        content = self.text_display.get("1.0", ctk.END)
        word_count = len(content.split())
        
        # Update info label with word count
        current_text = self.info_label.cget("text")
        duration_part = current_text.split(" | ")[1]
        self.info_label.configure(text=f"Words: {word_count} | {duration_part}")

    def clear_text(self):
        self.text_display.configure(state="normal")
        self.text_display.delete("1.0", ctk.END)
        self.text_display.configure(state="disabled")
        self.info_label.configure(text="Words: 0 | Duration: 00:00:00")

    def save_text(self):
        content = self.text_display.get("1.0", ctk.END)
        if not content.strip():
            messagebox.showwarning("Empty Content", "There is no text to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Transcription"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                messagebox.showinfo("Success", f"Transcription saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save file: {e}")

    def copy_to_clipboard(self):
        content = self.text_display.get("1.0", ctk.END)
        if not content.strip():
            messagebox.showwarning("Empty Content", "There is no text to copy.")
            return
        self.clipboard_clear()
        self.clipboard_append(content)
        messagebox.showinfo("Copied", "Transcription copied to clipboard.")


if __name__ == "__main__":
    try:
        app = VoiceTranscriberApp()
        app.mainloop()
    except ImportError as e:
        messagebox.showerror(
            "Dependency Error", 
            f"A required library is missing: {e.name}.\n\nPlease install it by running:\npip install {e.name}"
        )
    except Exception as e:
        # A bit of a catch-all for other startup issues, like no microphone.
        if "no default input device available" in str(e).lower():
            messagebox.showerror(
                "Microphone Error",
                "No microphone found. Please connect a microphone and restart the application."
            )
        else:
            messagebox.showerror("Application Error", f"An unexpected error occurred: {e}")
