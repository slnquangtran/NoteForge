# NoteForge macOS Installation Guide

This guide provides step-by-step instructions for installing NoteForge on macOS, including both Intel and Apple Silicon (M1/M2/M3) Macs.

## Table of Contents

- [System Requirements](#system-requirements)
- [Quick Installation](#quick-installation)
- [Manual Installation](#manual-installation)
- [Troubleshooting](#troubleshooting)
- [Apple Silicon vs Intel](#apple-silicon-vs-intel)

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| macOS Version | 10.15 (Catalina) | 12.0 (Monterey) or later |
| Python | 3.10 | 3.12 |
| RAM | 4 GB | 8 GB |
| Storage | 2 GB | 5 GB (plus model downloads) |
| Architecture | x86_64 (Intel) or arm64 (Apple Silicon) | arm64 (Apple Silicon) |

## Quick Installation

### Step 1: Run Pre-flight Check

Before installing, run the pre-flight check script to verify your system is ready:

```bash
python check-macos-deps.py
```

This will check:
- ✅ Python version
- ✅ Xcode Command Line Tools
- ✅ Homebrew
- ✅ System dependencies (PortAudio, LLVM)
- ✅ Disk space

### Step 2: Run Installation Script

```bash
chmod +x install-macos.sh
./install-macos.sh
```

The installation script will:
1. Detect your architecture (Intel vs Apple Silicon)
2. Install Xcode Command Line Tools if needed
3. Install Homebrew dependencies (PortAudio, LLVM)
4. Create a Python virtual environment
5. Install PyTorch optimized for your Mac
6. Install all Python dependencies
7. Verify the installation

### Step 3: Run NoteForge

```bash
# Activate the virtual environment
source venv/bin/activate

# Run NoteForge
python main.py
```

## Manual Installation

If you prefer to install manually or the script doesn't work:

### Step 1: Install System Dependencies

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required system libraries
brew install portaudio llvm
```

### Step 2: Install Xcode Command Line Tools

```bash
xcode-select --install
```

### Step 3: Install Python 3.12

**Option A: Download from python.org**

1. Download Python 3.12 from https://www.python.org/downloads/
2. Run the installer
3. Verify installation: `python3 --version`

**Option B: Using Homebrew**

```bash
brew install python@3.12
echo 'export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"' >> ~/.zshrc
```

### Step 4: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

### Step 5: Install Python Dependencies

```bash
pip install -r requirements-macos.txt
```

### Step 6: Verify Installation

```bash
python -c "
import customtkinter
import sounddevice
import vosk
import whisper
import torch
import transformers
print('✅ All dependencies installed successfully!')
"
```

## Apple Silicon vs Intel

### Apple Silicon (M1/M2/M3)

**Advantages:**
- ✅ Better performance for ML tasks
- ✅ More efficient power usage
- ✅ PyTorch supports MPS backend
- ✅ Faster model inference

**Installation Notes:**
- Python 3.12 recommended for best compatibility
- PyTorch installs with CPU support (MPS is experimental)
- First run may be slower as models are downloaded

**Verify Apple Silicon:**
```bash
uname -m  # Should return "arm64"
```

### Intel Mac

**Installation Notes:**
- Standard PyTorch installation
- Python 3.10+ supported
- Consider upgrading to Apple Silicon for better performance

**Verify Intel:**
```bash
uname -m  # Should return "x86_64"
```

## Troubleshooting

### Common Installation Issues

#### ❌ "ModuleNotFoundError: No module named 'utils'"

**Cause:** Missing utils module

**Solution:**
```bash
# Make sure you're in the correct directory
cd /path/to/NoteForge

# The utils module should be created during installation
ls utils/
```

#### ❌ "xcrun: error: invalid active developer path"

**Cause:** Xcode Command Line Tools not installed

**Solution:**
```bash
xcode-select --install
```

#### ❌ "portaudio.h not found"

**Cause:** PortAudio not installed

**Solution:**
```bash
brew install portaudio
pip install --no-cache-dir sounddevice
```

#### ❌ "llvmlite installation failed"

**Cause:** LLVM not installed or version mismatch

**Solution:**
```bash
brew install llvm
export LLVM_CONFIG=/opt/homebrew/opt/llvm/bin/llvm-config  # Apple Silicon
# or
export LLVM_CONFIG=/usr/local/opt/llvm/bin/llvm-config  # Intel
pip install llvmlite==0.42.0
```

#### ❌ "Microphone not working"

**Cause:** Microphone permissions not granted

**Solution:**
1. Open System Preferences > Privacy & Security
2. Select Microphone
3. Enable access for your terminal/app

#### ❌ "PyTorch MPS backend not available"

**Cause:** macOS version too old or PyTorch version incompatible

**Solution:**
```python
# Check PyTorch version
import torch
print(torch.__version__)

# MPS requires macOS 12.3+ and PyTorch 2.0+
# Falls back to CPU automatically
```

#### ❌ "Python version too old"

**Cause:** Using Python 3.9 or earlier

**Solution:**
```bash
# Check current version
python3 --version

# Install Python 3.12
brew install python@3.12

# Or download from https://python.org/downloads/
```

#### ❌ "webrtcvad installation failed"

**Cause:** Compilation issues on macOS

**Solution:**
```bash
# Skip webrtcvad - NoteForge will use alternative VAD
# Or try installing with conda
conda install -c conda-forge webrtcvad
```

### Performance Issues

#### Slow First Run

**Cause:** Downloading AI models for the first time

**Solution:**
- Models are ~100MB-1GB
- First run may take 5-15 minutes
- Ensure stable internet connection

#### High CPU Usage

**Cause:** Running on CPU instead of GPU/MPS

**Solution:**
- Apple Silicon: PyTorch should use MPS automatically
- Check with: `torch.backends.mps.is_available()`
- Falls back to CPU if MPS unavailable

### Verification Commands

```bash
# Check Python version
python3 --version

# Check architecture
uname -m

# Check Xcode tools
xcode-select -p

# Check Homebrew
brew --version

# Check PyTorch
python3 -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'MPS available: {torch.backends.mps.is_available()}')"

# Check all imports
python3 -c "
import customtkinter
import sounddevice
import vosk
import whisper
import torch
import transformers
import psutil
import numpy
print('✅ All imports successful')
"
```

## Getting Help

If you encounter issues not covered here:

1. **Check existing issues:** https://github.com/your-repo/noteforge/issues
2. **Run diagnostic script:** `python check-macos-deps.py`
3. **Check logs:** Look for error messages in terminal output
4. **Search online:** Your issue may have been solved by other users

## Known Limitations

- **webrtcvad:** May require conda installation on older macOS versions
- **MPS Backend:** Some PyTorch operations may not be supported on MPS
- **Microphone:** Requires explicit user permission on macOS

## System Architecture

```
NoteForge/
├── install-macos.sh     # Automated installation script
├── check-macos-deps.py  # Pre-flight system check
├── macos_compat.py      # macOS compatibility layer
├── requirements.txt     # Windows/Linux dependencies
├── requirements-macos.txt  # macOS-specific dependencies
├── utils/
│   ├── __init__.py
│   └── logger.py
└── README-macos.md      # This file
```

## Version Compatibility Matrix

| macOS Version | Python | PyTorch | Status |
|---------------|--------|---------|--------|
| 10.15 (Catalina) | 3.10 | 2.0+ | ✅ Supported |
| 11 (Big Sur) | 3.10-3.12 | 2.0+ | ✅ Supported |
| 12 (Monterey) | 3.10-3.12 | 2.0+ | ✅ Recommended |
| 13 (Ventura) | 3.10-3.12 | 2.0+ | ✅ Recommended |
| 14 (Sonoma) | 3.10-3.12 | 2.0+ | ✅ Recommended |
| 15 (Sequoia) | 3.10-3.12 | 2.0+ | ✅ Recommended |
