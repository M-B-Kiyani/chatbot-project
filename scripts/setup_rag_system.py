#!/usr/bin/env python3
"""
RAG System Setup Script

This script sets up the complete RAG system by:
1. Checking dependencies
2. Indexing the knowledge base
3. Running tests
4. Starting the API server

Usage:
    python scripts/setup_rag_system.py [--skip-index] [--skip-tests] [--start-server]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    required_packages = [
        "openai",
        "chromadb", 
        "tiktoken",
        "fastapi",
        "uvicorn"
    ]
    
    optional_packages = [
        "PyPDF2",
        "python-docx"
    ]
    
    missing_required = []
    missing_optional = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            missing_required.append(package)
            print(f"  ✗ {package}")
    
    for package in optional_packages:
        try:
            __import__(package)
            print(f"  ✓ {package} (optional)")
        except ImportError:
            missing_optional.append(package)
            print(f"  ⚠ {package} (optional - PDF/DOCX support)")
    
    if missing_required:
        print(f"\nERROR: Missing required packages: {missing_required}")
        print("Please install them with: pip install -r backend/requirements.txt")
        return False
    
    if missing_optional:
        print(f"\nWARNING: Missing optional packages: {missing_optional}")
        print("PDF and DOCX files will not be processed.")
        print("Install with: pip install PyPDF2 python-docx")
    
    return True

def check_environment():
    """Check environment variables."""
    print("\nChecking environment...")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("  ✗ OPENAI_API_KEY not set")
        print("  Please set your OpenAI API key:")
        print("  export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    print("  ✓ OPENAI_API_KEY is set")
    return True

def index_knowledge_base():
    """Index the knowledge base."""
    print("\nIndexing knowledge base...")
    
    script_path = Path(__file__).parent / "index_knowledge_base_complete.py"
    
    try:
        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("  ✓ Knowledge base indexed successfully")
            return True
        else:
            print(f"  ✗ Indexing failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ✗ Indexing timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"  ✗ Indexing error: {e}")
        return False

def run_tests():
    """Run system tests."""
    print("\nRunning tests...")
    
    script_path = Path(__file__).parent / "test_rag_system_complete.py"
    
    try:
        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("  ✓ All tests passed")
            return True
        else:
            print(f"  ✗ Tests failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ✗ Tests timed out (2 minutes)")
        return False
    except Exception as e:
        print(f"  ✗ Test error: {e}")
        return False

def start_server():
    """Start the API server."""
    print("\nStarting API server...")
    print("Server will be available at: http://localhost:8000")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")

def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup RAG system")
    parser.add_argument("--skip-index", action="store_true", help="Skip knowledge base indexing")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--start-server", action="store_true", help="Start the API server after setup")
    
    args = parser.parse_args()
    
    print("RAG SYSTEM SETUP")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check environment
    if not check_environment():
        return 1
    
    # Index knowledge base
    if not args.skip_index:
        if not index_knowledge_base():
            print("\nSetup failed during indexing.")
            return 1
    else:
        print("\nSkipping knowledge base indexing")
    
    # Run tests
    if not args.skip_tests:
        if not run_tests():
            print("\nSetup completed with test failures.")
            print("You may still be able to use the system.")
        else:
            print("\n✓ Setup completed successfully!")
    else:
        print("\nSkipping tests")
        print("✓ Setup completed!")
    
    # Start server
    if args.start_server:
        start_server()
    else:
        print("\nTo start the API server, run:")
        print("uvicorn backend.main:app --reload")
        print("\nThen visit: http://localhost:8000/docs")
    
    return 0

if __name__ == "__main__":
    exit(main())
