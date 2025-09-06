"""
API package for Farsi audio transcription.
"""
from .transcriber import transcribe_audio, get_default_api_key, validate_audio_file

__all__ = ['transcribe_audio', 'get_default_api_key', 'validate_audio_file']
