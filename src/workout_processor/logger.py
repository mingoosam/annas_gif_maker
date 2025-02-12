"""
Import python packages
"""
import logging
from pathlib import Path


def setup_logger(log_level: str = "INFO") -> logging.Logger:
    """
    Configure and return the package logger.
    """
    _logger = logging.getLogger("workout_processor")

    if not _logger.handlers:  # Avoid adding handlers multiple times
        _logger.setLevel(getattr(logging, log_level))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        _logger.addHandler(console_handler)

        # File handler
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "workout_processor.log")
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        _logger.addHandler(file_handler)

    return _logger


logger = setup_logger()
