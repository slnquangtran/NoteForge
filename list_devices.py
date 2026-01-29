import speech_recognition as sr

def list_microphones():
    print("Searching for microphones...")
    mics = sr.Microphone.list_microphone_names()
    
    if not mics:
        print("No microphones found.")
        return

    print(f"Found {len(mics)} devices:")
    for i, mic_name in enumerate(mics):
        print(f"[{i}] {mic_name}")

if __name__ == "__main__":
    try:
        list_microphones()
    except Exception as e:
        print(f"Error listing microphones: {e}")
