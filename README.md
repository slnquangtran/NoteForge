# NoteForge

**Smart Note Creation: Real-Time Transcription & Intelligent Note Summarization**

NoteForge is a powerful dual-purpose application that combines real-time voice transcription with AI-powered note summarization. Perfect for students, professionals, and anyone who needs to capture and organize spoken content into study-ready notes.

## Features

### Real-Time Transcription
- **Hybrid AI Architecture**: Combines Vosk (instant streaming) + Whisper (high accuracy)
- **Voice Activity Detection**: Precise speech detection using WebRTC VAD
- **Professional Audio Processing**:
  - Noise reduction
  - Dynamic gain normalization
  - 16kHz optimized sample rate
- **Modern UI**: Dark mode, audio level meter, always-on-top mode
- **Offline Capable**: Runs completely locally after initial setup

### Note Summarization
- **Semantic Topic Extraction**: Automatically organizes content by topics
- **Legal Content Recognition**: Detects case law, legal principles, and doctrines
- **Smart Classification**: Categorizes content into:
  - Definitions
  - Legal Rules & Principles
  - Key Cases (with citations)
  - Exceptions & Special Rules
  - Practical Examples
- **Multiple Input Formats**: Supports both text transcripts (.txt) and PowerPoint (.pptx)
- **Study-Ready Output**: Generates structured lecture notes organized by topic
- **PDF Export**: Save your notes as professional PDFs

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/slnquangtran/NoteForge.git
cd NoteForge
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```



### 3. Download Models
Run the helper script to download the Vosk model (~50MB):
```bash
python tools/download_models.py
```

The Whisper model will download automatically on first use.

## Usage

### Launch NoteForge
```bash
python main.py
```
