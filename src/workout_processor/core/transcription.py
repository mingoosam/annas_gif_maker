"""
# workout_processor/transcription.py
"""
from pathlib import Path
import json
import logging
from typing import Dict, List, Union
import whisper
from ..config.config import settings
from .exceptions import TranscriptionError
from ..logger import logger


def transcribe_audio(
    audio_path: Path,
    text_output_path: Path,
    json_output_path: Path) -> List[Dict[str, Union[str, float]]]:
    """
    Transcribe audio file using OpenAI Whisper.

    Args:
        audio_path: Path to input audio file
        text_output_path: Path where transcription text will be saved
        json_output_path: Path where full transcription data will be saved

    Returns:
        List of transcription segments with timing data

    Raises:
        TranscriptionError: If transcription fails
    """
    try:
        if json_output_path.exists():
            logger.info(
                f"Loading existing transcription from {json_output_path}")
            with open(json_output_path, 'r', encoding='utf-8') as f:
                result = json.load(f)
        else:
            logger.info(f"Transcribing audio from {audio_path}")
            try:
                model = whisper.load_model("base")
            except Exception as e:
                raise TranscriptionError(
                    f"Failed to load whisper model '{model_name}': {str(e)}")
            result = model.transcribe(str(audio_path), word_timestamps=True)

            text_output_path.parent.mkdir(parents=True, exist_ok=True)
            json_output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(text_output_path, "w", encoding="utf-8") as f:
                f.write(result['text'])
                logger.info(f"Transcription text saved to {text_output_path}")

            with open(json_output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
                logger.info(f"Model result saved to {json_output_path}")

        return [{
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"]
        } for segment in result["segments"]]

    except Exception as e:
        raise TranscriptionError(
            f"Failed to transcribe audio: {str(e)}") from e
