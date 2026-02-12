# Changelog

## [1.1.0] - 2026-02-09

### ✨ New Features
- **AI-Powered Note Summarization**: Integrated **BART (Large-CNN)** model for semantic topic extraction and automatic summarization of lecture notes.
- **Modern Premium UI**: Implemented a card-based glassmorphism layout with high-radius corners (25px) and a curated dark-mode palette (`#312C51`, `#48426D`, `#F0C38E`).
- **Automatic Session Export**: Every recording session now automatically saves:
    - High-quality audio: `recordings/recording_YYYYMMDD_HHMMSS.wav`
    - Full transcription: `recordings/transcript_YYYYMMDD_HHMMSS.txt`
- **Dynamic Level Meter**: Added a real-time audio volume visualizer to the main dashboard.

### 🚀 Performance & Hardware
- **Turbo Transcription Architecture**:
    - **NVIDIA CUDA**: Auto-detects and utilizes NVIDIA GPUs for lightning-fast Whisper inference.
    - **Apple Silicon (MPS)**: Auto-detects and utilizes Metal Performance Shaders for optimized Mac performance.
- **Snappier Streaming**: Reduced Vosk batching from 10 frames to 5 frames (100ms) for near-instant "Draft" updates as you speak.
- **Inference Tuning**: Optimized Whisper parameters (`beam_size=1`, `fp16=True`) to prioritize real-time response times.

### 🍎 macOS Compatibility
- **Pinned Requirements**: Optimized `requirements.txt` to pin `vosk==0.3.44` for system stability on Mac.
- **Build Stabilization**: Switched to `webrtcvad-wheels` to prevent common "Failed to build wheel" compilation errors.
- **Homebrew Integration**: Updated README with prerequisites for Mac users (PortAudio, Brew).

### 🛠️ Bug Fixes
- **Initialization Hang**: Resolved a critical issue where the app would hang indefinitely on "Initializing Whisper."
- **UI Thread Stability**: Added global error handling to the UI update loop to prevent freezes on status updates.
- **Scaling TypeError**: Fixed a font-scaling crash caused by invalid font fallback tuples on modern high-DPI displays.
- **Audio Capture Hook**: Restored missing `sd.InputStream` logic that caused audio silence.

---
*NoteForge v1.1.0 - Building better notes together.*
