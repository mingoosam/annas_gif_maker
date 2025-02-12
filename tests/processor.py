"""
# tests/processor.py
"""
from pathlib import Path
from typing import Dict, Union
from src.workout_processor.config.config import settings
from src.workout_processor.core.audio import extract_audio
from src.workout_processor.core.transcription import transcribe_audio
from src.workout_processor.core.movement_detection import get_movement_segments
from src.workout_processor.core.gif_generator import generate_movement_gifs
from src.workout_processor.logger import logger


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

    Example:
        >>> processor = WorkoutProcessor("workout.mov")
        >>> result = processor.process()
        >>> print(result["movements"])
    """

    def __init__(self, video_path: Union[Path, str]):
        """
        Initialize workout processor.

        Args:
            video_path: Path to input video file
        """
        self.video_path = Path(video_path)
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

    def process(self) -> Dict:
        """Process the workout video end-to-end.

        Executes the complete workflow:
        1. Extracts audio from the video
        2. Transcribes the audio using Whisper
        3. Identifies movement segments in the transcription
        4. Generates GIFs for each movement segment

        Returns:
            Dictionary containing:
                - video_path: Path to the processed video
                - movements: Dictionary mapping movement names to lists of
                  segments
                  Each segment contains:
                  - start_time: Start time in seconds
                  - end_time: End time in seconds
                  - description: Transcribed text for the segment
                  - similarity_score: Match confidence score

        Raises:
            AudioExtractionError: If audio extraction fails
            TranscriptionError: If transcription fails
            GIFGenerationError: If GIF generation fails

        Note:
            This method uses the configuration from the settings module for
            paths and parameters. The processing results are saved to disk
            according to the configured paths.
        """
        logger.info(f"Starting workout video processing: {self.video_path}")

        # Extract audio
        extract_audio(self.video_path, settings.AUDIO_PATH)

        # Transcribe audio
        transcription_segments = transcribe_audio(
            settings.AUDIO_PATH,
            settings.TRANSCRIPT_PATH,
            settings.JSON_PATH
        )

        # Detect movements
        movement_segments = get_movement_segments(
            transcription_segments,
            settings.MOVEMENTS,
            settings.SIMILARITY_THRESHOLD
        )

        # Generate GIFs
        generate_movement_gifs(
            self.video_path,
            movement_segments,
            settings.GIFS_PATH,
            settings.GIF_FPS,
            settings.GIF_SPEED_MULTIPLIER
        )

        return {
            "video_path": str(self.video_path),
            "movements": movement_segments
        }


# Example usage
if __name__ == "__main__":
    processor = WorkoutProcessor(settings.VIDEO_PATH)
    result = processor.process()
