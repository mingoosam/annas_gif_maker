"""
workout_processor/config.py
"""


from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Config settings for the workout video processor

    Attributes:

        VIDEO_PATH: Path to the input video file
        AUDIO_PATH: Path where extracted audio will be saved
        TRANSCRIPT_PATH: Path where text transcription will be saved
        JSON_PATH: Path where full transcription data will be saved
        GIFS_PATH: Directory where generated GIFs will be saved
        MOVEMENTS: List of movement names to detect in the video
        SIMILARITY_THRESHOLD: Minimum similarity score (0-100) to
                              consider a movement match
        GIF_FPS: Frames per second for output GIFs
        GIF_SPEED_MULTIPLIER: Factor by which to speed up the GIFs

    """
    VIDEO_PATH: Optional[Path] = Path("/Users/andyvarner/Documents/dev/projects/anna/data/video/IMG_0095.MOV") 
    AUDIO_PATH: Path = Path("temp/audio.wav")
    TRANSCRIPT_PATH: Path = Path("temp/transcript.txt")
    JSON_PATH: Path = Path("temp/transcript.json")
    GIFS_PATH: Path = Path("output/gifs")

    MOVEMENTS: List[str] = [
        "arm swings",
        "chair squats",
        "roll down and roll up",
        "goblet squat",
        "chest press",
        "underhand row",
        "farmer's carry"
    ]

    SIMILARITY_THRESHOLD: int = 80
    GIF_FPS: int = 15
    GIF_SPEED_MULTIPLIER: float = 2.0

    class Config:
        """
        Import environment variables
        """
        env_file = ".env"


settings = Settings()
