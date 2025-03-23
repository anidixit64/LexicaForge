"""Pytest configuration and shared fixtures.

This module provides common fixtures and configuration for all tests.
"""

import asyncio
import os
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from lexicaforge.core.logging import configure_logging

# Configure test logging
configure_logging(
    log_level="DEBUG",
    log_file=Path("logs/test.log"),
    development=True
)

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case.
    
    Yields:
        asyncio.AbstractEventLoop: The event loop instance.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Get the test database URL.
    
    Returns:
        str: The test database URL.
    """
    return os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/lexicaforge_test"
    )

@pytest.fixture(scope="session")
def engine(test_db_url: str):
    """Create a SQLAlchemy engine for testing.
    
    Args:
        test_db_url: The test database URL.
        
    Yields:
        sqlalchemy.Engine: The SQLAlchemy engine.
    """
    engine = create_engine(test_db_url)
    yield engine
    engine.dispose()

@pytest.fixture
def db_session(engine) -> Generator[Session, None, None]:
    """Create a database session for testing.
    
    Args:
        engine: The SQLAlchemy engine.
        
    Yields:
        sqlalchemy.orm.Session: The database session.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(autouse=True)
def _setup_test_env():
    """Set up the test environment variables.
    
    This fixture runs automatically for every test.
    """
    os.environ["ENVIRONMENT"] = "test"
    yield
    # Clean up any test-specific environment variables here

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Get the test data directory.
    
    Returns:
        Path: The path to the test data directory.
    """
    return Path(__file__).parent / "data"

@pytest.fixture(scope="session")
def sample_texts(test_data_dir: Path) -> dict[str, str]:
    """Load sample texts for testing.
    
    Args:
        test_data_dir: The test data directory.
        
    Returns:
        dict[str, str]: A dictionary of sample texts.
    """
    texts_file = test_data_dir / "sample_texts.txt"
    if not texts_file.exists():
        return {}
    
    texts = {}
    with open(texts_file, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                key, value = line.strip().split(":", 1)
                texts[key] = value
    return texts 