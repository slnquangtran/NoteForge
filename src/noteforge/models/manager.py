import torch
import gc
from .downloader import download_vosk, download_whisper, download_bart
from ..config.settings import get_setting

class ModelManager:
    """Manages runtime loading and caching of AI models."""
    _instances = {}

    @classmethod
    def get_vosk_model(cls):
        if "vosk" not in cls._instances:
            from vosk import Model
            from ..config.paths import get_vosk_model_dir
            download_vosk()
            cls._instances["vosk"] = Model(get_vosk_model_dir())
        return cls._instances["vosk"]

    @classmethod
    def get_whisper_model(cls, size=None):
        if size is None:
            size = get_setting("whisper_model_size")
        
        key = f"whisper_{size}"
        if key not in cls._instances:
            import whisper
            from ..config.paths import get_whisper_cache_dir
            download_whisper(size)
            cls._instances[key] = whisper.load_model(size, download_root=get_whisper_cache_dir())
        return cls._instances[key]

    @classmethod
    def get_bart_pipeline(cls):
        if "bart" not in cls._instances:
            from transformers import pipeline
            model_name = get_setting("bart_model_name")
            download_bart()
            
            # Device detection
            device = -1 # CPU
            if torch.cuda.is_available():
                device = 0
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                device = "mps"
            
            cls._instances["bart"] = pipeline("summarization", model=model_name, device=device)
        return cls._instances["bart"]

    @classmethod
    def unload_model(cls, key):
        if key in cls._instances:
            del cls._instances[key]
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                if hasattr(torch, "mps"):
                    torch.mps.empty_cache()
            return True
        return False

    @classmethod
    def unload_all(cls):
        cls._instances.clear()
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return True
