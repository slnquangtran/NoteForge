"""
NoteForge macOS Compatibility Module
Handles all macOS-specific compatibility issues and provides utilities
for cross-platform support including Apple Silicon and Intel Macs.
"""

import sys
import platform
import os
import subprocess
from typing import Optional, Tuple


def get_platform_info() -> dict:
    """
    Get detailed platform information.
    
    Returns:
        Dictionary containing platform details
    """
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'is_macos': platform.system() == 'Darwin',
        'is_apple_silicon': platform.machine() == 'arm64',
        'is_intel': platform.machine() == 'x86_64',
    }


def check_python_version() -> Tuple[bool, str]:
    """
    Check if Python version is compatible with NoteForge.
    
    Returns:
        Tuple of (is_compatible, message)
    """
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    if version_info.major == 3 and version_info.minor >= 10:
        return True, f"Python {version_str} is compatible"
    elif version_info.major == 3 and version_info.minor == 9:
        return True, f"Python {version_str} is compatible (3.12 recommended)"
    elif version_info.major == 3 and version_info.minor == 12:
        return True, f"Python {version_str} is optimal for macOS"
    else:
        return False, f"Python {version_str} is not compatible. Python 3.10+ required"


def check_macos_deps() -> dict:
    """
    Check for required macOS dependencies.
    
    Returns:
        Dictionary with dependency status
    """
    deps = {
        'xcode_tools': False,
        'homebrew': False,
        'portaudio': False,
        'llvm': False,
    }
    
    # Check Xcode Command Line Tools
    try:
        result = subprocess.run(['xcode-select', '-p'], capture_output=True, text=True)
        deps['xcode_tools'] = result.returncode == 0
    except FileNotFoundError:
        deps['xcode_tools'] = False
    
    # Check Homebrew
    try:
        result = subprocess.run(['brew', '--version'], capture_output=True, text=True)
        deps['homebrew'] = result.returncode == 0
    except (FileNotFoundError, subprocess.SubprocessError):
        deps['homebrew'] = False
    
    # Check PortAudio
    try:
        result = subprocess.run(['pkg-config', '--exists', 'portaudio'], capture_output=True, text=True)
        deps['portaudio'] = result.returncode == 0
    except (FileNotFoundError, subprocess.SubprocessError):
        deps['portaudio'] = False
    
    # Check LLVM
    try:
        result = subprocess.run(['llvm-config', '--version'], capture_output=True, text=True)
        deps['llvm'] = result.returncode == 0
    except (FileNotFoundError, subprocess.SubprocessError):
        deps['llvm'] = False
    
    return deps


def get_macos_version() -> Optional[str]:
    """
    Get macOS version name (e.g., "Ventura", "Monterey").
    
    Returns:
        Version name or None if unavailable
    """
    version_map = {
        '13': 'Ventura',
        '14': 'Sonoma',
        '15': 'Sequoia',
    }
    
    try:
        version_str = platform.mac_ver()[0]
        major = version_str.split('.')[0]
        return version_map.get(major, f"macOS {version_str}")
    except (IndexError, AttributeError):
        return None


def get_recommended_pytorch_url() -> str:
    """
    Get the recommended PyTorch installation URL for current platform.
    
    Returns:
        PyTorch index URL for pip
    """
    info = get_platform_info()
    
    if info['is_macos']:
        if info['is_apple_silicon']:
            return "https://download.pytorch.org/whl/cpu"
        else:
            return "https://download.pytorch.org/whl/cpu"
    
    return "https://download.pytorch.org/whl/cpu"


def setup_microphone_permissions() -> bool:
    """
    Check if microphone permissions are granted.
    
    Returns:
        True if permissions are granted, False otherwise
    """
    if sys.platform != 'darwin':
        return True
    
    # On macOS, we can't programmatically check permissions
    # This is a placeholder for future implementation
    return True


def get_macos_specific_requirements() -> list:
    """
    Get macOS-specific package recommendations.
    
    Returns:
        List of recommended Homebrew packages
    """
    return [
        'portaudio',  # For sounddevice
        'llvm',       # For llvmlite compilation
    ]


def patch_sounddevice_for_macos():
    """
    Apply workarounds for sounddevice on macOS.
    
    This function can be called to apply macOS-specific patches
    for the sounddevice library.
    """
    if sys.platform != 'darwin':
        return
    
    try:
        import sounddevice
        # Check if portaudio is properly linked
        import os
        if 'PYAUDIO_DRIVER' not in os.environ:
            os.environ['PYAUDIO_DRIVER'] = 'coreaudio'
    except ImportError:
        pass


def get_installation_instructions() -> dict:
    """
    Get platform-specific installation instructions.
    
    Returns:
        Dictionary with installation instructions
    """
    info = get_platform_info()
    
    instructions = {
        'general': [
            "Install Xcode Command Line Tools: xcode-select --install",
            "Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"",
            "Install system dependencies: brew install portaudio llvm",
            "Create virtual environment: python3 -m venv venv",
            "Install requirements: pip install -r requirements-macos.txt",
        ],
        'apple_silicon': [
            "Python 3.12 recommended for best performance",
            "PyTorch will use MPS backend on Apple Silicon",
            "First run may be slower as models are downloaded",
        ],
        'intel': [
            "Python 3.10+ supported",
            "PyTorch will use CPU backend",
            "Consider upgrading to Apple Silicon for better performance",
        ],
    }
    
    if info['is_apple_silicon']:
        return {
            'platform': 'Apple Silicon Mac',
            'architecture': 'arm64',
            'python_recommendation': '3.12',
            'pytorch_backend': 'MPS',
            'steps': instructions['general'] + instructions['apple_silicon'],
        }
    else:
        return {
            'platform': 'Intel Mac',
            'architecture': 'x86_64',
            'python_recommendation': '3.10+',
            'pytorch_backend': 'CPU',
            'steps': instructions['general'] + instructions['intel'],
        }


def validate_installation() -> Tuple[bool, list]:
    """
    Run a comprehensive installation validation.
    
    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []
    
    # Check Python version
    is_compatible, message = check_python_version()
    if not is_compatible:
        issues.append(f"Python: {message}")
    
    # Check macOS dependencies
    if platform.system() == 'Darwin':
        deps = check_macos_deps()
        if not deps['xcode_tools']:
            issues.append("Xcode Command Line Tools not installed")
        if not deps['homebrew']:
            issues.append("Homebrew not installed")
    
    # Check critical imports
    critical_imports = [
        ('customtkinter', 'GUI framework'),
        ('sounddevice', 'Audio processing'),
        ('vosk', 'Speech recognition'),
        ('whisper', 'Speech recognition'),
        ('torch', 'Machine learning'),
    ]
    
    for module, description in critical_imports:
        try:
            __import__(module)
        except ImportError:
            issues.append(f"{module} ({description}) not installed")
    
    return len(issues) == 0, issues
