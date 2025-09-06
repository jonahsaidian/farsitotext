"""
API module for Farsi audio transcription using OpenAI.
"""
from openai import OpenAI, AuthenticationError
import os


def transcribe_audio(file_path: str, api_key: str) -> str:
    """
    Transcribe Farsi audio file using OpenAI's API.
    
    Args:
        file_path (str): Path to the audio file
        api_key (str): OpenAI API key
        
    Returns:
        str: Transcribed text
        
    Raises:
        AuthenticationError: If API key is invalid
        Exception: For other transcription errors
    """
    return "This is a test"
    audio_file = open(file_path, "rb")
    
    try:
        client = OpenAI(api_key=api_key)
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=audio_file,
            language="fa",
            prompt="You are a farsi language expert. Please transcribe the following audio in farsi, output should be farsi text with appropriate line breaks and grammar as needed."
        )
        audio_file.close()
        return transcription.text
        
    except AuthenticationError:
        audio_file.close()
        raise AuthenticationError("Invalid API key. Please enter a valid OpenAI API key.")
    except Exception as e:
        audio_file.close()
        raise Exception(f"Transcription error: {e}")


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
