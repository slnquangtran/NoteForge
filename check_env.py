import speech_recognition as sr
import sys

print(f"Python: {sys.version}")
try:
    import pyaudio
    print(f"PyAudio detected: {pyaudio.__version__}")
except ImportError:
    print("PyAudio NOT installed")

print(f"SpeechRecognition version: {sr.__version__}")

try:
    mics = sr.Microphone.list_microphone_names()
    print(f"Microphones found: {len(mics)}")
    for i, m in enumerate(mics):
        print(f"{i}: {m}")
except Exception as e:
    print(f"Error listing mics: {e}")
