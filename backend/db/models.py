"""
Database models for the chatbot application
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class User(Base):
    """User model for storing user information."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class ChatSession(Base):
    """Chat session model for tracking conversations."""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())

class ChatMessage(Base):
    """Chat message model for storing conversation history."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_message = Column(Text)
    bot_response = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    message_metadata = Column(Text)  # JSON string for additional data

class Session(Base):
    """Session model for persisting chat sessions."""
    __tablename__ = "sessions"

    session_id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    messages = Column(JSON)  # JSON array of messages

class Lead(Base):
    """Lead model linking leads to sessions and HubSpot."""
    __tablename__ = "leads"

    lead_id = Column(Integer, primary_key=True, index=True)
    hubspot_id = Column(String, index=True)
    session_id = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)

class OAuthToken(Base):
    """OAuth token model for storing access and refresh tokens."""
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, index=True)  # 'google' or 'hubspot'
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    token_type = Column(String, default="Bearer")
    scope = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Document(Base):
    """Document model for storing document metadata."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, index=True)
    file_name = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    content = Column(Text)

class DocumentChunk(Base):
    """Document chunk model with embeddings."""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, index=True)
    chunk_index = Column(Integer)
    content = Column(Text)
    embedding = Column(Vector(1536))  # OpenAI text-embedding-3-small dimension
    chunk_metadata = Column(JSON)

# Create vector index
Index('document_chunks_embedding_idx', DocumentChunk.embedding, postgresql_using='ivfflat')

