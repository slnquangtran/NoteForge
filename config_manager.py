import json
import os
import shutil
import platform
import subprocess
import requests
import zipfile
import whisper

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

DEFAULT_SETTINGS = {
    "whisper_model_size": "large",
}

def load_settings():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                settings = json.load(f)
                return {**DEFAULT_SETTINGS, **settings}
            except json.JSONDecodeError:
                print("Error reading config.json, using default settings.")
                return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_settings(settings):
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def get_setting(key):
    settings = load_settings()
    return settings.get(key, DEFAULT_SETTINGS.get(key))

def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)

def get_whisper_cache_dir():
    # Attempt to find Whisper's default cache directory
    # This logic is based on common XDG_CACHE_HOME usage and Whisper's default behavior
    if platform.system() == "Windows":
        return os.path.join(os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local"), "Whisper", "models")
    else: # Linux, macOS
        return os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache"), "whisper")

def delete_models(whisper_model_size_to_delete=None):
    success_vosk = False
    success_whisper = False

    # 1. Delete Vosk model (project root model directory)
    # The Vosk model directory is two levels up from NoteForge/NoteForge
    # __file__ is NoteForge/NoteForge/config_manager.py
    # os.path.dirname(__file__) is NoteForge/NoteForge
    # os.path.dirname(os.path.dirname(__file__)) is NoteForge
    # os.path.dirname(os.path.dirname(os.path.dirname(__file__))) is Exp (project root)
    vosk_model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "model")
    if os.path.exists(vosk_model_dir):
        try:
            shutil.rmtree(vosk_model_dir)
            print(f"Deleted Vosk model directory: {vosk_model_dir}")
            success_vosk = True
        except Exception as e:
            print(f"Error deleting Vosk model directory {vosk_model_dir}: {e}")
    else:
        print(f"Vosk model directory not found: {vosk_model_dir}")
        success_vosk = True # Consider it a success if it's not there to begin with

    # 2. Delete Whisper model cache for the specified (or current) model size
    if whisper_model_size_to_delete is None:
        whisper_model_size_to_delete = get_setting("whisper_model_size")
    
    whisper_cache_dir = get_whisper_cache_dir()
    
    # Whisper model files are typically named e.g., 'medium.pt', 'large.pt'
    model_filename = f"{whisper_model_size_to_delete}.pt"
    model_path = os.path.join(whisper_cache_dir, model_filename)

    if os.path.exists(model_path):
        try:
            os.remove(model_path)
            print(f"Deleted Whisper model file: {model_path}")
            success_whisper = True
        except Exception as e:
            print(f"Error deleting Whisper model file {model_path}: {e}")
    else:
        print(f"Whisper model file not found in cache: {model_path}")
        success_whisper = True # Consider it a success if it's not there

    return success_vosk and success_whisper

def download_models(progress_callback=None):
    """
    Ensures Vosk and Whisper models are present. Downloads them if not found.
    progress_callback: A function to call with (message, percentage) for UI updates.
    """
    
    # 1. Vosk Model Download
    # The Vosk model directory is two levels up from NoteForge/NoteForge
    vosk_model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "model")
    VOSK_MODEL_NAME = "vosk-model-en-us-0.22"
    VOSK_MODEL_URL = f"https://alphacephei.com/vosk/models/{VOSK_MODEL_NAME}.zip"

    print(f"DEBUG: Vosk model directory: '{vosk_model_dir}'")
    print(f"DEBUG: os.path.exists(vosk_model_dir): {os.path.exists(vosk_model_dir)}")
    if os.path.exists(vosk_model_dir):
        print(f"DEBUG: os.listdir(vosk_model_dir) is empty: {not bool(os.listdir(vosk_model_dir))}")

    if not os.path.exists(vosk_model_dir) or not os.listdir(vosk_model_dir):
        print(f"Vosk model not found at {vosk_model_dir} or directory is empty. Downloading...")
        if progress_callback:
            progress_callback("Downloading Vosk model...", 0.1)

        # Create the model directory if it doesn't exist
        os.makedirs(vosk_model_dir, exist_ok=True)

        zip_path = os.path.join(vosk_model_dir, f"{VOSK_MODEL_NAME}.zip")
        try:
            with requests.get(VOSK_MODEL_URL, stream=True) as r:
                r.raise_for_status()
                total_size_in_bytes = int(r.headers.get('content-length', 0))
                block_size = 8192 # 8 Kibibytes
                progress = 0
                with open(zip_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=block_size): 
                        if progress_callback and total_size_in_bytes > 0:
                            progress += len(chunk)
                            percentage = 0.1 + (progress / total_size_in_bytes) * 0.4 # Vosk is 10-50%
                            progress_callback(f"Downloading Vosk model... {int(percentage*100)}%", percentage)
                        f.write(chunk)
            
            if progress_callback:
                progress_callback("Extracting Vosk model...", 0.5)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Vosk models are usually in a subfolder with the model name, extract directly into vosk_model_dir
                for member in zip_ref.namelist():
                    if member.startswith(f"{VOSK_MODEL_NAME}/"):
                        # Extract the contents of the subfolder directly into vosk_model_dir
                        # Adjust member path to remove the leading model name folder
                        dest_path = os.path.join(vosk_model_dir, os.path.relpath(member, VOSK_MODEL_NAME))
                        if not os.path.exists(os.path.dirname(dest_path)):
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        if not member.endswith('/'): # Avoid creating directories for empty folders
                            with zip_ref.open(member) as source, open(dest_path, 'wb') as target:
                                shutil.copyfileobj(source, target)
            
            # Clean up the zip file after extraction
            os.remove(zip_path)
            print("Vosk model downloaded and extracted successfully.")
            if progress_callback:
                progress_callback("Vosk model ready.", 0.5)
        except Exception as e:
            print(f"Error downloading or extracting Vosk model: {e}")
            if progress_callback:
                progress_callback(f"Error downloading Vosk: {e}", 0.5)
            # Clean up partially downloaded/extracted files if an error occurs
            if os.path.exists(zip_path):
                os.remove(zip_path)
            if os.path.exists(vosk_model_dir) and not os.listdir(vosk_model_dir):
                shutil.rmtree(vosk_model_dir) # Remove empty dir if extraction failed
            return False # Indicate failure
    else:
        print("Vosk model already present.")
        if progress_callback:
            progress_callback("Vosk model ready.", 0.5)


    # 2. Whisper Model Download
    current_whisper_size = get_setting("whisper_model_size")
    whisper_cache_dir = get_whisper_cache_dir()
    
    # Check for both standard and versioned filenames for Whisper models
    potential_whisper_model_paths = [
        os.path.join(whisper_cache_dir, f"{current_whisper_size}.pt")
    ]
    if current_whisper_size == "large":
        potential_whisper_model_paths.append(os.path.join(whisper_cache_dir, f"{current_whisper_size}-v3.pt"))

    found_whisper_model_path = None
    for p in potential_whisper_model_paths:
        if os.path.exists(p):
            found_whisper_model_path = p
            break
            
    print(f"DEBUG: Whisper cache directory: '{whisper_cache_dir}'")
    print(f"DEBUG: Potential Whisper model paths: {potential_whisper_model_paths}")
    print(f"DEBUG: Found Whisper model path: '{found_whisper_model_path}'")

    if found_whisper_model_path is None:
        print(f"Whisper model '{current_whisper_size}' not found. Downloading...")
        if progress_callback:
            progress_callback(f"Downloading Whisper model '{current_whisper_size}'...", 0.6)
        try:
            # whisper.load_model automatically downloads if not present
            whisper.load_model(current_whisper_size, download_root=whisper_cache_dir)
            print(f"Whisper model '{current_whisper_size}' downloaded successfully.")
            print(f"DEBUG: Contents of Whisper cache directory '{whisper_cache_dir}' after download: {os.listdir(whisper_cache_dir)}")
            if progress_callback:
                progress_callback(f"Whisper model '{current_whisper_size}' ready.", 1.0)
        except Exception as e:
            print(f"Error downloading Whisper model '{current_whisper_size}': {e}")
            if progress_callback:
                progress_callback(f"Error downloading Whisper: {e}", 1.0)
            return False # Indicate failure
    else:
        print(f"Whisper model '{current_whisper_size}' already present at '{found_whisper_model_path}'.")
        if progress_callback:
            progress_callback(f"Whisper model '{current_whisper_size}' ready.", 1.0)
    
    return True # Indicate success

def clear_all_models():
    """
    Deletes all Vosk and Whisper models regardless of size.
    """
    print("Attempting to clear all models...")
    # Delete Vosk model (all versions if multiple existed, though currently only one is managed)
    vosk_model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "model")
    if os.path.exists(vosk_model_dir):
        try:
            shutil.rmtree(vosk_model_dir)
            print(f"Deleted Vosk model directory: {vosk_model_dir}")
        except Exception as e:
            print(f"Error deleting Vosk model directory {vosk_model_dir}: {e}")
    else:
        print(f"Vosk model directory not found at {vosk_model_dir}.")

    # Delete all Whisper models in the cache directory
    whisper_cache_dir = get_whisper_cache_dir()
    if os.path.exists(whisper_cache_dir):
        try:
            # Delete the entire cache directory for Whisper
            shutil.rmtree(whisper_cache_dir)
            print(f"Deleted Whisper cache directory: {whisper_cache_dir}")
        except Exception as e:
            print(f"Error deleting Whisper cache directory {whisper_cache_dir}: {e}")
    else:
        print(f"Whisper cache directory not found at {whisper_cache_dir}.")

    return True