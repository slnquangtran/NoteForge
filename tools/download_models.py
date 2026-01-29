import os
import requests
import zipfile
import shutil
from tqdm import tqdm

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
MODEL_ZIP = "model.zip"
MODEL_DIR = "model"

def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

def setup_vosk_model():
    if os.path.exists(MODEL_DIR):
        print(f"Model directory '{MODEL_DIR}' already exists. Skipping download.")
        return

    print("Downloading Vosk model...")
    download_file(MODEL_URL, MODEL_ZIP)
    
    print("Extracting model...")
    with zipfile.ZipFile(MODEL_ZIP, 'r') as zip_ref:
        zip_ref.extractall(".")
    
    # Rename the extracted folder to 'model'
    # The zip usually contains a folder named "vosk-model-small-en-us-0.15"
    extracted_folder = "vosk-model-small-en-us-0.15"
    if os.path.exists(extracted_folder):
        os.rename(extracted_folder, MODEL_DIR)
        print(f"Model setup complete. Renamed '{extracted_folder}' to '{MODEL_DIR}'.")
    else:
        print(f"Warning: Expected folder '{extracted_folder}' not found. Please check the extracted contents.")

    # Cleanup
    if os.path.exists(MODEL_ZIP):
        os.remove(MODEL_ZIP)

if __name__ == "__main__":
    setup_vosk_model()
