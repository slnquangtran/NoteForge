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

### 2. Install Dependencies
```bash
# Windows & macOS
pip install -r requirements.txt
```
*Note: macOS users are automatically pinned to `vosk==0.3.44` for system stability.*

### 3. Prerequisites for macOS (IMPORTANT)
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
*NoteForge v1.1.0 pins `llvmlite==0.42.0` and `numpy<2.0.0` which officially support Python 3.12.*

### 4. Hardware Acceleration (Optional but Recommended)
- **Windows (NVIDIA)**: Automatically uses CUDA if available.
- **macOS (Apple Silicon)**: Automatically uses MPS (Metal Performance Shaders) for Whisper inference.

### 5. Launch NoteForge
```bash
python main.py
```
*Models will be downloaded automatically on the first run. The app will detect your hardware (CUDA/MPS/CPU) and optimize performance accordingly.*


