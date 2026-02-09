# NoteForge

**Smart Note Creation: Real-Time Transcription & Intelligent Note Summarization**

NoteForge is a powerful dual-purpose application that combines real-time voice transcription with AI-powered note summarization. Perfect for students, professionals, and anyone who needs to capture and organize spoken content into study-ready notes.

## Features

### Real-Time Transcription
- **Hybrid AI Architecture**: Combines Vosk (instant streaming) + Whisper (high accuracy)
- **Voice Activity Detection**: Precise speech detection using WebRTC VAD
- **Professional Audio Processing**:
  - Noise reduction
  - Dynamic gain normalization
  - 16kHz optimized sample rate
- **Modern UI**: Dark mode, audio level meter, always-on-top mode
- **Offline Capable**: Runs completely locally after initial setup

### Note Summarization
- **Semantic Topic Extraction**: Automatically organizes content by topics
- **Legal Content Recognition**: Detects case law, legal principles, and doctrines
- **Smart Classification**: Categorizes content into:
  - Definitions
  - Legal Rules & Principles
  - Key Cases (with citations)
  - Exceptions & Special Rules
  - Practical Examples
- **Multiple Input Formats**: Supports both text transcripts (.txt) and PowerPoint (.pptx)
- **Study-Ready Output**: Generates structured lecture notes organized by topic
- **PDF Export**: Save your notes as professional PDFs
- **Automatic Session Export**: (NEW) Automatically saves every recording as `.wav` and `.txt` in the `recordings/` folder.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/slnquangtran/NoteForge.git
cd NoteForge
```

### 2. macOS Prerequisites (Install FIRST)
If you're on macOS, install system dependencies **before** Python packages:
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install system dependencies
brew install portaudio llvm

# Install Xcode Command Line Tools
xcode-select --install
```

### 3. Install Python Dependencies
```bash
# Set LLVM path for macOS (Python 3.12 users)
export LLVM_CONFIG=$(brew --prefix llvm)/bin/llvm-config  # macOS only

# Install all dependencies
pip install -r requirements.txt
```

### 4. Verify Installation
Check that all dependencies are installed:
```bash
python install_check.py
```
You should see `✅ All dependencies installed!` before proceeding.

### 5. Troubleshooting (macOS)
If you encounter **"Failed to build wheel"** or **"PortAudio not found"** errors on Mac, follow these steps:
1.  **Install Homebrew**: [/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"](https://brew.sh)
2.  **Install System Deps**: `brew install portaudio llvm`
3.  **Install Xcode Tools**: `xcode-select --install`

#### 🛠️ Fix for `llvmlite` / `numba` Build Error
If you are on **Python 3.12** and see `TypeError: spawn() got an unexpected keyword argument 'dry_run'`, follow these steps:
1.  **Ensure LLVM is installed**: `brew install llvm`
2.  **Use the correct env var**:
```bash
export LLVM_CONFIG=$(brew --prefix llvm)/bin/llvm-config
pip install "llvmlite==0.42.0"
pip install -r requirements.txt
```

#### 🛠️ Fix for `ModuleNotFoundError: No module named 'whisper'`
If you see this error even after installing requirements:
1. **Uninstall duplicates**: `pip uninstall whisper` (this is a different package)
2. **Reinstall correct package**: `pip install openai-whisper`
3. **Check environment**: Ensure you are running `python` from the same environment where you ran `pip install`.

#### ✅ Verify Installation
After installing dependencies, verify everything is ready:
```bash
python -c "import torch; import whisper; import vosk; import pptx; print('✅ All dependencies installed!')"
```
If you see any `ModuleNotFoundError`, reinstall that specific package or run `pip install -r requirements.txt` again.

*NoteForge v1.1.0 pins `llvmlite==0.42.0` and `numpy<2.0.0` which officially support Python 3.12.*

### 6. Hardware Acceleration (Optional but Recommended)
- **Windows (NVIDIA)**: Automatically uses CUDA if available.
- **macOS (Apple Silicon)**: Automatically uses MPS (Metal Performance Shaders) for Whisper inference.

### 7. Launch NoteForge
```bash
python main.py
```
*Models will be downloaded automatically on the first run. The app will detect your hardware (CUDA/MPS/CPU) and optimize performance accordingly.*


