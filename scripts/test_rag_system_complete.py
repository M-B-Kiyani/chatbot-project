#!/usr/bin/env python3
"""
Complete RAG System Test Script

This script tests the entire RAG (Retrieval-Augmented Generation) system including:
1. Document indexing
2. Vector search functionality
3. Answer generation
4. API endpoints

Usage:
    python scripts/test_rag_system_complete.py

Requirements:
    - OPENAI_API_KEY environment variable must be set
    - Knowledge base must be indexed (run index_knowledge_base_complete.py first)
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from knowledge_base.processors.document_processor import DocumentProcessor
from backend.services.rag_service import RAGService

def test_document_processor():
    """Test the document processor functionality."""
    print("=" * 60)
    print("TESTING DOCUMENT PROCESSOR")
    print("=" * 60)
    
    try:
        processor = DocumentProcessor(
            documents_dir=str(Path(__file__).parent.parent / "knowledge_base"),
            embeddings_dir=str(Path(__file__).parent.parent / "knowledge_base" / "embeddings")
        )
        
        # Test processing a single document
        kb_path = Path(__file__).parent.parent / "knowledge_base"
        test_files = list(kb_path.rglob("*.md"))[:2]  # Test first 2 markdown files
        
        if not test_files:
            print("No markdown files found for testing")
            return False
        
        print(f"Testing with files: {[f.name for f in test_files]}")
        
        for test_file in test_files:
            print(f"\nProcessing: {test_file.name}")
            doc_data = processor.process_document(test_file)
            if doc_data:
                print(f"  ✓ Successfully processed")
                print(f"  - Chunks: {len(doc_data['chunks'])}")
                print(f"  - File size: {doc_data['metadata']['file_size']} bytes")
            else:
                print(f"  ✗ Failed to process")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Document processor test failed: {e}")
        return False

def test_rag_service():
    """Test the RAG service functionality."""
    print("\n" + "=" * 60)
    print("TESTING RAG SERVICE")
    print("=" * 60)
    
    try:
        rag_service = RAGService()
        
        # Test search functionality
        test_queries = [
            "What services does the company offer?",
            "How can I contact support?",
            "What technologies are used?",
            "Tell me about the company history"
        ]
        
        for query in test_queries:
            print(f"\nTesting query: '{query}'")
            
            # Test search
            docs = rag_service.search_documents(query, 3)
            print(f"  Found {len(docs)} documents")
            
            if docs:
                for i, doc in enumerate(docs):
                    print(f"    {i+1}. {doc.get('metadata', {}).get('file_name', 'unknown')} (score: {doc.get('relevance_score', 0):.3f})")
                
                # Test answer generation
                result = rag_service.generate_answer(query, docs)
                print(f"  Answer confidence: {result['confidence']}")
                print(f"  Answer preview: {result['answer'][:100]}...")
            else:
                print("  No documents found")
        
        # Test knowledge base stats
        stats = rag_service.get_knowledge_base_stats()
        print(f"\nKnowledge base stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"✗ RAG service test failed: {e}")
        return False

def test_api_endpoints(base_url="http://localhost:8000"):
    """Test the API endpoints."""
    print("\n" + "=" * 60)
    print("TESTING API ENDPOINTS")
    print("=" * 60)
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("  ✓ Health endpoint working")
        else:
            print(f"  ✗ Health endpoint failed: {response.status_code}")
            return False
        
        # Test knowledge base stats
        print("\nTesting knowledge base stats...")
        response = requests.get(f"{base_url}/knowledge", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Knowledge base stats: {data}")
        else:
            print(f"  ✗ Knowledge base stats failed: {response.status_code}")
        
        # Test RAG search
        print("\nTesting RAG search...")
        test_query = "What services does the company offer?"
        response = requests.get(f"{base_url}/rag-search", 
                               params={"q": test_query, "n_results": 3}, 
                               timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ RAG search working")
            print(f"  - Query: {data['query']}")
            print(f"  - Results: {data['total_results']}")
            for i, doc in enumerate(data['documents']):
                print(f"    {i+1}. {doc['file_name']} (score: {doc['score']:.3f})")
        else:
            print(f"  ✗ RAG search failed: {response.status_code}")
            return False
        
        # Test RAG answer generation
        print("\nTesting RAG answer generation...")
        response = requests.post(f"{base_url}/rag-answer", 
                                params={"query": test_query}, 
                                timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ RAG answer generation working")
            print(f"  - Confidence: {data['confidence']}")
            print(f"  - Answer preview: {data['answer'][:150]}...")
        else:
            print(f"  ✗ RAG answer generation failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("  ⚠ API server not running. Start the server with: uvicorn backend.main:app --reload")
        return False
    except Exception as e:
        print(f"  ✗ API test failed: {e}")
        return False

def main():
    """Main test function."""
    print("RAG SYSTEM COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nERROR: OPENAI_API_KEY environment variable is not set!")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1
    
    print(f"OpenAI API key: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Not set'}")
    
    # Run tests
    tests = [
        ("Document Processor", test_document_processor),
        ("RAG Service", test_rag_service),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"\n{test_name}: {'✓ PASSED' if result else '✗ FAILED'}")
        except Exception as e:
            print(f"\n{test_name}: ✗ ERROR - {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! RAG system is working correctly.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())
