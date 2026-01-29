# ⚡ NoteForge

**Smart Note Creation: Real-Time Transcription & Intelligent Note Summarization**

NoteForge is a powerful dual-purpose application that combines real-time voice transcription with AI-powered note summarization. Perfect for students, professionals, and anyone who needs to capture and organize spoken content into study-ready notes.

![NoteForge](screenshot.png)

## 🎯 Features

### 🎤 Real-Time Transcription
- **Hybrid AI Architecture**: Combines Vosk (instant streaming) + Whisper (high accuracy)
- **Voice Activity Detection**: Precise speech detection using WebRTC VAD
- **Professional Audio Processing**:
  - Noise reduction
  - Dynamic gain normalization
  - 16kHz optimized sample rate
- **Modern UI**: Dark mode, audio level meter, always-on-top mode
- **Offline Capable**: Runs completely locally after initial setup

### 📝 Note Summarization
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

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/slnquangtran/Voice-transcriber.git
cd Voice-transcriber
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: For GPU acceleration with Whisper, install [PyTorch](https://pytorch.org/) manually.

### 3. Download Models
Run the helper script to download the Vosk model (~50MB):
```bash
python tools/download_models.py
```

The Whisper model will download automatically on first use.

## 🚀 Usage

### Launch NoteForge
```bash
python main.py
```

### Real-Time Transcription
1. Click **"Real-Time Transcription"**
2. Select your microphone from the dropdown
3. Click **"Start Recording"**
4. Speak naturally - instant text appears (gray), then refines to high accuracy (white)
5. Export your transcript when done

<<<<<<< HEAD
### Note Summarization
1. Click **"Note Summarization"**
2. Load a transcript (.txt) or PowerPoint (.pptx)
3. Click **"Generate Lecture Notes"**
4. Get organized, topic-based study notes
5. Export to PDF or save as text

## 📋 Example Output

### Note Summarization Output
```
======================================================================
TOPIC: CONSIDERATION
======================================================================

DEFINITIONS:
• Consideration = price paid for a promise
• Something of value in the eyes of the law

LEGAL RULES & PRINCIPLES:
• Must be sufficient but need not be adequate
• Past consideration generally invalid
• Performance of existing duty = no consideration

KEY CASES:
• Stilk v Myrick (1809): Existing duty rule
• Williams v Roffey Bros (1990): Practical benefit exception
• Pao On v Lau Yiu Long: Past consideration exception

EXCEPTIONS & SPECIAL RULES:
• Practical benefit doctrine (Williams)
• Pao On exception for past consideration
```

## 🛠️ Tech Stack

### Core Technologies
- **GUI Framework**: CustomTkinter
- **Audio Processing**: PyAudio, SoundDevice, WebRTC VAD
- **AI Engines**: Vosk, OpenAI Whisper
- **Document Processing**: python-pptx, ReportLab
- **NLP**: NLTK

### Key Libraries
- `customtkinter` - Modern UI components
- `vosk` - Real-time speech recognition
- `openai-whisper` - High-accuracy transcription
- `python-pptx` - PowerPoint extraction
- `reportlab` - PDF generation
- `nltk` - Natural language processing
- `webrtcvad` - Voice activity detection
- `noisereduce` - Audio noise reduction

## 💡 Use Cases

- **Students**: Record lectures and generate organized study notes
- **Legal Professionals**: Transcribe meetings and extract case references
- **Researchers**: Convert interviews into structured summaries
- **Content Creators**: Transcribe videos/podcasts for content repurposing
- **Business**: Meeting transcription and action item extraction

## 📝 Requirements

- Python 3.8+
- Windows/Linux/macOS
- Microphone (for transcription)
- Internet connection (only for initial model download)

## 🎓 Perfect For

- Law students studying case law
- Medical students organizing lecture content
- Business students processing case studies
- Anyone who needs to convert spoken content into organized notes

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🐛 Issues

Found a bug? Please open an issue on GitHub with:
- Description of the problem
- Steps to reproduce
- Expected vs actual behavior

## ⭐ Support

If you find NoteForge useful, please consider giving it a star on GitHub!

---

**Built with ❤️ for students and professionals who value organized, accessible knowledge**
=======
MIT License
>>>>>>> a547eedc0c46e73dd21ba88bf66e9bc794ec3f64
