"""
Knowledge base configuration settings
"""

import os
from typing import Dict, Any

class KnowledgeBaseConfig:
    """Configuration for the knowledge base system."""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_KEY')
        self.vector_db_key = os.getenv('VECTOR_DB_KEY')
        self.embedding_model = "text-embedding-ada-002"
        self.chunk_size = 1000
        self.chunk_overlap = 200
        self.max_tokens = 8192
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """Get configuration for embedding generation."""
        return {
            "model": self.embedding_model,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "max_tokens": self.max_tokens
        }
    
    def get_vector_db_config(self) -> Dict[str, Any]:
        """Get configuration for vector database."""
        return {
            "api_key": self.vector_db_key,
            "environment": "production",  # or "development"
            "index_name": "chatbot-knowledge"
        }

