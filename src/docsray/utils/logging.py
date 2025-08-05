"""Logging configuration utilities."""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", format: Optional[str] = None) -> None:
    """Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format: Log format string (optional)
    """
    if format is None:
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format,
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )

    # Set specific loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
