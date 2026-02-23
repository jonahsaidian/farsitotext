"""
API package for Farsi audio transcription.
"""

from .transcriber import (
    chunk_audio,
    get_default_api_key,
    postprocess_transcription,
    transcribe_audio,
    transcribe_audio_segment,
)

__all__ = [
    "transcribe_audio",
    "transcribe_audio_segment",
    "chunk_audio",
    "get_default_api_key",
    "postprocess_transcription",
]
