import os
import shutil
import zipfile
import requests
from ..config.paths import get_vosk_model_dir, get_whisper_cache_dir
from ..config.settings import get_setting
from .registry import VOSK_MODEL_NAME, VOSK_MODEL_URL

def download_vosk(progress_callback=None):
    """Ensures Vosk model is present. Downloads if not found."""
    vosk_model_dir = get_vosk_model_dir()
    
    if os.path.exists(vosk_model_dir) and os.listdir(vosk_model_dir):
        return True

    os.makedirs(vosk_model_dir, exist_ok=True)
    zip_path = os.path.join(vosk_model_dir, f"{VOSK_MODEL_NAME}.zip")
    
    try:
        if progress_callback:
            progress_callback("Downloading Vosk model...", 0.1)
            
        with requests.get(VOSK_MODEL_URL, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            progress = 0
            with open(zip_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    if progress_callback and total_size > 0:
                        progress += len(chunk)
                        percentage = 0.1 + (progress / total_size) * 0.4
                        progress_callback(f"Downloading Vosk model... {int(percentage*100)}%", percentage)

        if progress_callback:
            progress_callback("Extracting Vosk model...", 0.5)
            
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if member.startswith(f"{VOSK_MODEL_NAME}/"):
                    dest_path = os.path.join(vosk_model_dir, os.path.relpath(member, VOSK_MODEL_NAME))
                    if not os.path.exists(os.path.dirname(dest_path)):
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    if not member.endswith('/'):
                        with zip_ref.open(member) as source, open(dest_path, 'wb') as target:
                            shutil.copyfileobj(source, target)
        
        os.remove(zip_path)
        return True
    except Exception as e:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        print(f"Error downloading Vosk: {e}")
        return False

def download_whisper(model_size=None, progress_callback=None):
    """Ensures Whisper model is present."""
    try:
        import whisper
    except ImportError:
        return False
        
    if model_size is None:
        model_size = get_setting("whisper_model_size")
    
    cache_dir = get_whisper_cache_dir()
    try:
        if progress_callback:
            progress_callback(f"Downloading Whisper model '{model_size}'...", 0.6)
        whisper.load_model(model_size, download_root=cache_dir)
        return True
    except Exception as e:
        print(f"Error downloading Whisper: {e}")
        return False

def download_bart(progress_callback=None):
    """Ensures BART model is present."""
    try:
        from transformers import pipeline
    except ImportError:
        return False
        
    model_name = get_setting("bart_model_name")
    try:
        if progress_callback:
            progress_callback(f"Downloading BART model...", 0.9)
        pipeline("summarization", model=model_name)
        return True
    except Exception as e:
        print(f"Error downloading BART: {e}")
        return False

def delete_all_models():
    """Clears all local models and caches."""
    shutil.rmtree(get_vosk_model_dir(), ignore_errors=True)
    shutil.rmtree(get_whisper_cache_dir(), ignore_errors=True)
    try:
        from huggingface_hub import constants
        shutil.rmtree(constants.HF_HUB_CACHE, ignore_errors=True)
    except:
        pass
    return True
