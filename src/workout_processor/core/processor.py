"""
workout_processor/core/processor.py
"""
from pathlib import Path
from typing import Dict, Union

from ..config.config import settings
from .audio import extract_audio
from .transcription import transcribe_audio
from .movement_detection import get_movement_segments
from .gif_generator import generate_movement_gifs
from ..logger import logger


class WorkoutProcessor:
    """Main class for processing workout videos.

    This class orchestrates the entire workflow of processing a workout video:
    1. Extracting audio from the video
    2. Transcribing the audio using Whisper
    3. Detecting movement segments in the transcription using fuzzy methods
    4. Generating GIFs for each detected movement

    Attributes:
        video_path: Path to the input video file

    Raises:
        FileNotFoundError: If the input video file doesn't exist
        AudioExtractionError: If audio extraction fails
        TranscriptionError: If audio transcription fails
        GIFGenerationError: If GIF generation fails
    """

    def __init__(self, video_path: Union[Path, str], progress_callback=None):
        """
        Initialize workout processor.

        Args:
            video_path: Path to input video file
        """
        self.video_path = Path(video_path)
        self.progress_callback = progress_callback
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

    async def update_progress(self, step: str, progress: float):
        """Update progress for the current processing step."""
        if self.progress_callback:
            try:
                await self.progress_callback({
                    "step": step,
                    "progress": round(progress, 2)  # Round to 2 decimal places
                })
            except Exception as e:
                logger.error(f"Failed to update progress: {e}")

    async def process(self) -> Dict:
        """Process the workout video end-to-end.

        Executes the complete workflow:
        1. Extracts audio from the video
        2. Transcribes the audio using Whisper
        3. Identifies movement segments in the transcription
        4. Generates GIFs for each movement segment

        Returns:
            Dictionary containing:
                - video_path: Path to the processed video
                - movements: Dictionary mapping movement names to lists of segments
                  Each segment contains:
                  - start_time: Start time in seconds
                  - end_time: End time in seconds
                  - description: Transcribed text for the segment
                  - similarity_score: Match confidence score
        """
        logger.info(f"Starting workout video processing: {self.video_path}")

        try:
            # Extract audio
            await self.update_progress("audio", 0)
            extract_audio(self.video_path, settings.AUDIO_PATH)
            await self.update_progress("audio", 100)

            # Transcribe audio
            await self.update_progress("transcribe", 0)
            transcription_segments = transcribe_audio(
                settings.AUDIO_PATH,
                settings.TRANSCRIPT_PATH,
                settings.JSON_PATH
            )
            await self.update_progress("transcribe", 100)

            # Detect movements
            await self.update_progress("detect", 0)
            movement_segments = get_movement_segments(
                transcription_segments,
                settings.MOVEMENTS,
                settings.SIMILARITY_THRESHOLD
            )
            await self.update_progress("detect", 100)

            # Generate GIFs
            await self.update_progress("gif", 0)
            generate_movement_gifs(
                self.video_path,
                movement_segments,
                settings.GIFS_PATH,
                settings.GIF_FPS,
                settings.GIF_SPEED_MULTIPLIER
            )
            await self.update_progress("gif", 100)

            return {
                "video_path": str(self.video_path),
                "movements": movement_segments
            }
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise 