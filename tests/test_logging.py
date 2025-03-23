"""Tests for the logging configuration module."""

import logging
from pathlib import Path

import pytest
import structlog

from lexicaforge.core.logging import configure_logging, logger

def test_logger_initialization():
    """Test that the logger is properly initialized."""
    assert isinstance(logger, structlog.BoundLogger)

def test_configure_logging_development(tmp_path: Path):
    """Test logging configuration in development mode.
    
    Args:
        tmp_path: Pytest fixture providing a temporary directory.
    """
    log_file = tmp_path / "test.log"
    configure_logging(
        log_level="DEBUG",
        log_file=log_file,
        development=True
    )
    
    # Test that the log file was created
    assert log_file.exists()
    
    # Test that we can log messages
    logger.info("test message")
    
    # Verify the log file contains our message
    log_content = log_file.read_text()
    assert "test message" in log_content
    assert "INFO" in log_content

def test_configure_logging_production(tmp_path: Path):
    """Test logging configuration in production mode.
    
    Args:
        tmp_path: Pytest fixture providing a temporary directory.
    """
    log_file = tmp_path / "test.log"
    configure_logging(
        log_level="INFO",
        log_file=log_file,
        development=False
    )
    
    # Test that the log file was created
    assert log_file.exists()
    
    # Test that we can log messages
    logger.info("test message")
    
    # Verify the log file contains our message in JSON format
    log_content = log_file.read_text()
    assert "test message" in log_content
    assert "INFO" in log_content
    assert "{" in log_content  # Check for JSON format

@pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARNING", "ERROR"])
def test_log_levels(log_level: str, tmp_path: Path):
    """Test different log levels.
    
    Args:
        log_level: The log level to test.
        tmp_path: Pytest fixture providing a temporary directory.
    """
    log_file = tmp_path / "test.log"
    configure_logging(log_level=log_level, log_file=log_file)
    
    # Log messages at different levels
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    
    # Verify that only messages at or above the configured level are logged
    log_content = log_file.read_text()
    configured_level = getattr(logging, log_level.upper())
    
    if configured_level <= logging.DEBUG:
        assert "debug message" in log_content
    if configured_level <= logging.INFO:
        assert "info message" in log_content
    if configured_level <= logging.WARNING:
        assert "warning message" in log_content
    if configured_level <= logging.ERROR:
        assert "error message" in log_content 