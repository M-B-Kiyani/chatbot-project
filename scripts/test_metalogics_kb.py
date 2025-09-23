#!/usr/bin/env python3
"""
Test script specifically for the Metalogics knowledge base.
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

def test_metalogics_queries():
    """Test with Metalogics-specific queries."""
    print("🧪 Testing Metalogics Knowledge Base Queries")
    print("=" * 60)
    
    try:
        from rag_service import RAGService
        
        rag_service = RAGService()
        
        # Metalogics-specific test queries
        test_queries = [
            "What services does Metalogics offer?",
            "Tell me about the company history and mission",
            "What technologies and platforms do you work with?",
            "How can I contact Metalogics for sales or support?",
            "What is your pricing structure?",
            "Tell me about your portfolio and past projects",
            "What are your development processes?",
            "Do you offer mobile app development?",
            "What is your expertise in blockchain and Web3?",
            "How do you handle SEO and digital marketing?"
        ]
        
        print(f"Testing {len(test_queries)} Metalogics-specific queries...\n")
        
        for i, query in enumerate(test_queries, 1):
            print(f"🔍 Query {i}: {query}")
            print("-" * 50)
            
            try:
                # Search for relevant documents
                docs = rag_service.search_documents(query, 3)
                
                if docs:
                    print(f"✅ Found {len(docs)} relevant documents")
                    
                    # Show top results
                    for j, doc in enumerate(docs[:2], 1):
                        print(f"   {j}. {doc['metadata']['file_name']} (score: {doc['relevance_score']:.2f})")
                        print(f"      📁 Section: {doc['metadata'].get('file_path', 'N/A')}")
                        print(f"      📝 Preview: {doc['content'][:100]}...")
                    
                    # Generate answer
                    print(f"\n💬 Generated Answer:")
                    answer = rag_service.generate_answer(query, docs)
                    print(f"   {answer}")
                    
                else:
                    print("❌ No relevant documents found")
                
                print("\n" + "="*60 + "\n")
                
            except Exception as e:
                print(f"❌ Error processing query: {str(e)}")
                print("\n" + "="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Metalogics testing: {str(e)}")
        return False

def test_api_endpoints(base_url="http://localhost:8000"):
    """Test API endpoints with Metalogics queries."""
    print(f"\n🌐 Testing API Endpoints (via {base_url})")
    print("=" * 60)
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test knowledge base stats
        response = requests.get(f"{base_url}/knowledge", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Knowledge base stats: {data.get('stats', {}).get('total_chunks', 0)} chunks")
        else:
            print(f"❌ Knowledge base stats failed: {response.status_code}")
            return False
        
        # Test search with Metalogics queries
        metalogics_queries = [
            "What services does Metalogics offer?",
            "Tell me about your company history",
            "What technologies do you use?"
        ]
        
        for query in metalogics_queries:
            print(f"\n🔍 Testing search: {query}")
            
            response = requests.get(
                f"{base_url}/rag-search",
                params={"q": query, "n_results": 3},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Found {data['total_results']} results")
                
                if data['documents']:
                    top_doc = data['documents'][0]
                    print(f"   📄 Top result: {top_doc['metadata']['file_name']} (score: {top_doc['relevance_score']:.2f})")
            else:
                print(f"   ❌ Search failed: {response.status_code}")
        
        # Test answer generation
        print(f"\n💬 Testing answer generation...")
        
        response = requests.post(
            f"{base_url}/rag-answer",
            json={"query": "What services does Metalogics offer?"},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Answer generated: {len(data['answer'])} characters")
            print(f"   📝 Answer preview: {data['answer'][:200]}...")
        else:
            print(f"   ❌ Answer generation failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"❌ API test error: {str(e)}")
        return False

def test_knowledge_base_coverage():
    """Test knowledge base coverage and organization."""
    print("\n📊 Testing Knowledge Base Coverage")
    print("=" * 60)
    
    try:
        from rag_service import RAGService
        
        rag_service = RAGService()
        
        # Test different knowledge base sections
        sections = [
            ("Company Information", "What is Metalogics about?"),
            ("Services", "What services do you offer?"),
            ("Portfolio", "What projects have you completed?"),
            ("Technologies", "What technologies do you use?"),
            ("Contact", "How can I contact you?"),
            ("Pricing", "What are your prices?"),
            ("FAQ", "What are your frequently asked questions?")
        ]
        
        coverage_results = {}
        
        for section, query in sections:
            print(f"\n🔍 Testing {section} section...")
            
            docs = rag_service.search_documents(query, 5)
            
            if docs:
                # Analyze which files are being found
                file_sources = set()
                for doc in docs:
                    file_path = doc['metadata'].get('file_path', '')
                    if 'metalogics_kb' in file_path:
                        section_name = Path(file_path).parent.name
                        file_sources.add(section_name)
                
                coverage_results[section] = {
                    'found': True,
                    'doc_count': len(docs),
                    'sources': list(file_sources),
                    'top_score': docs[0]['relevance_score'] if docs else 0
                }
                
                print(f"   ✅ Found {len(docs)} documents from: {', '.join(file_sources)}")
                print(f"   📊 Top score: {docs[0]['relevance_score']:.2f}")
            else:
                coverage_results[section] = {
                    'found': False,
                    'doc_count': 0,
                    'sources': [],
                    'top_score': 0
                }
                print(f"   ❌ No documents found")
        
        # Summary
        print(f"\n📈 Coverage Summary:")
        print("-" * 40)
        
        found_sections = sum(1 for result in coverage_results.values() if result['found'])
        total_sections = len(coverage_results)
        
        print(f"✅ Sections covered: {found_sections}/{total_sections}")
        
        for section, result in coverage_results.items():
            status = "✅" if result['found'] else "❌"
            print(f"   {status} {section}: {result['doc_count']} docs, score: {result['top_score']:.2f}")
        
        return found_sections == total_sections
        
    except Exception as e:
        print(f"❌ Error in coverage testing: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🚀 Metalogics Knowledge Base Test Suite")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1
    
    # Run tests
    tests = [
        ("Metalogics Queries", test_metalogics_queries),
        ("API Endpoints", test_api_endpoints),
        ("Knowledge Base Coverage", test_knowledge_base_coverage)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test passed")
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n{'=' * 60}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Metalogics knowledge base is working correctly.")
        print("\n💡 Next steps:")
        print("   1. Start the API server: make dev-backend")
        print("   2. Use the RAG endpoints for your chatbot")
        print("   3. Add more documents to metalogics_kb/ as needed")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())

