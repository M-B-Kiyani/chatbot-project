"""
Integration tests for the RAG system.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "knowledge_base"))
sys.path.append(str(project_root / "backend" / "services"))

from processors.document_processor import DocumentProcessor
from rag_service import RAGService

@pytest.fixture
def sample_document():
    """Create a sample document for testing."""
    doc_path = project_root / "knowledge_base" / "metalogics_kb" / "test_doc.txt"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    
    content = """
    This is a test document for RAG system testing.
    
    It contains information about:
    - Document processing
    - Vector embeddings
    - Similarity search
    - Answer generation
    
    The system should be able to find this document when searching for
    relevant information about RAG functionality.
    """
    
    with open(doc_path, 'w') as f:
        f.write(content)
    
    yield doc_path
    
    # Cleanup
    if doc_path.exists():
        doc_path.unlink()

@pytest.fixture
def document_processor():
    """Create a document processor for testing."""
    return DocumentProcessor(
        documents_dir=str(project_root / "knowledge_base" / "metalogics_kb"),
        embeddings_dir=str(project_root / "knowledge_base" / "embeddings")
    )

@pytest.fixture
def rag_service():
    """Create a RAG service for testing."""
    return RAGService()

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not set")
class TestRAGIntegration:
    """Integration tests for the RAG system."""
    
    def test_document_processing(self, sample_document, document_processor):
        """Test document processing functionality."""
        # Process the sample document
        doc_data = document_processor.process_document(sample_document)
        
        assert doc_data is not None
        assert doc_data['file_name'] == 'test_doc.txt'
        assert len(doc_data['chunks']) > 0
        assert doc_data['file_type'] == '.txt'
    
    def test_embedding_generation(self, document_processor):
        """Test embedding generation."""
        test_text = "This is a test text for embedding generation."
        embedding = document_processor.generate_embeddings(test_text)
        
        assert embedding is not None
        assert len(embedding) > 0
        assert isinstance(embedding[0], float)
    
    def test_vector_database_operations(self, sample_document, document_processor):
        """Test vector database operations."""
        # Process document
        doc_data = document_processor.process_document(sample_document)
        assert doc_data is not None
        
        # Upsert to vector database
        document_processor.upsert_to_vector_db(doc_data)
        
        # Search for similar documents
        results = document_processor.search_similar_documents("RAG system testing", 3)
        
        assert len(results) > 0
        assert results[0]['relevance_score'] > 0
    
    def test_rag_service_search(self, sample_document, rag_service):
        """Test RAG service search functionality."""
        # Process the sample document first
        processor = DocumentProcessor(
            documents_dir=str(project_root / "knowledge_base" / "metalogics_kb"),
            embeddings_dir=str(project_root / "knowledge_base" / "embeddings")
        )
        
        doc_data = processor.process_document(sample_document)
        processor.upsert_to_vector_db(doc_data)
        
        # Test search
        results = rag_service.search_documents("RAG system testing", 3)
        
        assert len(results) > 0
        assert results[0]['relevance_score'] > 0
        assert 'content' in results[0]
        assert 'metadata' in results[0]
    
    def test_rag_service_answer_generation(self, sample_document, rag_service):
        """Test RAG service answer generation."""
        # Process the sample document first
        processor = DocumentProcessor(
            documents_dir=str(project_root / "knowledge_base" / "metalogics_kb"),
            embeddings_dir=str(project_root / "knowledge_base" / "embeddings")
        )
        
        doc_data = processor.process_document(sample_document)
        processor.upsert_to_vector_db(doc_data)
        
        # Test answer generation
        query = "What is this document about?"
        docs = rag_service.search_documents(query, 3)
        answer = rag_service.generate_answer(query, docs)
        
        assert answer is not None
        assert len(answer) > 0
        assert "RAG" in answer or "test" in answer.lower()
    
    def test_knowledge_base_stats(self, rag_service):
        """Test knowledge base statistics."""
        stats = rag_service.get_knowledge_base_stats()
        
        assert 'total_chunks' in stats
        assert 'collection_name' in stats
        assert 'last_updated' in stats
        assert stats['total_chunks'] >= 0
    
    def test_end_to_end_workflow(self, sample_document, rag_service):
        """Test complete end-to-end workflow."""
        # Process document
        processor = DocumentProcessor(
            documents_dir=str(project_root / "knowledge_base" / "metalogics_kb"),
            embeddings_dir=str(project_root / "knowledge_base" / "embeddings")
        )
        
        doc_data = processor.process_document(sample_document)
        processor.upsert_to_vector_db(doc_data)
        
        # Test complete RAG workflow
        query = "What information does this document contain?"
        
        # Search
        docs = rag_service.search_documents(query, 3)
        assert len(docs) > 0
        
        # Generate answer
        answer = rag_service.generate_answer(query, docs)
        assert answer is not None
        assert len(answer) > 0
        
        # Verify answer quality
        assert any(keyword in answer.lower() for keyword in ['document', 'information', 'rag', 'test'])

if __name__ == "__main__":
    pytest.main([__file__])
