#!/usr/bin/env python3
"""
Complete Knowledge Base Indexing Script

This script processes all files in the knowledge_base directory and indexes them
into a vector database for RAG (Retrieval-Augmented Generation) functionality.

Usage:
    python scripts/index_knowledge_base_complete.py

Requirements:
    - OPENAI_API_KEY environment variable must be set
    - Required Python packages installed (see requirements.txt)
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the knowledge_base directory to the path
sys.path.append(str(Path(__file__).parent.parent / "knowledge_base"))
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from processors.document_processor import DocumentProcessor
from services.rag_service import RAGService

def main():
    """Main function to index the knowledge base."""
    parser = argparse.ArgumentParser(description="Index knowledge base for RAG")
    parser.add_argument("--knowledge-base-dir", 
                       default=str(Path(__file__).parent.parent / "knowledge_base"),
                       help="Path to knowledge base directory")
    parser.add_argument("--embeddings-dir",
                       default=str(Path(__file__).parent.parent / "knowledge_base" / "embeddings"),
                       help="Path to embeddings directory")
    parser.add_argument("--chunk-size", type=int, default=1000,
                       help="Chunk size in tokens (default: 1000)")
    parser.add_argument("--chunk-overlap", type=int, default=200,
                       help="Chunk overlap in tokens (default: 200)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be processed without actually indexing")
    
    args = parser.parse_args()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable is not set!")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1
    
    # Initialize document processor
    print("Initializing document processor...")
    processor = DocumentProcessor(
        documents_dir=args.knowledge_base_dir,
        embeddings_dir=args.embeddings_dir
    )
    
    # Update chunking parameters
    processor.chunk_size = args.chunk_size
    processor.chunk_overlap = args.chunk_overlap
    
    print(f"Knowledge base directory: {args.knowledge_base_dir}")
    print(f"Embeddings directory: {args.embeddings_dir}")
    print(f"Chunk size: {args.chunk_size} tokens")
    print(f"Chunk overlap: {args.chunk_overlap} tokens")
    print()
    
    # Find all files that would be processed
    kb_path = Path(args.knowledge_base_dir)
    if not kb_path.exists():
        print(f"ERROR: Knowledge base directory {kb_path} does not exist!")
        return 1
    
    # Supported file extensions
    supported_extensions = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml']
    
    # Add PDF and DOCX if libraries are available
    try:
        import PyPDF2
        supported_extensions.append('.pdf')
        print("✓ PDF support available")
    except ImportError:
        print("⚠ PDF support not available (PyPDF2 not installed)")
    
    try:
        from docx import Document
        supported_extensions.append('.docx')
        print("✓ DOCX support available")
    except ImportError:
        print("⚠ DOCX support not available (python-docx not installed)")
    
    print()
    
    # Find all files
    all_files = []
    for file_path in kb_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            all_files.append(file_path)
    
    print(f"Found {len(all_files)} files to process:")
    for file_path in sorted(all_files):
        rel_path = file_path.relative_to(kb_path)
        print(f"  - {rel_path}")
    print()
    
    if args.dry_run:
        print("Dry run completed. No files were actually processed.")
        return 0
    
    # Process all documents
    print("Starting document processing...")
    start_time = datetime.now()
    
    try:
        processor.process_all_documents()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n✓ Indexing completed successfully!")
        print(f"Duration: {duration}")
        
        # Get statistics
        try:
            rag_service = RAGService()
            stats = rag_service.get_knowledge_base_stats()
            print(f"Total chunks in vector database: {stats.get('total_chunks', 'Unknown')}")
        except Exception as e:
            print(f"Could not retrieve statistics: {e}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error during indexing: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
