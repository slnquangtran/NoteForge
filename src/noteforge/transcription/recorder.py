import sounddevice as sd
import numpy as np
import threading

class AudioRecorder:
    """Handles audio device enumeration and stream capture."""
    def __init__(self, sample_rate=16000, frame_duration_ms=20):
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        self.frame_bytes = self.frame_size * 2
        self.is_recording = False
        self.stream = None
        self.selected_device = None

    @staticmethod
    def get_devices():
        """Returns a list of available input devices: (index, display_name)."""
        devices_list = []
        try:
            default_input_index = sd.default.device[0]
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    name = dev['name']
                    is_def = " (Default)" if i == default_input_index else ""
                    devices_list.append((i, f"{i}: {name}{is_def}"))
        except Exception as e:
            print(f"Error getting audio devices: {e}")
            devices_list = [(None, "Default Device")]
        return devices_list

    def start(self, device_index, callback):
        """Starts the capture thread."""
        self.selected_device = device_index
        self.is_recording = True
        
        def audio_thread():
            try:
                with sd.InputStream(samplerate=self.sample_rate,
                                    blocksize=self.frame_size,
                                    device=self.selected_device,
                                    channels=1,
                                    dtype='int16') as stream:
                    self.stream = stream
                    while self.is_recording:
                        indata, overflowed = stream.read(self.frame_size)
                        # indata is numpy array (frame_size, 1)
                        callback(indata)
            except Exception as e:
                print(f"Recorder Error: {e}")
                self.is_recording = False

        t = threading.Thread(target=audio_thread, daemon=True)
        t.start()
        return t

    def stop(self):
        """Stops the capture."""
        self.is_recording = False
        self.stream = None
