"""
Integration tests for knowledge base functionality
"""

import pytest
import sys
from pathlib import Path

# Add knowledge base to path
kb_path = Path(__file__).parent.parent.parent / "knowledge_base"
sys.path.insert(0, str(kb_path))

from processors.document_processor import DocumentProcessor
from config.settings import KnowledgeBaseConfig

class TestKnowledgeBaseIntegration:
    """Integration tests for knowledge base."""
    
    @pytest.fixture
    def document_processor(self):
        """Create a DocumentProcessor instance."""
        return DocumentProcessor()
    
    @pytest.fixture
    def kb_config(self):
        """Create a KnowledgeBaseConfig instance."""
        return KnowledgeBaseConfig()
    
    def test_document_processor_initialization(self, document_processor):
        """Test document processor initialization."""
        assert document_processor.documents_dir is not None
        assert document_processor.embeddings_dir is not None
    
    def test_knowledge_base_config(self, kb_config):
        """Test knowledge base configuration."""
        embedding_config = kb_config.get_embedding_config()
        assert "model" in embedding_config
        assert "chunk_size" in embedding_config
        assert embedding_config["model"] == "text-embedding-ada-002"
    
    def test_document_processing_placeholder(self, document_processor):
        """Test document processing with placeholder data."""
        # Create a test file
        test_file = Path("test_document.txt")
        test_file.write_text("This is a test document.")
        
        try:
            result = document_processor.process_document(test_file)
            assert result is not None
            assert "file_path" in result
            assert "content" in result
        finally:
            # Clean up test file
            if test_file.exists():
                test_file.unlink()

