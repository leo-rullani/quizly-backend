from pathlib import Path
from typing import Optional

import whisper

_MODEL: Optional[whisper.Whisper] = None


def get_whisper_model():
    """
    Lazily load and cache the Whisper model instance.
    """
    global _MODEL
    if _MODEL is None:
        _MODEL = whisper.load_model("tiny")
    return _MODEL


def transcribe_audio(audio_path: Path) -> str:
    """
    Transcribe an audio file into text using Whisper.
    """
    model = get_whisper_model()
    result = model.transcribe(str(audio_path))
    return result.get("text", "").strip()