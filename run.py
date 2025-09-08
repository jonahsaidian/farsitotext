import os
import sys
import threading
import webbrowser

# Configure pydub/ffmpeg paths when frozen by PyInstaller
try:
	from pydub import AudioSegment
	base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
	ffmpeg_dir = os.path.join(base_path, "ffmpeg")
	ffmpeg_bin = os.path.join(ffmpeg_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")
	ffprobe_bin = os.path.join(ffmpeg_dir, "ffprobe.exe" if os.name == "nt" else "ffprobe")
	if os.path.exists(ffmpeg_bin) and os.path.exists(ffprobe_bin):
		AudioSegment.converter = ffmpeg_bin
		AudioSegment.ffprobe = ffprobe_bin
except Exception:
	# If pydub/ffmpeg not present, continue; Streamlit UI will surface errors as needed
	pass

# Streamlit programmatic bootstrap
from streamlit.web import bootstrap  # type: ignore

APP_PATH = os.path.join(os.path.dirname(__file__), "ui", "app.py")


def _open_browser_when_ready():
	# Give the server a moment to start, then open browser to the default port
	import time
	time.sleep(1.5)
	try:
		webbrowser.open("http://localhost:8501", new=2)
	except Exception:
		pass


def main() -> None:
	# Optional Streamlit environment tweaks
	os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")
	os.environ.setdefault("STREAMLIT_SERVER_HEADLESS", "false")

	# Open browser shortly after starting server
	threading.Thread(target=_open_browser_when_ready, daemon=True).start()

	# Run Streamlit app
	# args: (file, command_line, args, flag_options)
	bootstrap.run(APP_PATH, "streamlit run", [], {})


if __name__ == "__main__":
	main()
