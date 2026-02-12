"""NoteForge macOS health check script"""

import platform
import subprocess
import sys


def main():
    print("NoteForge macOS Health Check")
    print("===========================")
    print("Platform:", platform.system(), platform.release())
    print("Python:", platform.python_version())

    # Xcode Command Line Tools
    try:
        res = subprocess.run(["xcode-select", "-p"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        xcode_ok = (res.returncode == 0)
    except Exception:
        xcode_ok = False
    print("Xcode Command Line Tools:", "OK" if xcode_ok else "Missing")

    # Homebrew
    try:
        res = subprocess.run(["brew", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        brew_ok = (res.returncode == 0)
    except Exception:
        brew_ok = False
    print("Homebrew:", "OK" if brew_ok else "Missing")

    # VosK
    try:
        import vosk  # type: ignore
        vosk_ver = getattr(vosk, "__version__", "unknown")
        vosk_ok = True
    except Exception:
        vosk_ok = False
        vosk_ver = None
    print("VosK:", vosk_ver if vosk_ok else "Missing")

    # PortAudio
    try:
        subprocess.run(["pkg-config", "--exists", "portaudio"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        pa_ok = True
    except Exception:
        pa_ok = False
    print("PortAudio:", "OK" if pa_ok else "Missing")

    # Tkinter availability
    try:
        import tkinter  # noqa: F401
        print("Tkinter: OK")
    except Exception:
        print("Tkinter: Missing")

    ok = xcode_ok and brew_ok and pa_ok and vosk_ok
    print("\nOverall:", "PASS" if ok else "ISSUES DETECTED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
