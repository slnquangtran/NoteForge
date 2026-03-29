import os
import sys

# Ensure src is in python path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from noteforge.study import StudyGenerator

def test_generator_init():
    gen = StudyGenerator()
    assert gen.topic_keywords is not None

if __name__ == "__main__":
    try:
        test_generator_init()
        print("test_study.py: PASSED")
    except Exception as e:
        print(f"test_study.py: FAILED - {e}")
        sys.exit(1)
