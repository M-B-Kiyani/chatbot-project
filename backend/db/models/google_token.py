"""
Google OAuth token model for encrypted storage in database
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class GoogleToken(Base):
    """Google OAuth token model with encrypted storage."""
    __tablename__ = "google_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Could be email or Google user ID
    encrypted_access_token = Column(Text, nullable=False)
    encrypted_refresh_token = Column(Text)
    expires_at = Column(DateTime(timezone=True))
    token_type = Column(String, default="Bearer")
    scope = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())