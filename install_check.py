#!/usr/bin/env python3
"""
NoteForge Dependency Checker
Verifies all required dependencies are installed before running the app.
"""

import sys

def check_dependencies():
    missing = []
    
    dependencies = [
        ('customtkinter', 'customtkinter'),
        ('sounddevice', 'sounddevice'),
        ('numpy', 'numpy'),
        ('vosk', 'vosk'),
        ('whisper', 'openai-whisper'),
        ('webrtcvad', 'webrtcvad-wheels'),
        ('PIL', 'Pillow'),
        ('transformers', 'transformers'),
        ('torch', 'torch'),
        ('sentencepiece', 'sentencepiece'),
        ('psutil', 'psutil'),
        ('tqdm', 'tqdm'),
        ('requests', 'requests'),
        ('pptx', 'python-pptx'),
        ('reportlab', 'reportlab'),
        ('huggingface_hub', 'huggingface-hub'),
    ]
    
    print("🔍 Checking NoteForge dependencies...\n")
    
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - MISSING")
            missing.append(package_name)
    
    print()
    
    if missing:
        print(f"⚠️  {len(missing)} dependencies are missing!")
        print("\nTo install missing dependencies, run:")
        print("  pip install -r requirements.txt")
        print("\nOr install individually:")
        for pkg in missing:
            print(f"  pip install {pkg}")
        return False
    else:
        print("✅ All dependencies installed! You can now run:")
        print("  python main.py")
        return True

if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)
