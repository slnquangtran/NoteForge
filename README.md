# Hybrid Voice Transcriber (Vosk + Whisper)

A high-performance real-time voice transcription application that combines **Vosk** (for low-latency streaming) and **OpenAI Whisper** (for high-accuracy correction). Features a modern dark-mode UI built with `customtkinter`.

![Screenshot](screenshot.png)

## Features

-   **Hybrid Architecture**:
    -   **Real-time**: Instant text display using Vosk Streaming (<100ms latency).
    -   **Accuracy**: Automatic background correction using Whisper (OpenAI) when you pause.
-   **Voice Activity Detection (VAD)**: Uses `webrtcvad` to precisely detect speech and trigger corrections.
-   **Pro Audio Pipeline**:
    -   Noise Reduction (`noisereduce`)
    -   Dynamic Gain Normalization
    -   16kHz Sample Rate optimization
-   **Modern UI**: Dark mode, audio level meter, transparency control, and "Always on Top" mode.
-   **Offline Capable**: Runs completely locally (after model download).

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/Voice-transcriber.git
    cd Voice-transcriber
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: You may need to install [PyTorch](https://pytorch.org/) manually if you want GPU acceleration for Whisper.*

3.  **Download Models**:
    Run the included helper script to download the Vosk model (~50MB):
    ```bash
    python tools/download_models.py
    ```
    *Whisper model will be downloaded automatically on first run.*

## Usage

1.  Run the application:
    ```bash
    python app.py
    ```
2.  Select your Microphone from the dropdown.
3.  Click **"Start Recording"**.
4.  Speak naturally. Gray text will appear instantly; it will turn black/white when refined by Whisper.

## Requirements

-   Python 3.8+
-   Windows/Linux/macOS
-   Internet connection (only for initial model download)

## Tech Stack

-   **GUI**: `customtkinter`
-   **Audio**: `pyaudio`, `sounddevice`, `webrtcvad`
-   **AI Engines**: `vosk`, `openai-whisper`
-   **Processing**: `numpy`, `noisereduce`

## License

MIT License