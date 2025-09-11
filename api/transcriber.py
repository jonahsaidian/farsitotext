"""
API module for Farsi audio transcription using OpenAI.
"""
from openai import OpenAI, AuthenticationError
import os
import tempfile
from openai.types.chat.chat_completion_content_part_input_audio_param import InputAudio
from pydub import AudioSegment
from dotenv import load_dotenv
import openai

load_dotenv()

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


def postprocess_transcription(transcribed_text: str, api_key: str) -> str:
    """
    Calls OpenAI to return the transcribed text with minor grammar, spelling, and syntax fixes only.
    The model should not attempt to modify the text beyond that.
    """
    return transcribed_text
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

