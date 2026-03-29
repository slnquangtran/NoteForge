import json
import numpy as np
import torch
from ..models.manager import ModelManager

class TranscriptionEngine:
    """Orchestrates Vosk and Whisper for hybrid transcription."""
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self._vosk_model = None
        self._whisper_model = None

    def get_vosk_recognizer(self):
        import vosk
        if not self._vosk_model:
            self._vosk_model = ModelManager.get_vosk_model()
        return vosk.KaldiRecognizer(self._vosk_model, self.sample_rate)

    def transcribe_whisper(self, audio_bytes, model_size=None):
        """Runs Whisper transcription on a chunk of audio."""
        if not self._whisper_model:
            self._whisper_model = ModelManager.get_whisper_model(model_size)
            
        # Convert bytes to float32 numpy array
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Determine device
        device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
        use_fp16 = (device == "cuda")
        
        result = self._whisper_model.transcribe(
            audio_np, 
            fp16=use_fp16, 
            language="english",
            beam_size=1,
            best_of=1
        )
        return result.get("text", "").strip()
