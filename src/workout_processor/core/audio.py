"""
workout_processor/audio.py
"""

from pathlib import Path
#from moviepy import VideoFileClip
from moviepy.editor import VideoFileClip
from ..config.config import settings
from .exceptions import AudioExtractionError
from ..logger import logger


def extract_audio(video_path: Path, audio_output_path: Path) -> None:
    """
    Extract audio from video file.

    Args:
        video_path: Path to input video file
        audio_output_path: Path where audio will be saved

    Raises:
        AudioExtractionError: If audio extraction fails
    """
    logger.info(f"Extracting audio from {video_path}")
    try:
        video = VideoFileClip(str(video_path))
        if video.audio is None:
            raise AudioExtractionError("No audio track found in video")

        audio_output_path.parent.mkdir(parents=True, exist_ok=True)
        video.audio.write_audiofile(str(audio_output_path))
        video.close()

        logger.info(f"Audio saved to {audio_output_path}")
    except Exception as e:
        raise AudioExtractionError(f"Failed to extract audio: {str(e)}") from e
