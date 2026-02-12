#!/bin/bash

# NoteForge macOS Installation Script
# Python 3.12 required for best compatibility
# Handles Apple Silicon (M1/M2/M3) and Intel Macs

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🍎 NoteForge macOS Installation Script${NC}"
echo "========================================"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only."
    exit 1
fi

# Check architecture
arch=$(uname -m)
print_info "Architecture: $arch"

if [[ "$arch" == "arm64" ]]; then
    print_status "Apple Silicon detected (M1/M2/M3)"
else
    print_status "Intel Mac detected"
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
print_info "Python version: $python_version"

# Extract major and minor version
python_major=$(echo "$python_version" | cut -d. -f1)
python_minor=$(echo "$python_version" | cut -d. -f2)

# Check if Python 3.12 is installed
if [[ "$python_major" == "3" && "$python_minor" == "12" ]]; then
    print_status "Python 3.12 detected - excellent choice!"
elif [[ "$python_major" == "3" && "$python_minor" -ge "10" ]]; then
    print_warning "Python $python_version detected - Python 3.12 recommended for best compatibility"
    print_info "Consider installing Python 3.12 from https://python.org/downloads/"
else
    print_error "Python 3.10+ is required. Python $python_version is too old."
    print_info "Please install Python 3.12 from https://python.org/downloads/"
    print_info "Or using Homebrew: brew install python@3.12"
    exit 1
fi

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    print_warning "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    print_status "Homebrew detected"
fi

# Install Xcode Command Line Tools if not present
if ! xcode-select -p &> /dev/null; then
    print_info "Installing Xcode Command Line Tools..."
    xcode-select --install
    if [ -z "$NON_INTERACTIVE" ]; then
        print_warning "Please complete Xcode Command Line Tools installation and press Enter to continue..."
        read -p ""
    else
        print_warning "Xcode Command Line Tools installation started non-interactively"
    fi
else
    print_status "Xcode Command Line Tools detected"
fi

# Install system dependencies via Homebrew
print_info "Installing system dependencies..."
brew install portaudio llvm || print_warning "Some system dependencies may have failed to install"

# Create virtual environment
echo ""
print_info "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
echo ""
print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip, setuptools, wheel
print_info "Upgrading pip, setuptools, wheel..."
pip install --upgrade pip setuptools wheel

# Install PyTorch with proper backend for macOS
echo ""
print_info "Installing PyTorch (macOS optimized)..."
if [[ "$arch" == "arm64" ]]; then
    # Apple Silicon
    print_info "Installing PyTorch for Apple Silicon..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
else
    # Intel
    print_info "Installing PyTorch for Intel Mac..."
    pip install torch torchvision torchaudio
fi
print_status "PyTorch installed successfully"

# Install macOS-compatible requirements
echo ""
print_info "Installing NoteForge requirements..."
if pip install -r requirements-macos.txt; then
    print_status "Core requirements installed successfully"
else
    print_error "Some requirements failed to install"
    print_info "Retrying with --no-build-isolation..."
    pip install --no-build-isolation -r requirements-macos.txt || true
fi

# Handle webrtcvad separately if needed
echo ""
print_info "Setting up voice activity detection..."
if pip install webrtcvad 2>/dev/null; then
    print_status "webrtcvad installed successfully"
else
    print_warning "webrtcvad installation failed - using alternative VAD"
    print_info "NoteForge will work with limited voice detection features"
fi

# Verify installation
echo ""
print_info "Verifying installation..."

verification_script=$(cat << 'EOF'
import sys
try:
    import customtkinter
    import sounddevice
    import numpy
    import vosk
    import whisper
    import torch
    import transformers
    import psutil
    import Pillow
    print('✅ All core dependencies installed successfully!')
    print(f'Python: {sys.version}')
    print(f'PyTorch: {torch.__version__}')
    print(f'NumPy: {numpy.__version__}')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
EOF
)

if python3 -c "$verification_script"; then
    echo ""
    echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
    echo ""
    echo "📝 To run NoteForge:"
    echo "   1. Activate virtual environment: source venv/bin/activate"
    echo "   2. Run the app: python3 main.py"
    echo ""
    echo "💡 Important reminders:"
    echo "   - Grant microphone permissions in System Preferences > Privacy & Security"
    echo "   - First run may download large AI models (~100MB-1GB)"
    echo "   - See README-macos.md for troubleshooting"
else
    echo ""
    print_error "Installation verification failed"
    echo ""
    echo "🔧 Common solutions:"
    echo "   1. Restart terminal and try: source venv/bin/activate"
    echo "   2. Check Python version: python3 --version"
    echo "   3. Install Xcode Command Line Tools: xcode-select --install"
    echo "   4. Check Homebrew: brew doctor"
    echo ""
    exit 1
fi
