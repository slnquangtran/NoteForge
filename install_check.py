#!/usr/bin/env python3
"""
NoteForge Dependency Checker
Verifies all required dependencies are installed before running the app.
Supports Windows, Linux, and macOS.
"""

import sys
import platform


def check_dependencies():
    missing = []
    
    dependencies = [
        ('customtkinter', 'customtkinter'),
        ('sounddevice', 'sounddevice'),
        ('numpy', 'numpy'),
        ('vosk', 'vosk'),
        ('whisper', 'openai-whisper'),
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
    
    # macOS-specific optional dependencies
    macos_optional = [
        ('webrtcvad', 'webrtcvad'),
    ]
    
    print("🔍 Checking NoteForge dependencies...\n")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python: {platform.python_version()}\n")
    
    # Check core dependencies
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - MISSING")
            missing.append(package_name)
    
    # Check macOS-specific optional dependencies
    if platform.system() == "Darwin":
        print(f"\n🍎 macOS Optional Dependencies:")
        for module_name, package_name in macos_optional:
            try:
                __import__(module_name)
                print(f"✅ {package_name} (optional)")
            except ImportError:
                print(f"⚠️  {package_name} (optional) - NOT INSTALLED")
                print(f"    Voice Activity Detection will use fallback mode")
    
    print()
    
    if missing:
        print(f"⚠️  {len(missing)} dependencies are missing!")
        print("\nTo install missing dependencies:")
        
        if platform.system() == "Darwin":
            print("  🍎 macOS detected. Use:")
            print("    source venv/bin/activate")
            print("    pip install -r requirements-macos.txt")
            print("\n  Or run the automated installer:")
            print("    chmod +x install-macos.sh")
            print("    ./install-macos.sh")
        else:
            print("  pip install -r requirements.txt")
        
        print("\nOr install individually:")
        for pkg in missing:
            print(f"  pip install {pkg}")
        
        print("\n💡 Tip: Run 'python check-macos-deps.py' (macOS) to check system requirements")
        return False
    else:
        print("✅ All dependencies installed!")
        
        # Check PyTorch backend availability
        if platform.system() == "Darwin":
            try:
                import torch
                if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    print("✅ PyTorch MPS backend available (Apple Silicon optimized)")
                else:
                    print("ℹ️  PyTorch using CPU backend")
            except:
                pass
        
        print("\n🚀 You can now run:")
        if platform.system() == "Darwin":
            print("  source venv/bin/activate")
        print("  python main.py")
        return True


if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)
