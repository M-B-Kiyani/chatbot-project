#!/usr/bin/env python3
"""
Test script for the RAG system.
"""

import os
import sys
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "knowledge_base"))
sys.path.append(str(project_root / "backend" / "services"))

def test_document_processing():
    """Test document processing functionality."""
    print("Testing document processing...")
    
    try:
        from knowledge_base.processors.document_processor import DocumentProcessor
        
        processor = DocumentProcessor(
            documents_dir=str(project_root / "knowledge_base" / "metalogics_kb"),
            embeddings_dir=str(project_root / "knowledge_base" / "embeddings")
        )
        
        # Test processing a sample document
        sample_doc = project_root / "knowledge_base" / "documents" / "sample_knowledge.txt"
        if sample_doc.exists():
            doc_data = processor.process_document(sample_doc)
            if doc_data:
                print(f"✓ Document processed successfully: {doc_data['file_name']}")
                print(f"  - Chunks: {len(doc_data['chunks'])}")
                print(f"  - File type: {doc_data['file_type']}")
                return True
            else:
                print("✗ Document processing failed")
                return False
        else:
            print("✗ Sample document not found")
            return False
            
    except Exception as e:
        print(f"✗ Document processing error: {str(e)}")
        return False

def test_rag_service():
    """Test RAG service functionality."""
    print("\nTesting RAG service...")
    
    try:
        from backend.services.rag_service import RAGService
        
        rag_service = RAGService()
        
        # Test knowledge base stats
        stats = rag_service.get_knowledge_base_stats()
        print(f"✓ Knowledge base stats retrieved: {stats}")
        
        # Test document search
        search_results = rag_service.search_documents("chatbot features", 3)
        print(f"✓ Document search completed: {len(search_results)} results")
        
        if search_results:
            # Test answer generation
            answer = rag_service.generate_answer(
                "What are the main features of this chatbot?",
                search_results
            )
            print(f"✓ Answer generation completed: {len(answer['answer'])} characters")
            print(f"  Answer preview: {answer['answer'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ RAG service error: {str(e)}")
        return False

def test_api_endpoints(base_url="http://localhost:8000"):
    """Test API endpoints."""
    print(f"\nTesting API endpoints at {base_url}...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health endpoint working")
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
        
        # Test knowledge base stats
        response = requests.get(f"{base_url}/knowledge", timeout=5)
        if response.status_code == 200:
            print("✓ Knowledge base stats endpoint working")
        else:
            print(f"✗ Knowledge base stats failed: {response.status_code}")
            return False
        
        # Test search endpoint
        response = requests.get(
            f"{base_url}/rag-search",
            params={"q": "API endpoints", "n_results": 3},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Search endpoint working: {data['total_results']} results")
        else:
            print(f"✗ Search endpoint failed: {response.status_code}")
            return False
        
        # Test answer generation endpoint
        response = requests.post(
            f"{base_url}/rag-answer",
            json={"query": "What are the main features?"},
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Answer generation endpoint working: {len(data['answer'])} characters")
        else:
            print(f"✗ Answer generation endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to API server. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"✗ API test error: {str(e)}")
        return False

def main():
    """Main test function."""
    print("RAG System Test Suite")
    print("=" * 50)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("✗ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1
    
    # Run tests
    tests = [
        ("Document Processing", test_document_processing),
        ("RAG Service", test_rag_service),
        ("API Endpoints", test_api_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"✗ {test_name} test failed")
    
    print(f"\n{'=' * 50}")
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! RAG system is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
