import json
import os
from .paths import get_config_file

DEFAULT_SETTINGS = {
    "whisper_model_size": "base",
    "bart_model_name": "facebook/bart-large-cnn",
}

def load_settings():
    config_file = get_config_file()
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            try:
                settings = json.load(f)
                return {**DEFAULT_SETTINGS, **settings}
            except json.JSONDecodeError:
                return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_settings(settings):
    config_file = get_config_file()
    with open(config_file, "w") as f:
        json.dump(settings, f, indent=4)

def get_setting(key, default=None):
    settings = load_settings()
    if key == "whisper_model_size":
        val = settings.get(key, DEFAULT_SETTINGS.get(key))
        if val not in ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]:
            return "base"
        return val
    return settings.get(key, default if default is not None else DEFAULT_SETTINGS.get(key))

def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
