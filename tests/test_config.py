import os
import sys

# Ensure src is in python path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from noteforge import config

def test_settings_get_set():
    # Test setting a value
    config.set("test_key", "test_value")
    assert config.get("test_key") == "test_value"
    
    # Test default value
    assert config.get("non_existent_key", "default") == "default"

if __name__ == "__main__":
    try:
        test_settings_get_set()
        print("test_config.py: PASSED")
    except Exception as e:
        print(f"test_config.py: FAILED - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
