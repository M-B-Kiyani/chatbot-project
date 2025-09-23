#!/usr/bin/env python3
"""
Script to index the Metalogics knowledge base with enhanced processing.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "knowledge_base"))
sys.path.append(str(project_root / "backend" / "services"))

from processors.document_processor import DocumentProcessor
from rag_service import RAGService

def analyze_knowledge_base_structure():
    """Analyze the structure of the Metalogics knowledge base."""
    kb_path = project_root / "knowledge_base" / "metalogics_kb"
    
    if not kb_path.exists():
        print(f"❌ Knowledge base directory not found: {kb_path}")
        return {}
    
    structure = {}
    total_files = 0
    
    for root, dirs, files in os.walk(kb_path):
        rel_path = Path(root).relative_to(kb_path)
        section = str(rel_path) if str(rel_path) != "." else "root"
        
        # Filter for supported file types
        supported_files = [f for f in files if f.endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml'))]
        
        if supported_files:
            structure[section] = supported_files
            total_files += len(supported_files)
    
    return structure, total_files

def print_knowledge_base_summary(structure: Dict[str, List[str]], total_files: int):
    """Print a summary of the knowledge base structure."""
    print("📚 Metalogics Knowledge Base Structure:")
    print("=" * 50)
    
    for section, files in structure.items():
        print(f"\n📁 {section}/")
        for file in files:
            print(f"   📄 {file}")
    
    print(f"\n📊 Total files to process: {total_files}")
    print("=" * 50)

def main():
    """Main function to index the Metalogics knowledge base."""
    print("🚀 Starting Metalogics Knowledge Base Indexing...")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1
    
    # Analyze knowledge base structure
    print("🔍 Analyzing knowledge base structure...")
    structure, total_files = analyze_knowledge_base_structure()
    
    if not structure:
        print("❌ No knowledge base found or empty directory")
        return 1
    
    print_knowledge_base_summary(structure, total_files)
    
    # Initialize the document processor
    print("\n🔧 Initializing document processor...")
    processor = DocumentProcessor(
        documents_dir=str(project_root / "knowledge_base" / "metalogics_kb"),
        embeddings_dir=str(project_root / "knowledge_base" / "embeddings")
    )
    
    # Process all documents
    print("\n📝 Processing documents...")
    print("-" * 40)
    
    try:
        processor.process_all_documents()
        
        # Get statistics
        print("\n📊 Getting knowledge base statistics...")
        rag_service = RAGService()
        stats = rag_service.get_knowledge_base_stats()
        
        print(f"\n✅ Metalogics Knowledge Base indexing completed!")
        print("=" * 60)
        print(f"📈 Total chunks indexed: {stats.get('total_chunks', 0)}")
        print(f"🗂️  Collection name: {stats.get('collection_name', 'N/A')}")
        print(f"🕒 Last updated: {stats.get('last_updated', 'N/A')}")
        
        # Test the system with some sample queries
        print("\n🧪 Testing with sample queries...")
        test_queries = [
            "What services does Metalogics offer?",
            "Tell me about the company history",
            "What technologies do you use?",
            "How can I contact Metalogics?",
            "What is your pricing structure?"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: {query}")
            docs = rag_service.search_documents(query, 2)
            if docs:
                print(f"   ✅ Found {len(docs)} relevant documents")
                print(f"   📄 Top result: {docs[0]['metadata']['file_name']} (score: {docs[0]['relevance_score']:.2f})")
            else:
                print("   ❌ No relevant documents found")
        
        print(f"\n🎉 Metalogics Knowledge Base is ready for use!")
        print("💡 You can now use the RAG API endpoints to search and generate answers.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())

