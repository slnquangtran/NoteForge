import os
import sys

# Ensure src is in python path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from noteforge.transcription import TranscriptionEngine

def test_engine_init():
    # Just check if we can import and instantiate (partially)
    assert TranscriptionEngine is not None

if __name__ == "__main__":
    try:
        test_engine_init()
        print("test_transcription.py: PASSED")
    except Exception as e:
        print(f"test_transcription.py: FAILED - {e}")
        sys.exit(1)
