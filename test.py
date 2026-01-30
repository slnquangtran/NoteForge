import customtkinter as ctk
import os
import sys
from PIL import Image

# Giữ nguyên phần Import apps của bạn
try:
    from app import HybridTranscriberApp
except: HybridTranscriberApp = None

class MainMenuApp(ctk.CTk): 
    def __init__(self):
        super().__init__()

        self.title("NoteForge")
        self.geometry("800x600")
        self.resizable(False, False) # Cố định kích thước để place chính xác
        ctk.set_appearance_mode("dark")
        
        # Căn giữa cửa sổ
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        self.geometry(f"800x600+{x}+{y}")

        # --- 1. SETUP BACKGROUND (THÙNG CHỨA CHÍNH) ---
        bg_path = "bg.jpg" # Đảm bảo file ảnh image_8d8a74.png của bạn đổi tên thành bg.jpg
        img = Image.open(bg_path)
        self.bg_image = ctk.CTkImage(light_image=img, dark_image=img, size=(800, 600))
        
        # Đây là Master duy nhất. Mọi thứ khác phải gắn vào đây.
        self.main_bg = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.main_bg.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_widgets()

    def create_widgets(self):
        # --- 2. TIÊU ĐỀ (Gắn trực tiếp vào main_bg) ---
        self.title_label = ctk.CTkLabel(
            self.main_bg, 
            text="⚡ NOTEFORGE", 
            font=("Segoe UI", 45, "bold"),
            text_color="#3B8ED0",
            fg_color="transparent" # Bây giờ lệnh này mới có tác dụng thực sự
        )
        self.title_label.place(relx=0.5, rely=0.2, anchor="center")

        self.subtitle_label = ctk.CTkLabel(
            self.main_bg,
            text="Real-Time Transcription & Intelligent Note Summarization",
            font=("Segoe UI", 16),
            text_color="#AAAAAA",
            fg_color="transparent"
        )
        self.subtitle_label.place(relx=0.5, rely=0.28, anchor="center")

        # --- 3. CÁC NÚT BẤM (Gắn trực tiếp vào main_bg bằng Place) ---
        btn_width = 320
        btn_height = 50
        btn_font = ("Segoe UI", 16)

        # Nút 1: Real-Time
        self.btn_trans = ctk.CTkButton(
            self.main_bg, text="🎤  Real-Time Transcription",
            width=btn_width, height=btn_height, font=btn_font,
            command=self.open_voice_transcriber
        )
        self.btn_trans.place(relx=0.5, rely=0.45, anchor="center")

        # Nút 2: Summarization
        self.btn_study = ctk.CTkButton(
            self.main_bg, text="📝  Note Summarization",
            width=btn_width, height=btn_height, font=btn_font,
            fg_color="#8E44AD", hover_color="#9B59B6"
        )
        self.btn_study.place(relx=0.5, rely=0.55, anchor="center")

        # Nút 3: Settings
        self.btn_settings = ctk.CTkButton(
            self.main_bg, text="⚙️  Settings",
            width=btn_width, height=btn_height, font=btn_font,
            fg_color="transparent", border_width=2, border_color="#3B8ED0"
        )
        self.btn_settings.place(relx=0.5, rely=0.65, anchor="center")

        # Nút 4: Exit
        self.btn_exit = ctk.CTkButton(
            self.main_bg, text="❌  Exit",
            width=btn_width, height=btn_height, font=btn_font,
            fg_color="#C0392B", hover_color="#E74C3C", command=self.quit
        )
        self.btn_exit.place(relx=0.5, rely=0.75, anchor="center")

        # Footer
        self.footer = ctk.CTkLabel(
            self.main_bg,
            text="v2.1 AI Edition | Powered by Vosk, Whisper & Spacy",
            font=("Segoe UI", 12), text_color="gray", fg_color="transparent"
        )
        self.footer.place(relx=0.5, rely=0.94, anchor="center")

    def open_voice_transcriber(self):
        if HybridTranscriberApp:
            self.withdraw()
            child = HybridTranscriberApp(self)
            child.protocol("WM_DELETE_WINDOW", lambda: [child.destroy(), self.deiconify()])

if __name__ == "__main__":
    app = MainMenuApp()
    app.mainloop()