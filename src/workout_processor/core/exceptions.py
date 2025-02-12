"""
workout_processor/exceptions.py
"""


class WorkoutProcessorError(Exception):
    """Base exception class for workout processor errors.

    All custom exceptions in the workout processor should inherit from this class
    to maintain a consistent error hierarchy and enable specific error handling.
    """
    pass


class AudioExtractionError(WorkoutProcessorError):
    """Raised when audio extraction fails"""
    pass


class TranscriptionError(WorkoutProcessorError):
    """Raised when transcription fails"""
    pass


class GIFGenerationError(WorkoutProcessorError):
    """Raised when GIF generation fails"""
    pass
