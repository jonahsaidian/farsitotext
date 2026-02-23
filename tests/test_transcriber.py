from unittest.mock import MagicMock, patch

from pydub import AudioSegment

from api.transcriber import (
    chunk_audio,
    get_default_api_key,
    postprocess_transcription,
    transcribe_audio_segment,
)


def silent_audio(duration_ms: int) -> AudioSegment:
    return AudioSegment.silent(duration=duration_ms)


class TestChunkAudio:
    def test_audio_shorter_than_chunk_returns_single_chunk(self):
        audio = silent_audio(5000)
        chunks = chunk_audio(audio, chunk_duration_ms=10000)
        assert len(chunks) == 1
        assert len(chunks[0]) == 5000

    def test_even_split(self):
        audio = silent_audio(30000)
        chunks = chunk_audio(audio, chunk_duration_ms=10000)
        assert len(chunks) == 3
        assert all(len(c) == 10000 for c in chunks)

    def test_remainder_chunk(self):
        audio = silent_audio(25000)
        chunks = chunk_audio(audio, chunk_duration_ms=10000)
        assert len(chunks) == 3
        assert len(chunks[2]) == 5000

    def test_default_chunk_duration_is_30s(self):
        audio = silent_audio(60000)
        chunks = chunk_audio(audio)
        assert len(chunks) == 2


class TestGetDefaultApiKey:
    def test_returns_key_from_env(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-123")
        assert get_default_api_key() == "sk-test-123"

    def test_returns_empty_string_when_not_set(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        assert get_default_api_key() == ""


class TestPostprocessTranscription:
    def test_returns_text_unchanged(self):
        text = "این یک متن فارسی است"
        assert postprocess_transcription(text, "fake-key") == text

    def test_handles_empty_string(self):
        assert postprocess_transcription("", "fake-key") == ""


class TestTranscribeAudioSegment:
    def test_returns_transcribed_text(self):
        audio = silent_audio(3000)
        mock_response = MagicMock()
        mock_response.text = "سلام دنیا"

        with patch("api.transcriber.OpenAI") as mock_cls:
            mock_cls.return_value.audio.transcriptions.create.return_value = mock_response
            result = transcribe_audio_segment(audio, "fake-key")

        assert result == "سلام دنیا"

    def test_passes_correct_language_and_model(self):
        audio = silent_audio(3000)
        mock_response = MagicMock()
        mock_response.text = "test"

        with patch("api.transcriber.OpenAI") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.audio.transcriptions.create.return_value = mock_response
            transcribe_audio_segment(audio, "fake-key")

        call_kwargs = mock_client.audio.transcriptions.create.call_args.kwargs
        assert call_kwargs["language"] == "fa"
        assert call_kwargs["model"] == "gpt-4o-transcribe"
