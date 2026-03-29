# Wrapper for the new package-based study system
import sys
import os

# Ensure src is in path for standalone execution/legacy imports
repo_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(repo_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from noteforge.study.generator import StudyGenerator
from noteforge.study.exporter import export_to_pdf

class LectureNoteGenerator:
    """Compatibility wrapper for StudyGenerator."""
    def __init__(self):
        self.generator = StudyGenerator()

    def process_file(self, filepath, progress_callback=None):
        return self.generator.process_file(filepath, progress_callback)

    def export_to_pdf(self, processed_data, output_path):
        if isinstance(processed_data, dict):
            notes = processed_data.get("notes", "")
        else:
            notes = processed_data
        return export_to_pdf(notes, output_path)

# For backward compatibility
ConceptualAssistant = LectureNoteGenerator
