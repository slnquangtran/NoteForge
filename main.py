import customtkinter as ctk
import os
import sys
from PIL import Image

# --- Giữ nguyên logic Import của bạn ---
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

class MainMenuApp(ctk.CTk): 
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title("NoteForge")
        self.geometry("800x600")
        self.resizable(False, False)

        self.configure(fg_color="#0a0a0a")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue") 
        
        # Center the window
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        self.geometry(f"800x600+{x}+{y}")

        self.current_child = None

        # --- 1. THIẾT LẬP ẢNH NỀN LÀM MASTER (XÓA VỆT XÁM) ---
        bg_path = "bg.jpg" # Đảm bảo file ảnh image_8d8a74.png của bạn đổi tên thành bg.jpg
        img = Image.open(bg_path)
        self.bg_img_data = ctk.CTkImage(
            light_image=img,
            dark_image=img,
            size=(800, 600)
        )
        
        # Mọi widget sau này sẽ dùng self.main_bg làm 'master'
        self.main_bg = ctk.CTkLabel(self, image=self.bg_img_data, text="")
        self.main_bg.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_widgets()

    def create_widgets(self):
        # --- 2. HEADER (Gắn trực tiếp vào main_bg) ---
        self.title_label = ctk.CTkLabel(
            self.main_bg, 
            text="⚡ NOTEFORGE", 
            font=("Segoe UI", 42, "bold"),
            text_color="#fdcc4b",
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

        # --- 3. KHU VỰC NÚT BẤM (Gắn trực tiếp vào main_bg) ---
        btn_width = 300
        btn_height = 50
        btn_font = ("Segoe UI", 16)

        # 1. Real-Time Transcription
        self.btn_transcriber = ctk.CTkButton(
            self.main_bg,
            text="   🎤   Real-Time Transcription   ",
            font=btn_font,
            width=btn_width,
            height=btn_height,
            fg_color="#00ADB5",      # Màu xanh Teal hiện đại
            hover_color="#00FFF5",   # Màu Neon khi di chuột
            border_width=2, 
            border_color="#AAD7D9",  # Viền xanh nhạt tạo độ bóng
            command=self.open_voice_transcriber
        )
        self.btn_transcriber.place(relx=0.5, rely=0.45, anchor="center")

        # 2. Note Summarization
        self.btn_study = ctk.CTkButton(
            self.main_bg,
            text="   📝   Note Summarization   ",
            font=btn_font,
            width=btn_width,
            height=btn_height,
            fg_color="#982598",
            hover_color="#E491C9",
            command=self.open_study_assistant, # Giữ nguyên chức năng
            border_width=2, 
            border_color="#F1E9E9"
        )
        self.btn_study.place(relx=0.5, rely=0.55, anchor="center")

        # 3. Settings
        self.btn_settings = ctk.CTkButton(
            self.main_bg,
            text="   ⚙️   Settings   ",
            font=btn_font,
            width=btn_width,
            height=btn_height,
            fg_color="transparent",
            border_width=2,
            border_color="#3B8ED0",
            text_color="#DCE4EE",
            command=self.open_settings # Giữ nguyên chức năng
        )
        self.btn_settings.place(relx=0.5, rely=0.65, anchor="center")

        # 4. Exit
        self.btn_exit = ctk.CTkButton(
            self.main_bg,
            text="   ❌   Exit   ",
            font=btn_font,
            width=btn_width,
            height=btn_height,
            fg_color="#F63049",
            hover_color="#D02752",
            command=self.exit_app, # Giữ nguyên chức năng
            border_width=2, 
            border_color="#8A244B"
        )
        self.btn_exit.place(relx=0.5, rely=0.75, anchor="center")

        # --- 4. FOOTER ---
        self.footer_label = ctk.CTkLabel(
            self.main_bg,
            text="v2.1 AI Edition | Powered by Vosk, Whisper & Spacy",
            font=("Segoe UI", 12),
            text_color="gray",
            fg_color="transparent"
        )
        self.footer_label.place(relx=0.5, rely=0.95, anchor="center")

    # --- CÁC HÀM CHỨC NĂNG (GIỮ NGUYÊN HOÀN TOÀN TỪ CODE CŨ CỦA BẠN) ---
    def open_voice_transcriber(self):
        if HybridTranscriberApp is None:
            print("App module not found")
            return
        self.withdraw()
        self.current_child = HybridTranscriberApp(self)
        
        def on_child_close():
            self.current_child.destroy()
            self.current_child = None
            self.deiconify()
            
        self.current_child.protocol("WM_DELETE_WINDOW", on_child_close)
        self.current_child.focus()

    def open_study_assistant(self):
        if StudyAssistantGUI is None:
            print("Study GUI module not found")
            return
        self.withdraw()
        self.current_child = StudyAssistantGUI(self)
        
        def on_child_close():
            self.current_child.destroy()
            self.current_child = None
            self.deiconify()
            
        self.current_child.protocol("WM_DELETE_WINDOW", on_child_close)
        self.current_child.focus()

    def open_settings(self):
        toplevel = ctk.CTkToplevel(self)
        toplevel.geometry("300x200")
        toplevel.title("Settings")
        toplevel.focus()
        toplevel.attributes("-topmost", True) # Đảm bảo hiện lên trên ảnh nền
        ctk.CTkLabel(toplevel, text="Settings", font=("Bold", 20)).pack(pady=20)
        ctk.CTkLabel(toplevel, text="Global config coming soon...").pack(pady=10)

    def exit_app(self):
        self.quit()
        sys.exit()

if __name__ == "__main__":
    app = MainMenuApp()
    app.mainloop()