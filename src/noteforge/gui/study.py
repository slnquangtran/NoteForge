import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os

from ..study.generator import StudyGenerator
from ..study.exporter import export_to_pdf

class StudyAssistantGUI(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        
        self.title("NoteForge - Note Summarization")
        self.configure(fg_color="#312C51")
        self.center_window()
        
        self.generator = StudyGenerator()
        self.processed_data = None
        
        self.status_var = ctk.StringVar(value="Ready. Load a file to generate notes.")
        self.create_widgets()

    def center_window(self):
        self.update_idletasks()
        width, height = 1000, 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(3, weight=1)

        # Header
        header_card = ctk.CTkFrame(self, fg_color="#48426D", corner_radius=25)
        header_card.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        ctk.CTkLabel(header_card, text="📝 AI Study Assistant", font=("Segoe UI", 20, "bold")).pack(side="left", padx=20, pady=15)
        ctk.CTkButton(header_card, text="📂 Load File", command=self.load_file).pack(side="right", padx=20, pady=15)

        # Main Textbox
        self.notes_box = ctk.CTkTextbox(self, font=("Segoe UI", 14), wrap="word", corner_radius=20, border_width=2, border_color="#312C51")
        self.notes_box.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

        # Thoughts Box
        thoughts_card = ctk.CTkFrame(self, fg_color="#48426D", corner_radius=25)
        thoughts_card.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="nsew")
        ctk.CTkLabel(thoughts_card, text="🧠 AI Thought Process", font=("Segoe UI", 12, "italic"), text_color="#F0C38E").pack(padx=20, anchor="w")
        self.thoughts_box = ctk.CTkTextbox(thoughts_card, height=120, font=("Segoe UI", 12), wrap="word", corner_radius=15)
        self.thoughts_box.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        # Footer
        footer_card = ctk.CTkFrame(self, fg_color="#48426D", corner_radius=25)
        footer_card.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.progress_bar = ctk.CTkProgressBar(footer_card, width=200)
        self.progress_bar.pack(side="left", padx=20)
        self.progress_bar.set(0)
        ctk.CTkLabel(footer_card, textvariable=self.status_var).pack(side="left", padx=10)
        
        self.btn_process = ctk.CTkButton(footer_card, text="📝 Generate Notes", command=self.start_processing)
        self.btn_process.pack(side="right", padx=20)
        self.btn_export = ctk.CTkButton(footer_card, text="💾 Export PDF", command=self.export_pdf, state="disabled")
        self.btn_export.pack(side="right", padx=10)

        self.loaded_filepath = None

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("PowerPoint", "*.pptx")])
        if path:
            self.loaded_filepath = path
            self.status_var.set(f"Loaded: {os.path.basename(path)}")

    def start_processing(self):
        if not self.loaded_filepath: return
        self.btn_process.configure(state="disabled")
        self.thoughts_box.delete("1.0", "end")
        threading.Thread(target=self.run_pipeline, daemon=True).start()

    def run_pipeline(self):
        def update(msg, prog):
            self.after(0, lambda: self.status_var.set(msg))
            self.after(0, lambda: self.progress_bar.set(prog))
            if msg.startswith("AI Thought:"):
                self.after(0, lambda: self.add_thought(msg))

        try:
            results = self.generator.process_file(self.loaded_filepath, progress_callback=update)
            self.processed_data = results
            self.after(0, self.display_results)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, lambda: self.btn_process.configure(state="normal"))

    def add_thought(self, msg):
        self.thoughts_box.insert("end", f"→ {msg.replace('AI Thought: ', '')}\n")
        self.thoughts_box.see("end")

    def display_results(self):
        if "error" in self.processed_data:
            messagebox.showerror("Error", self.processed_data["error"])
            return
        self.notes_box.delete("1.0", "end")
        self.notes_box.insert("1.0", self.processed_data.get("notes", ""))
        self.btn_export.configure(state="normal")
        self.status_var.set("Done!")

    def export_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if path:
            export_to_pdf(self.processed_data.get("notes", ""), path)
            messagebox.showinfo("Export", "Saved!")
