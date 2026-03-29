import os
import sys

# Ensure src is in python path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from noteforge.models.manager import ModelManager
from noteforge.models.registry import VOSK_MODEL_URL

def test_model_registry():
    assert VOSK_MODEL_URL.startswith("https://")
    
def test_manager_unload():
    # Smoke test for unload logic
    assert ModelManager.unload_model("non_existent") == False

if __name__ == "__main__":
    try:
        test_model_registry()
        test_manager_unload()
        print("test_models.py: PASSED")
    except Exception as e:
        print(f"test_models.py: FAILED - {e}")
        sys.exit(1)
