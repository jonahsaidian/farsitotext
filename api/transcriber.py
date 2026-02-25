"""
API module for Farsi audio transcription using OpenAI.
"""

import os
import subprocess
import tempfile

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_audio_duration_ms(file_path: str) -> int:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return int(float(result.stdout.strip()) * 1000)


def chunk_audio(file_path: str, chunk_duration_ms: int = 30000):
    """
    Generator that yields temp wav file paths for each chunk of the audio file.
    Uses ffmpeg to cut chunks directly from disk — no full PCM load into memory.
    Each yielded path should be deleted by the caller after use.
    """
    duration_ms = get_audio_duration_ms(file_path)

    for start_ms in range(0, duration_ms, chunk_duration_ms):
        chunk_ms = min(chunk_duration_ms, duration_ms - start_ms)
        start_s = start_ms / 1000.0
        duration_s = chunk_ms / 1000.0

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp_path = tmp.name

        subprocess.run(
            [
                "ffmpeg",
                "-ss",
                str(start_s),
                "-i",
                file_path,
                "-t",
                str(duration_s),
                "-ar",
                "16000",
                "-ac",
                "1",
                "-y",
                tmp_path,
            ],
            capture_output=True,
            check=True,
        )
        yield tmp_path


def transcribe_audio_segment(file_path: str, api_key: str) -> str:
    """
    Transcribe a single audio file using OpenAI's API.

    Args:
        file_path (str): Path to the audio file (wav)
        api_key (str): OpenAI API key

    Returns:
        str: Transcribed text
    """
    with open(file_path, "rb") as audio_file:
        client = OpenAI(api_key=api_key)
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file,
            language="fa",
            prompt="You are a farsi language expert. Please transcribe the following audio in farsi, output should be farsi text with appropriate line breaks and grammar as needed.",
        )
        return transcription.text


def transcribe_audio(file_path: str, api_key: str) -> str:
    """
    Transcribe Farsi audio file using OpenAI's API with chunking support.

    Args:
        file_path (str): Path to the audio file
        api_key (str): OpenAI API key

    Returns:
        str: Transcribed text

    Raises:
        AuthenticationError: If API key is invalid
        Exception: For other transcription errors
    """
    transcribed_texts = []
    for i, chunk_path in enumerate(chunk_audio(file_path, chunk_duration_ms=30000)):
        try:
            chunk_text = transcribe_audio_segment(chunk_path, api_key)
            if chunk_text.strip():
                transcribed_texts.append(chunk_text)
        except Exception as e:
            print(f"Error transcribing chunk {i}: {e}")
        finally:
            try:
                os.unlink(chunk_path)
            except OSError:
                pass

    # Combine all transcribed text
    return " ".join(transcribed_texts)


def postprocess_transcription(transcribed_text: str, api_key: str) -> str:
    """
    Calls OpenAI to return the transcribed text with minor grammar, spelling, and syntax fixes only.
    The model should not attempt to modify the text beyond that.
    """
    client = OpenAI(api_key=api_key)
    prompt = (
        "You are a helpful assistant and expert in the Farsi language. "
        "Below is an audio recording of a person speaking Farsi that has been transcribed into text via a chunking strategy. "
        "Given the following transcribed text, return it with only minor fixes for grammar, spelling, and syntax. "
        "Do not change the meaning, do not summarize, and do not modify the text beyond these minor corrections. "
        "If it seems like the transcription is incomplete, return the incomplete text as is. Do not add words that seem like they should be there. "
        "Return only the corrected text, do not include any other text or commentary, only return the farsi text."
    )
    response = client.responses.create(
        model="gpt-4o",
        input=transcribed_text,
        instructions=prompt,
    )
    return response.output_text


def get_default_api_key() -> str:
    """
    Get API key from environment variables.

    Returns:
        str: API key from environment or empty string
    """
    return os.environ.get("OPENAI_API_KEY", "")
