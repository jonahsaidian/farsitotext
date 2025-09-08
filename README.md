# Farsi Audio Transcriber

A Streamlit app that transcribes Farsi (Persian) audio to text using OpenAI's API. Large files are processed reliably by chunking audio into segments.

## Project Structure

```
farsi_to_text/
├── ui/
│   ├── app.py          # Streamlit UI application
│   └── __init__.py
├── api/
│   ├── transcriber.py  # API logic for transcription (chunking + per-chunk transcription)
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

3. Set your OpenAI API key (via environment variable):
```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# macOS/Linux
export OPENAI_API_KEY=your_api_key_here
```

## Running the App

### Streamlit App
```bash
streamlit run ui/app.py
```

## Features

- **Streamlit UI**: Modern, clean interface
- **Auto API Key**: Automatically loads from environment variables
- **File Upload**: Drag-and-drop audio file selection
- **Progress Tracking**: Real-time progress with time estimates
- **Chunked Processing**: Processes large files by 200s chunks for reliability
- **Text Export**: Save transcribed text as .txt file
- **Restart**: One-click full reset to initial state

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
- Environment variables are read from the OS. If you prefer a `.env` file, you can install `python-dotenv` and load it at app start.

## Build a self-contained .exe (Windows, PyInstaller)

1. Place `ffmpeg.exe` and `ffprobe.exe` in an `ffmpeg/` folder at repo root (same level as `run.py`).
2. Build the executable:
```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile \
  --add-binary "ffmpeg\\ffmpeg.exe;ffmpeg" \
  --add-binary "ffmpeg\\ffprobe.exe;ffmpeg" \
  run.py
```

3. Distribute the single exe from `dist/run.exe`. The app will auto-open the browser to `http://localhost:8501`.

Notes:
- `run.py` starts Streamlit programmatically and configures pydub to use the bundled FFmpeg binaries when frozen.
- For macOS/Linux, adjust binary names accordingly and consider `--windowed` or platform-specific bundlers.
