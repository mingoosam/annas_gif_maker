"""
# workout_processor/movement_detection.py
"""
from typing import Dict, List
import logging
import nltk
from nltk.stem import PorterStemmer
from fuzzywuzzy import fuzz
from ..config.config import settings
from ..logger import logger


def stem_string(text: str) -> str:
    """Apply Porter stemming to each word in the text.

    Args:
        text: Input text to be stemmed

    Returns:
        Space-separated string of stemmed words

    Note:
        - Porter stemming reduces words to their root form,
            which helps in matching
        - similar words regardless of their exact form
            (e.g., "running" -> "run").
    """
    ps = PorterStemmer()
    return ' '.join(ps.stem(word) for word in text.split())


def get_movement_segments(
    transcription_segments: List[Dict],
    movements: List[str],
    similarity_threshold: int
) -> Dict:
    """Identify movement segments from transcription data.

    Analyzes transcribed text to find segments that match known movement names,
    using fuzzy string matching to account for variations in how movements
    might be described.

    Args:
        transcription_segments: List of dictionaries containing transcription
                                data with 'start', 'end', and 'text' keys
        movements:              List of movement names to search for in the
                                transcription
        similarity_threshold:   Minimum similarity score (0-100) required for
                                a match

    Returns:
        Dictionary mapping movement names to lists of matching segments.
        Each segment contains start_time, end_time, description, and
        similarity_score.

    Note:
        Uses the Porter stemming algorithm and fuzzy string matching to handle
        variations in movement descriptions. The similarity_threshold parameter
        can be adjusted to make matching more or less strict.

    """
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        logger.info("Downloading NLTK tokenizer")
        nltk.download('punkt', quiet=True)

    key_segments = {movement: [] for movement in movements}

    for segment in transcription_segments:
        segment_text = segment["text"].lower()

        for movement in movements:
            similarity = fuzz.token_set_ratio(
                stem_string(movement.lower()),
                stem_string(segment_text)
            )

            if similarity >= similarity_threshold:
                key_segments[movement].append({
                    "start_time": segment["start"] - 2,
                    "end_time": segment["end"] + 8,
                    "description": segment["text"],
                    "similarity_score": similarity,
                })
                break

    # Log detection results
    for movement, segments in key_segments.items():
        logger.info(f"Found {len(segments)} segments for '{movement}'")

    return key_segments
