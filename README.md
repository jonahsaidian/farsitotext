# Farsi Audio Transcriber

A Streamlit app that transcribes Farsi (Persian) audio to text using OpenAI's API. Large files are processed reliably by chunking audio into segments. After transcription, the text is post-processed by OpenAI to fix minor grammar, spelling, and syntax issues (without changing meaning).

## Project Structure

```
farsi_to_text/
├── ui/
│   ├── app.py          # Streamlit UI application
│   └── __init__.py
├── api/
│   ├── transcriber.py  # API logic for transcription (chunking + per-chunk transcription + post-processing)
│   └── __init__.py
├── requirements.txt    # Python dependencies
└── README.md
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install FFmpeg (required by pydub for MP3/MP4, etc.)
   - Windows: download from `https://ffmpeg.org/download.html`, extract, and add the `bin` folder to PATH
   - macOS (Homebrew): `brew install ffmpeg`
   - Linux: use your package manager, e.g. `sudo apt-get install ffmpeg`

3. Set your OpenAI API key (via environment variable or .env file):
```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# macOS/Linux
export OPENAI_API_KEY=your_api_key_here
```
Or create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_api_key_here
```

## Running the App

### Streamlit App
```bash
streamlit run ui/app.py
```

## Features

- **Streamlit UI**: Modern, clean interface
- **Auto API Key**: Automatically loads from environment variables or .env file
- **File Upload**: Drag-and-drop audio file selection (MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM)
- **Progress Tracking**: Real-time progress with time estimates and live transcription display
- **Chunked Processing**: Processes large files by 200s chunks for reliability
- **Text Export**: Save transcribed text as .txt file
- **Restart**: One-click full reset to initial state (clears file uploader and all state)
- **Post-processing**: After transcription, text is sent to OpenAI (gpt-4o) for minor grammar, spelling, and syntax fixes (no summarization or content change)
- **Robust Error Handling**: Any error in transcription or post-processing is clearly shown, and the user can always restart cleanly

## Supported Audio Formats

- MP3
- MP4
- MPEG
- MPGA
- M4A
- WAV
- WEBM

## Notes

- FFmpeg must be installed and on PATH for `pydub` to read non-WAV formats like MP3 and MP4.
- Time estimates are heuristic:
  - Loading estimate ≈ 60 seconds per 100 MB (rounded to nearest 5s)
  - Transcription estimate ≈ ~1 minute per remaining chunk
- Environment variables are read from the OS or a `.env` file (using `python-dotenv`).
- Uses OpenAI's `gpt-4o-transcribe` for audio and `gpt-4o` for post-processing.
- The file uploader is fully reset on restart, so you can upload a new file after any error or completion.
