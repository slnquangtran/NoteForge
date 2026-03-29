import os
import platform

def get_repo_root():
    # Relative to this file: src/noteforge/config/paths.py
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

def get_config_file():
    return os.path.join(get_repo_root(), "config.json")

def get_vosk_model_dir():
    return os.path.join(get_repo_root(), "model")

def get_whisper_cache_dir():
    if platform.system() == "Windows":
        return os.path.join(os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local"), "Whisper", "models")
    else: # Linux, macOS
        return os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache"), "whisper")

def get_recordings_dir():
    d = os.path.join(get_repo_root(), "recordings")
    if not os.path.exists(d):
        os.makedirs(d, exist_ok=True)
    return d
