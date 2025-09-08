"""
API module for Farsi audio transcription using OpenAI.
"""
from openai import OpenAI, AuthenticationError
import os
import tempfile
from pydub import AudioSegment


def chunk_audio(audio_segment: AudioSegment, chunk_duration_ms: int = 30000) -> list:
    """
    Chunk an AudioSegment into smaller segments.
    
    Args:
        audio_segment (AudioSegment): The audio segment to chunk
        chunk_duration_ms (int): Duration of each chunk in milliseconds (default: 30 seconds)
        
    Returns:
        list: List of AudioSegment chunks
    """
    chunks = []
    total_duration = len(audio_segment)
    
    for start_time in range(0, total_duration, chunk_duration_ms):
        end_time = min(start_time + chunk_duration_ms, total_duration)
        chunk = audio_segment[start_time:end_time]
        chunks.append(chunk)
    
    return chunks


def transcribe_audio_segment(audio_segment: AudioSegment, api_key: str) -> str:
    """
    Transcribe a single AudioSegment using OpenAI's API.
    
    Args:
        audio_segment (AudioSegment): The audio segment to transcribe
        api_key (str): OpenAI API key
        
    Returns:
        str: Transcribed text
    """
    # Save AudioSegment to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        audio_segment.export(tmp_file.name, format="wav")
        tmp_file_path = tmp_file.name
    
    try:
        with open(tmp_file_path, "rb") as audio_file:
            client = OpenAI(api_key=api_key)
            transcription = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file,
                language="fa",
                prompt="You are a farsi language expert. Please transcribe the following audio in farsi, output should be farsi text with appropriate line breaks and grammar as needed."
            )
            return transcription.text
    finally:
        try:
            os.unlink(tmp_file_path)
        except OSError:
            pass


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
    # Load audio file with pydub
    audio_segment = AudioSegment.from_file(file_path)
    
    # Chunk the audio (30-second chunks)
    chunks = chunk_audio(audio_segment, chunk_duration_ms=30000)
    
    # Transcribe each chunk
    transcribed_texts = []
    for i, chunk in enumerate(chunks):
        try:
            chunk_text = transcribe_audio_segment(chunk, api_key)
            if chunk_text.strip():  # Only add non-empty transcriptions
                transcribed_texts.append(chunk_text)
        except Exception as e:
            # Log error but continue with other chunks
            print(f"Error transcribing chunk {i}: {e}")
            continue
    
    # Combine all transcribed text
    return " ".join(transcribed_texts)


def get_default_api_key() -> str:
    """
    Get API key from environment variables.
    
    Returns:
        str: API key from environment or empty string
    """
    return os.environ.get("OPENAI_API_KEY", "")


def validate_audio_file(file_path: str) -> bool:
    """
    Validate if the file is a supported audio format.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if valid audio file, False otherwise
    """
    valid_exts = ('.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm')
    return file_path.lower().endswith(valid_exts)
