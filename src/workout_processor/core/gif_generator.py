"""
# workout_processor/gif_generator.py
"""

from pathlib import Path
import logging
from typing import Dict
from moviepy.editor import VideoFileClip
from ..config.config import settings
from .exceptions import GIFGenerationError
from ..logger import logger


def generate_movement_gifs(
    video_path: Path,
    key_segments: Dict,
    output_dir: Path,
    fps: int = 15,
    speed_multiplier: float = 2.0
) -> None:
    """
    Generate GIFs for each movement segment.

    Args:
        video_path: Path to input video file
        key_segments: Dictionary of movement segments
        output_dir: Directory where GIFs will be saved
        fps: Frames per second for output GIFs
        speed_multiplier: Factor by which to speed up the GIFs

    Raises:
        GIFGenerationError: If GIF generation fails
    """
    logger.info(f"Generating GIFs from {video_path}")

    try:
        video = VideoFileClip(str(video_path))
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, (movement, segments) in enumerate(key_segments.items(), 1):
            for j, segment in enumerate(segments, 1):
                gif_path = output_dir / \
                    f"{i:02d}_{movement.replace(' ', '_')}_{j:02d}.gif"

                logger.info(f"Creating GIF: {gif_path.name}")
                clip = (video.subclip(segment["start_time"], segment["end_time"])
                        .speedx(speed_multiplier))
                clip.write_gif(str(gif_path), fps=fps)

        video.close()
        logger.info("GIF generation completed")

    except Exception as e:
        raise GIFGenerationError(f"Failed to generate GIFs: {str(e)}") from e
