import pyaudio

p = pyaudio.PyAudio()

print("--- Default Input Device ---")
try:
    default_info = p.get_default_input_device_info()
    print(f"Name: {default_info['name']}")
    print(f"Index: {default_info['index']}")
except Exception as e:
    print(f"Error getting default: {e}")

print("\n--- All Input Devices ---")
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        dev = p.get_device_info_by_host_api_device_index(0, i)
        print(f"Input Device id {i} - {dev.get('name')} (Channels: {dev.get('maxInputChannels')})")
    else:
        # Just to see what we are skipping
        # dev = p.get_device_info_by_host_api_device_index(0, i)
        # print(f"Skipping id {i} - {dev.get('name')} (Channels: 0)")
        pass

p.terminate()
