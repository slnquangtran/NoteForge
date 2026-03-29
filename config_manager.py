# Wrapper for the new package-based config system
import sys
import os

# Ensure src is in path for standalone execution/legacy imports
repo_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from noteforge.config.settings import load_settings, save_settings, get_setting, set_setting, DEFAULT_SETTINGS
from noteforge.config.paths import get_config_file, get_whisper_cache_dir, get_vosk_model_dir

import shutil
import platform
import requests
import zipfile
try:
    import whisper
except ImportError:
    whisper = None

CONFIG_FILE = get_config_file()

def validate_config():
    """Ensures config file has valid keys/values."""
    settings = load_settings()
    changed = False
    
    # Ensure defaults exist
    for k, v in DEFAULT_SETTINGS.items():
        if k not in settings:
            settings[k] = v
            changed = True
            
    if changed:
        save_settings(settings)

from noteforge.models.downloader import download_vosk, download_whisper, download_bart, delete_all_models as clear_all_models

def download_models(progress_callback=None):
    """Ensures all models are present."""
    v = download_vosk(progress_callback)
    w = download_whisper(progress_callback=progress_callback)
    b = download_bart(progress_callback)
    return v and w # BART is optional for Core

def delete_models():
    """Compatibility wrapper for clearing models."""
    return clear_all_models()