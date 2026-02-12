#!/usr/bin/env python3
"""
NoteForge macOS Pre-flight Check Script
Run this before installing NoteForge to ensure your system is ready.
"""

import sys
import subprocess
import platform
from typing import Tuple, List


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
    print("=" * 60)


def print_status(name: str, status: str, details: str = ""):
    """Print a status line with consistent formatting."""
    status_symbol = {
        'OK': f"{Colors.GREEN}✓{Colors.END}",
        'WARNING': f"{Colors.YELLOW}⚠{Colors.END}",
        'ERROR': f"{Colors.RED}✗{Colors.END}",
        'INFO': f"{Colors.BLUE}ℹ{Colors.END}",
    }.get(status, "?")
    
    print(f"  {status_symbol} {name}")
    if details:
        print(f"     {details}")


def check_python_version() -> Tuple[bool, str]:
    """Check Python version compatibility."""
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    if version_info.major == 3 and version_info.minor == 12:
        return True, f"Python {version_str} - Optimal for macOS"
    elif version_info.major == 3 and version_info.minor >= 10:
        return True, f"Python {version_str} - Compatible"
    elif version_info.major == 3 and version_info.minor == 9:
        return True, f"Python {version_str} - Compatible (3.12 recommended)"
    elif version_info.major == 3 and version_info.minor < 9:
        return False, f"Python {version_str} - Too old (3.9+ required)"
    else:
        return False, f"Python {version_str} - Not supported"


def check_xcode_tools() -> Tuple[bool, str]:
    """Check if Xcode Command Line Tools are installed."""
    try:
        result = subprocess.run(
            ['xcode-select', '-p'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return True, "Installed"
        else:
            return False, "Not installed"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, "Not installed"


def check_homebrew() -> Tuple[bool, str]:
    """Check if Homebrew is installed."""
    try:
        result = subprocess.run(
            ['brew', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            return True, version
        else:
            return False, "Not installed"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, "Not installed"


def check_system_deps() -> Tuple[bool, List[str]]:
    """Check for required system dependencies."""
    missing = []
    
    deps = [
        ('portaudio', 'PortAudio (audio I/O)'),
        ('llvm', 'LLVM (compiler toolchain)'),
    ]
    
    for dep, description in deps:
        try:
            result = subprocess.run(
                ['pkg-config', '--exists', dep],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                missing.append(description)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            missing.append(description)
    
    return len(missing) == 0, missing


def check_architecture() -> Tuple[bool, str]:
    """Check system architecture."""
    machine = platform.machine()
    
    if machine == 'arm64':
        return True, f"Apple Silicon ({machine}) - Excellent for ML"
    elif machine == 'x86_64':
        return True, f"Intel ({machine}) - Compatible"
    else:
        return False, f"Unknown architecture ({machine})"


def check_macos_version() -> Tuple[bool, str]:
    """Check macOS version."""
    version = platform.mac_ver()[0]
    major = int(version.split('.')[0])
    
    if major >= 11:  # Big Sur and later
        return True, f"macOS {version} - Compatible"
    elif major >= 10:
        return True, f"macOS {version} - May require adjustments"
    else:
        return False, f"macOS {version} - Too old"


def check_disk_space() -> Tuple[bool, str]:
    """Check available disk space."""
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        free_gb = free / (1024**3)
        
        if free_gb > 10:
            return True, f"{free_gb:.1f} GB available - Excellent"
        elif free_gb > 5:
            return True, f"{free_gb:.1f} GB available - Good"
        elif free_gb > 2:
            return False, f"{free_gb:.1f} GB available - Low (5GB+ recommended)"
        else:
            return False, f"{free_gb:.1f} GB available - Insufficient"
    except Exception:
        return False, "Unable to check disk space"


def main():
    """Run all pre-flight checks."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}🍎 NoteForge Pre-flight Check{Colors.END}")
    print("=" * 60)
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.system()} {platform.release()}")
    
    all_checks_passed = True
    
    # Python Version
    print_header("Python Installation")
    passed, message = check_python_version()
    print_status("Python Version", "OK" if passed else "ERROR", message)
    if not passed:
        all_checks_passed = False
    
    # macOS Version
    print_header("macOS System")
    passed, message = check_macos_version()
    print_status("macOS Version", "OK" if passed else "WARNING", message)
    
    # Architecture
    passed, message = check_architecture()
    print_status("Architecture", "OK" if passed else "WARNING", message)
    
    # Xcode Tools
    print_header("Developer Tools")
    passed, message = check_xcode_tools()
    print_status("Xcode Command Line Tools", "OK" if passed else "ERROR", message)
    if not passed:
        all_checks_passed = False
        print("     Install with: xcode-select --install")
    
    # Homebrew
    print_header("Package Manager")
    passed, message = check_homebrew()
    print_status("Homebrew", "OK" if passed else "WARNING", message)
    if not passed:
        print("     Install with: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    
    # System Dependencies
    print_header("System Dependencies")
    passed, missing = check_system_deps()
    if passed:
        print_status("Dependencies", "OK", "All required dependencies installed")
    else:
        print_status("Dependencies", "WARNING", f"Missing: {', '.join(missing)}")
        print("     Install with: brew install portaudio llvm")
    
    # Disk Space
    print_header("Disk Space")
    passed, message = check_disk_space()
    print_status("Free Space", "OK" if passed else "WARNING", message)
    
    # Summary
    print_header("Summary")
    if all_checks_passed:
        print(f"\n{Colors.GREEN}✅ Your system is ready for NoteForge!{Colors.END}")
        print("\nTo install:")
        print("  1. chmod +x install-macos.sh")
        print("  2. ./install-macos.sh")
        print("\nOr for manual installation:")
        print("  1. Create virtual environment: python3 -m venv venv")
        print("  2. Activate: source venv/bin/activate")
        print("  3. Install: pip install -r requirements-macos.txt")
        return 0
    else:
        print(f"\n{Colors.YELLOW}⚠️  Some checks failed.{Colors.END}")
        print("Please resolve the issues marked with ✗ before installing.")
        print("\nFor help, see:")
        print("  - README-macos.md")
        print("  - https://github.com/your-repo/noteforge/issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
