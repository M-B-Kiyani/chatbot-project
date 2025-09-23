"""
Unit tests for database operations
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from db.database import get_db, create_tables
from db.models import User, ChatSession, ChatMessage

class TestDatabase:
    """Test cases for database operations."""
    
    def test_user_model_creation(self):
        """Test User model creation."""
        user = User(
            google_id="google_123",
            email="test@example.com",
            name="Test User"
        )
        
        assert user.google_id == "google_123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.is_active is True
    
    def test_chat_session_model_creation(self):
        """Test ChatSession model creation."""
        session = ChatSession(
            user_id=1,
            session_id="session_123"
        )
        
        assert session.user_id == 1
        assert session.session_id == "session_123"
    
    def test_chat_message_model_creation(self):
        """Test ChatMessage model creation."""
        message = ChatMessage(
            session_id="session_123",
            user_message="Hello",
            bot_response="Hi there!"
        )
        
        assert message.session_id == "session_123"
        assert message.user_message == "Hello"
        assert message.bot_response == "Hi there!"

