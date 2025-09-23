#!/usr/bin/env python3
"""
Example usage of the RAG system.
"""

import os
import sys
import requests
import json
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "knowledge_base"))
sys.path.append(str(project_root / "backend" / "services"))

def example_direct_usage():
    """Example of using the RAG system directly (without API)."""
    print("=== Direct RAG System Usage ===")
    
    try:
        from rag_service import RAGService
        
        # Initialize RAG service
        rag_service = RAGService()
        
        # Example queries
        queries = [
            "What are the main features of this chatbot?",
            "How do I use the API endpoints?",
            "What is the technical stack?",
            "How do I configure the system?"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            print("-" * 50)
            
            # Search for relevant documents
            docs = rag_service.search_documents(query, 3)
            print(f"Found {len(docs)} relevant documents")
            
            # Generate answer
            answer = rag_service.generate_answer(query, docs)
            print(f"Answer: {answer}")
            
            # Show source documents
            if docs:
                print("\nSource documents:")
                for i, doc in enumerate(docs, 1):
                    print(f"  {i}. {doc['metadata']['file_name']} (score: {doc['relevance_score']:.2f})")
                    print(f"     {doc['content'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"Error in direct usage: {str(e)}")
        return False

def example_api_usage(base_url="http://localhost:8000"):
    """Example of using the RAG system via API."""
    print(f"\n=== API Usage (via {base_url}) ===")
    
    try:
        # Example queries
        queries = [
            "What are the main features?",
            "How do I configure the system?",
            "What API endpoints are available?"
        ]
        
        for query in queries:
            print(f"\nQuery: {query}")
            print("-" * 50)
            
            # Search for documents
            search_response = requests.get(
                f"{base_url}/rag-search",
                params={"q": query, "n_results": 3},
                timeout=10
            )
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                print(f"Found {search_data['total_results']} documents")
                
                # Generate answer
                answer_response = requests.post(
                    f"{base_url}/rag-answer",
                    json={"query": query},
                    timeout=15
                )
                
                if answer_response.status_code == 200:
                    answer_data = answer_response.json()
                    print(f"Answer: {answer_data['answer']}")
                    
                    # Show source documents
                    if answer_data['documents_used']:
                        print("\nSource documents:")
                        for i, doc in enumerate(answer_data['documents_used'], 1):
                            print(f"  {i}. {doc['metadata']['file_name']} (score: {doc['relevance_score']:.2f})")
                else:
                    print(f"Answer generation failed: {answer_response.status_code}")
            else:
                print(f"Search failed: {search_response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("Could not connect to API server. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"Error in API usage: {str(e)}")
        return False

def example_knowledge_base_management():
    """Example of knowledge base management operations."""
    print("\n=== Knowledge Base Management ===")
    
    try:
        from rag_service import RAGService
        
        # Initialize RAG service
        rag_service = RAGService()
        
        # Get knowledge base statistics
        stats = rag_service.get_knowledge_base_stats()
        print(f"Knowledge base statistics:")
        print(f"  Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  Collection name: {stats.get('collection_name', 'N/A')}")
        print(f"  Last updated: {stats.get('last_updated', 'N/A')}")
        
        # Process knowledge base (if needed)
        print("\nProcessing knowledge base...")
        rag_service.process_knowledge_base()
        
        return True
        
    except Exception as e:
        print(f"Error in knowledge base management: {str(e)}")
        return False

def main():
    """Main example function."""
    print("RAG System Usage Examples")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1
    
    # Run examples
    examples = [
        ("Direct Usage", example_direct_usage),
        ("API Usage", example_api_usage),
        ("Knowledge Base Management", example_knowledge_base_management)
    ]
    
    for example_name, example_func in examples:
        print(f"\n{example_name}:")
        try:
            example_func()
        except Exception as e:
            print(f"❌ {example_name} failed: {str(e)}")
    
    print(f"\n{'=' * 60}")
    print("Examples completed!")
    print("\nNext steps:")
    print("1. Add more documents to knowledge_base/documents/")
    print("2. Run 'make rag-index' to process new documents")
    print("3. Test the system with 'make rag-test'")
    print("4. Start the API server with 'make dev-backend'")
    print("5. Use the API endpoints for integration")
    
    return 0

if __name__ == "__main__":
    exit(main())
