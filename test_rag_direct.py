#!/usr/bin/env python3
"""
Direct test of the RAG system without FastAPI server
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

from rag_pipeline import load_documents, chunk_documents, create_vectorstore, search_vectorstore, generate_answer

def test_rag_system():
    """Test the RAG system directly."""
    print("🧪 Testing RAG System Directly")
    print("=" * 50)
    
    # Load documents
    print("1. Loading documents...")
    docs = load_documents("knowledge_base")
    print(f"   Loaded {len(docs)} documents")
    
    if not docs:
        print("❌ No documents loaded!")
        return False
    
    # Chunk documents
    print("\n2. Chunking documents...")
    chunks = chunk_documents(docs)
    print(f"   Created {len(chunks)} chunks")
    
    # Create vector store
    print("\n3. Creating vector store...")
    vectorstore = create_vectorstore(chunks)
    print("   ✅ Vector store created successfully")
    
    # Test search
    print("\n4. Testing search...")
    test_queries = [
        "What services does Metalogics offer?",
        "How can I contact support?",
        "What technologies does the company use?"
    ]
    
    for query in test_queries:
        print(f"\n   Query: {query}")
        try:
            results = search_vectorstore(query, k=3)
            print(f"   Found {len(results)} results")
            
            for i, (doc, score) in enumerate(results):
                print(f"     {i+1}. Score: {score:.3f} - {doc.metadata.get('source', 'unknown')}")
                print(f"        Preview: {doc.page_content[:100]}...")
            
            # Generate answer
            print(f"\n   Generating answer...")
            answer = generate_answer(query, results)
            print(f"   Answer: {answer[:200]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ RAG system test completed!")
    return True

if __name__ == "__main__":
    test_rag_system()
