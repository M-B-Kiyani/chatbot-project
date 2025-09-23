"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def test_client():
    """Create a test client for API testing."""
    # TODO: Import and configure your FastAPI app
    # from backend.main import app
    # return TestClient(app)
    return None

@pytest.fixture
def sample_chat_message():
    """Sample chat message for testing."""
    return {
        "message": "Hello, how are you?",
        "user_id": "test_user_123",
        "session_id": "test_session_456"
    }

