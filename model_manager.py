# Wrapper for the new package-based model management system
import sys
import os

# Ensure src is in path for standalone execution/legacy imports
repo_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from noteforge.models.manager import ModelManager as NewModelManager

class ModelManager:
    """Compatibility wrapper for NewModelManager."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance

    def get_model(self, model_type, model_name, **kwargs):
        if model_type == 'vosk':
            return NewModelManager.get_vosk_model()
        elif model_type == 'whisper':
            return NewModelManager.get_whisper_model(model_name)
        elif model_type == 'bart':
            return NewModelManager.get_bart_pipeline()
        return None

    def unload_model(self, model_type, model_name):
        key = f"{model_type}_{model_name}" if model_type == "whisper" else model_type
        return NewModelManager.unload_model(key)

    def unload_all(self):
        return NewModelManager.unload_all()

def get_model_manager():
    return ModelManager()
