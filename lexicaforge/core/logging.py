"""Logging configuration for LexicaForge.

This module provides a standardized logging configuration for the entire application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import structlog
from structlog.types import Processor

def setup_structlog_processors() -> list[Processor]:
    """Set up the processors for structlog configuration.
    
    Returns:
        list[Processor]: List of processors to be used by structlog.
    """
    return [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ]

def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    development: bool = False
) -> None:
    """Configure logging for the application.
    
    Args:
        log_level: The logging level to use (default: "INFO")
        log_file: Optional path to log file (default: None)
        development: Whether to run in development mode (default: False)
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )

    # Configure structlog
    processors = setup_structlog_processors()
    
    if development:
        # Add pretty printing for development
        processors.insert(0, structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        cache_logger_on_first_use=True
    )

    # Set up file handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        logging.getLogger().addHandler(file_handler)

# Create a logger instance
logger = structlog.get_logger() 