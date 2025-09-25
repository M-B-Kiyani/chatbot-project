"""
Encrypted Google OAuth token manager with database storage
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet

from db.models.google_token import GoogleToken


class GoogleTokenManager:
    """Manages encrypted Google OAuth tokens in database."""

    def __init__(self):
        # Get encryption key from environment
        key = os.getenv('GOOGLE_TOKEN_ENCRYPTION_KEY')
        if not key:
            # Generate a key if not provided (for development)
            key = Fernet.generate_key().decode()
            print(f"WARNING: GOOGLE_TOKEN_ENCRYPTION_KEY not set. Using generated key: {key}")
        else:
            # Ensure key is 32 bytes
            key = key.encode()
            if len(key) != 32:
                # If it's a string, encode it properly
                import base64
                try:
                    key = base64.urlsafe_b64decode(key)
                except:
                    raise ValueError("GOOGLE_TOKEN_ENCRYPTION_KEY must be a valid Fernet key (32 bytes)")

        self.fernet = Fernet(key)

    def _encrypt(self, data: str) -> str:
        """Encrypt a string."""
        return self.fernet.encrypt(data.encode()).decode()

    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()

    def save_token(self, db: Session, user_id: str, access_token: str,
                   refresh_token: Optional[str] = None, expires_at: Optional[datetime] = None,
                   scope: Optional[str] = None) -> GoogleToken:
        """Save or update encrypted token for a user."""
        # Check if token exists
        token_record = db.query(GoogleToken).filter(GoogleToken.user_id == user_id).first()

        encrypted_access = self._encrypt(access_token)
        encrypted_refresh = self._encrypt(refresh_token) if refresh_token else None

        if token_record:
            # Update existing
            token_record.encrypted_access_token = encrypted_access
            token_record.encrypted_refresh_token = encrypted_refresh
            token_record.expires_at = expires_at
            token_record.scope = scope
            token_record.updated_at = datetime.utcnow()
        else:
            # Create new
            token_record = GoogleToken(
                user_id=user_id,
                encrypted_access_token=encrypted_access,
                encrypted_refresh_token=encrypted_refresh,
                expires_at=expires_at,
                scope=scope
            )
            db.add(token_record)

        db.commit()
        db.refresh(token_record)
        return token_record

    def get_token(self, db: Session, user_id: str) -> Optional[Dict[str, Any]]:
        """Get decrypted token for a user."""
        token_record = db.query(GoogleToken).filter(GoogleToken.user_id == user_id).first()
        if not token_record:
            return None

        try:
            access_token = self._decrypt(token_record.encrypted_access_token)
            refresh_token = self._decrypt(token_record.encrypted_refresh_token) if token_record.encrypted_refresh_token else None

            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': token_record.expires_at,
                'token_type': token_record.token_type,
                'scope': token_record.scope
            }
        except Exception as e:
            print(f"Error decrypting token for user {user_id}: {e}")
            return None

    def refresh_token(self, db: Session, user_id: str, new_access_token: str,
                     new_expires_at: Optional[datetime] = None) -> bool:
        """Update access token after refresh."""
        token_record = db.query(GoogleToken).filter(GoogleToken.user_id == user_id).first()
        if not token_record:
            return False

        token_record.encrypted_access_token = self._encrypt(new_access_token)
        if new_expires_at:
            token_record.expires_at = new_expires_at
        token_record.updated_at = datetime.utcnow()

        db.commit()
        return True

    def delete_token(self, db: Session, user_id: str) -> bool:
        """Delete token for a user."""
        token_record = db.query(GoogleToken).filter(GoogleToken.user_id == user_id).first()
        if token_record:
            db.delete(token_record)
            db.commit()
            return True
        return False

    def is_token_valid(self, db: Session, user_id: str) -> bool:
        """Check if user has a valid (non-expired) token."""
        token_data = self.get_token(db, user_id)
        if not token_data or not token_data.get('access_token'):
            return False

        expires_at = token_data.get('expires_at')
        if expires_at and datetime.utcnow() >= expires_at:
            return False

        return True


# Global instance
google_token_manager = GoogleTokenManager()