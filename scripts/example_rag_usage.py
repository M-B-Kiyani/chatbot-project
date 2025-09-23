#!/usr/bin/env python3
"""
Example RAG System Usage

This script demonstrates how to use the RAG system for document search and answer generation.

Usage:
    python scripts/example_rag_usage.py

Requirements:
    - OPENAI_API_KEY environment variable must be set
    - Knowledge base must be indexed (run index_knowledge_base_complete.py first)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the knowledge_base directory to the path
sys.path.append(str(Path(__file__).parent.parent / "knowledge_base"))
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from services.rag_service import RAGService

def main():
    """Demonstrate RAG system usage."""
    print("RAG SYSTEM USAGE EXAMPLE")
    print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is not set!")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1
    
    # Initialize RAG service
    print("Initializing RAG service...")
    rag_service = RAGService()
    
    # Example queries
    example_queries = [
        "What services does Metalogics offer?",
        "How can I contact the sales team?",
        "What technologies does the company use?",
        "Tell me about the company's mission and vision",
        "What are the pricing options available?"
    ]
    
    print("\nExample 1: Document Search")
    print("-" * 30)
    
    query = example_queries[0]
    print(f"Query: {query}")
    
    # Search for relevant documents
    documents = rag_service.search_documents(query, 3)
    print(f"\nFound {len(documents)} relevant documents:")
    
    for i, doc in enumerate(documents, 1):
        metadata = doc.get('metadata', {})
        print(f"\n{i}. {metadata.get('file_name', 'unknown')}")
        print(f"   Relevance Score: {doc.get('relevance_score', 0):.3f}")
        print(f"   File Path: {metadata.get('file_path', 'unknown')}")
        print(f"   Content Preview: {doc.get('content', '')[:100]}...")
    
    print("\n" + "=" * 50)
    print("Example 2: Answer Generation")
    print("-" * 30)
    
    query = example_queries[1]
    print(f"Query: {query}")
    
    # Generate answer
    result = rag_service.generate_answer(query, documents)
    
    print(f"\nAnswer (Confidence: {result['confidence']}):")
    print(f"{result['answer']}")
    
    print(f"\nDocuments used:")
    for i, doc in enumerate(result['documents_used'], 1):
        metadata = doc.get('metadata', {})
        print(f"  {i}. {metadata.get('file_name', 'unknown')} (score: {doc.get('relevance_score', 0):.3f})")
    
    print("\n" + "=" * 50)
    print("Example 3: Low Relevance Handling")
    print("-" * 30)
    
    # Test with a query that might have low relevance
    low_relevance_query = "What is the weather like today?"
    print(f"Query: {low_relevance_query}")
    
    documents = rag_service.search_documents(low_relevance_query, 3)
    result = rag_service.generate_answer(low_relevance_query, documents, relevance_threshold=0.7)
    
    print(f"\nAnswer (Confidence: {result['confidence']}):")
    print(f"{result['answer']}")
    print(f"Reason: {result['reason']}")
    
    print("\n" + "=" * 50)
    print("Example 4: API Usage")
    print("-" * 30)
    
    print("To use the API endpoints, start the server with:")
    print("uvicorn backend.main:app --reload")
    print("\nThen you can make requests like:")
    print("GET /api/rag-search?q=What services do you offer?&n_results=5")
    print("POST /api/rag-answer with query parameter")
    
    print("\n" + "=" * 50)
    print("Example completed successfully!")
    
    return 0

if __name__ == "__main__":
    exit(main())
