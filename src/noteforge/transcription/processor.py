try:
    import webrtcvad
    webrtcvad_available = True
except ImportError:
    webrtcvad_available = False

class VADProcessor:
    """Handles Voice Activity Detection."""
    def __init__(self, sample_rate=16000, aggressiveness=2):
        self.sample_rate = sample_rate
        if webrtcvad_available:
            self.vad = webrtcvad.Vad(aggressiveness)
        else:
            self.vad = None

    def is_speech(self, frame_bytes):
        """Returns True if speech is detected in the frame."""
        if not self.vad:
            return False
        try:
            return self.vad.is_speech(frame_bytes, self.sample_rate)
        except Exception:
            return False
