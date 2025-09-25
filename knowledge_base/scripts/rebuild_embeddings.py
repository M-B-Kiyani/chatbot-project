#!/usr/bin/env python3
"""
Script to rebuild embeddings for the knowledge base.
This script clears existing embeddings and re-processes all documents.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "knowledge_base"))
sys.path.insert(0, str(project_root / "backend"))

from processors.document_processor import DocumentProcessor
from backend.db.database import SessionLocal
from backend.db.models import Document, DocumentChunk

def clear_existing_data(dry_run=False):
    """Clear existing documents and chunks from the database."""
    if dry_run:
        print("DRY RUN: Would clear existing documents and chunks from database")
        return

    db = SessionLocal()
    try:
        # Count existing data
        doc_count = db.query(Document).count()
        chunk_count = db.query(DocumentChunk).count()

        print(f"Clearing {doc_count} documents and {chunk_count} chunks...")

        # Delete in correct order (chunks first due to foreign key)
        db.query(DocumentChunk).delete()
        db.query(Document).delete()
        db.commit()

        print("Successfully cleared existing data")
    except Exception as e:
        db.rollback()
        print(f"Error clearing data: {str(e)}")
        raise
    finally:
        db.close()

def rebuild_embeddings(dry_run=False):
    """Rebuild embeddings by processing all documents."""
    if dry_run:
        print("DRY RUN: Would rebuild embeddings for all documents")
        return

    print("Starting embedding rebuild...")

    # Initialize document processor
    processor = DocumentProcessor(
        documents_dir=str(project_root / "knowledge_base")
    )

    # Process all documents
    processor.process_all_documents()

    print("Embedding rebuild completed")

def get_stats():
    """Get current knowledge base statistics."""
    db = SessionLocal()
    try:
        doc_count = db.query(Document).count()
        chunk_count = db.query(DocumentChunk).count()
        return doc_count, chunk_count
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Rebuild embeddings for the knowledge base")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--skip-clear",
        action="store_true",
        help="Skip clearing existing data (append mode)"
    )

    args = parser.parse_args()

    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return 1

    print("Knowledge Base Embedding Rebuild Script")
    print("=" * 40)

    # Show current stats
    try:
        doc_count, chunk_count = get_stats()
        print(f"Current state: {doc_count} documents, {chunk_count} chunks")
    except Exception as e:
        print(f"Could not get current stats: {e}")

    if args.dry_run:
        print("\nDRY RUN MODE - No changes will be made")
    else:
        print("\nPRODUCTION MODE - Changes will be applied")

    # Clear existing data unless skipped
    if not args.skip_clear:
        print("\n1. Clearing existing data...")
        clear_existing_data(args.dry_run)
    else:
        print("\n1. Skipping data clearing (append mode)...")

    # Rebuild embeddings
    print("\n2. Rebuilding embeddings...")
    rebuild_embeddings(args.dry_run)

    # Show final stats
    if not args.dry_run:
        try:
            doc_count, chunk_count = get_stats()
            print(f"\nFinal state: {doc_count} documents, {chunk_count} chunks")
        except Exception as e:
            print(f"Could not get final stats: {e}")

    print("\nRebuild process completed successfully!")
    return 0

if __name__ == "__main__":
    exit(main())