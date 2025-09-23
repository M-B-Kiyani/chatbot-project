#!/usr/bin/env python3
"""
Test Document Processing Without API Key

This script tests the document processing functionality without requiring
an OpenAI API key, so you can verify the system works before setting up the API.
"""

import os
import sys
from pathlib import Path

# Add the knowledge_base directory to the path
sys.path.append(str(Path(__file__).parent.parent / "knowledge_base"))

def test_file_reading():
    """Test reading different file types."""
    print("Testing file reading capabilities...")
    
    kb_path = Path(__file__).parent.parent / "knowledge_base"
    
    # Test reading markdown files
    md_files = list(kb_path.rglob("*.md"))
    print(f"Found {len(md_files)} markdown files")
    
    for md_file in md_files[:3]:  # Test first 3 files
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"  ✓ {md_file.name}: {len(content)} characters")
        except Exception as e:
            print(f"  ✗ {md_file.name}: {e}")
    
    # Test reading text files
    txt_files = list(kb_path.rglob("*.txt"))
    print(f"\nFound {len(txt_files)} text files")
    
    for txt_file in txt_files[:3]:  # Test first 3 files
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"  ✓ {txt_file.name}: {len(content)} characters")
        except Exception as e:
            print(f"  ✗ {txt_file.name}: {e}")

def test_chunking():
    """Test text chunking functionality."""
    print("\nTesting text chunking...")
    
    try:
        import tiktoken
        
        # Initialize tokenizer
        tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Test text
        test_text = """
        This is a test document with multiple sentences. 
        It contains various information that should be chunked properly.
        The chunking algorithm should split this text into manageable pieces.
        Each chunk should have some overlap with the previous chunk.
        This ensures that important information is not lost at chunk boundaries.
        """
        
        # Tokenize
        tokens = tokenizer.encode(test_text)
        print(f"  Original text: {len(tokens)} tokens")
        
        # Chunk with 50 tokens and 10 token overlap
        chunk_size = 50
        chunk_overlap = 10
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = min(start + chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            start = end - chunk_overlap
            if start >= len(tokens):
                break
        
        print(f"  Created {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks):
            print(f"    Chunk {i+1}: {len(tokenizer.encode(chunk))} tokens")
            print(f"      Preview: {chunk[:50]}...")
        
        return True
        
    except ImportError:
        print("  ✗ tiktoken not available")
        return False
    except Exception as e:
        print(f"  ✗ Chunking test failed: {e}")
        return False

def test_document_processor():
    """Test the document processor without API calls."""
    print("\nTesting document processor...")
    
    try:
        from processors.document_processor import DocumentProcessor
        
        # Create processor (this will fail on API calls but we can test file reading)
        processor = DocumentProcessor(
            documents_dir=str(Path(__file__).parent.parent / "knowledge_base"),
            embeddings_dir=str(Path(__file__).parent.parent / "knowledge_base" / "embeddings")
        )
        
        # Test processing a single file
        kb_path = Path(__file__).parent.parent / "knowledge_base"
        test_files = list(kb_path.rglob("*.md"))[:1]  # Test first markdown file
        
        if test_files:
            test_file = test_files[0]
            print(f"  Testing with: {test_file.name}")
            
            # Test file reading
            content = processor._read_file_content(test_file)
            print(f"    File content: {len(content)} characters")
            
            # Test content cleaning
            cleaned = processor._clean_content(content)
            print(f"    Cleaned content: {len(cleaned)} characters")
            
            # Test chunking
            chunks = processor._chunk_text(cleaned)
            print(f"    Created {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
                print(f"      Chunk {i+1}: {len(chunk)} characters")
                print(f"        Preview: {chunk[:100]}...")
            
            return True
        else:
            print("  No test files found")
            return False
            
    except Exception as e:
        print(f"  ✗ Document processor test failed: {e}")
        return False

def main():
    """Main test function."""
    print("DOCUMENT PROCESSING TEST (No API Key Required)")
    print("=" * 60)
    
    tests = [
        ("File Reading", test_file_reading),
        ("Text Chunking", test_chunking),
        ("Document Processor", test_document_processor)
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
        print("\n🎉 All document processing tests passed!")
        print("The system is ready for indexing once you set your OpenAI API key.")
        print("\nNext steps:")
        print("1. Set your OpenAI API key: export OPENAI_API_KEY='your-key'")
        print("2. Run: python scripts/index_knowledge_base_complete.py")
        print("3. Start the server: uvicorn backend.main:app --reload")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check the issues above.")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    exit(main())
