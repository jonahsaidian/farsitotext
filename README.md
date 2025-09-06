# Farsi Audio Transcriber

A simple tool to transcribe Farsi (Persian) audio to text using OpenAI's API.

## Project Structure

```
farsi_to_text/
├── ui/
│   ├── app.py          # Streamlit UI application
│   └── __init__.py
├── api/
│   ├── transcriber.py  # API logic for transcription
│   └── __init__.py
├── main.py             # Original Tkinter app (legacy)
├── requirements.txt    # Python dependencies
└── README.md
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your OpenAI API key (optional):
```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# macOS/Linux
export OPENAI_API_KEY=your_api_key_here
```

## Running the App

### Streamlit Version (Recommended)
```bash
streamlit run ui/app.py
```

### Original Tkinter Version
```bash
python main.py
```

## Features

- **Streamlit UI**: Modern, clean interface
- **Auto API Key**: Automatically loads from environment variables
- **File Upload**: Drag-and-drop audio file selection
- **Progress Tracking**: Real-time transcription progress
- **Text Export**: Save transcribed text as .txt file
- **Start Over**: Easy reset for new files

## Supported Audio Formats

- MP3
- MP4
- MPEG
- MPGA
- M4A
- WAV
- WEBM
