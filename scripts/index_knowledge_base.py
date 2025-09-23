#!/usr/bin/env python3
"""
Script to index the knowledge base with documents and create embeddings.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "knowledge_base"))
sys.path.append(str(project_root / "backend" / "services"))

from processors.document_processor import DocumentProcessor
from rag_service import RAGService

def main():
    """Main function to index the knowledge base."""
    print("Starting knowledge base indexing...")
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1
    
    # Initialize the document processor
    processor = DocumentProcessor(
        documents_dir=str(project_root / "knowledge_base" / "metalogics_kb"),
        embeddings_dir=str(project_root / "knowledge_base" / "embeddings")
    )
    
    # Process all documents
    print("Processing documents...")
    processor.process_all_documents()
    
    # Get statistics
    print("\nGetting knowledge base statistics...")
    rag_service = RAGService()
    stats = rag_service.get_knowledge_base_stats()
    
    print(f"\nKnowledge base indexing completed!")
    print(f"Total chunks indexed: {stats.get('total_chunks', 0)}")
    print(f"Collection name: {stats.get('collection_name', 'N/A')}")
    print(f"Last updated: {stats.get('last_updated', 'N/A')}")
    
    return 0

if __name__ == "__main__":
    exit(main())
