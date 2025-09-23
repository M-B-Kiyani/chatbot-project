#!/usr/bin/env python3
"""
Chatbot Backend Main Entry Point
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def main():
    """Main function to initialize the backend server."""
    print("🚀 Chatbot Backend - Project scaffold initialized!")
    print("📁 Backend structure ready for development")
    print("🔧 API routes, services, and database modules available")
    
    # Check for environment variables
    env_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET', 
        'HUBSPOT_CLIENT_ID',
        'HUBSPOT_CLIENT_SECRET',
        'HUBSPOT_DEVELOPER_API_KEY',
        'PINECONE_API_KEY',
        'OPENAI_API_KEY',
        'SUPABASE_URL'
    ]
    
    print("\n🔍 Checking environment variables:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {'*' * min(len(value), 8)}...")
        else:
            print(f"  ❌ {var}: Not set")
    
    print("\n📋 Next steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Configure your .env file with required keys")
    print("  3. Run: python main.py")

# if __name__ == "__main__":
#     main()

from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from services.rag_service import RAGService
from db.database import create_tables

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

# @app.on_event("startup")
# async def startup_event():
#     """Initialize the RAG system and create database tables on startup."""
#     print("Starting system initialization...")
#     try:
#         # Create database tables
#         create_tables()
#         print("Database tables created successfully!")

#         # Initialize RAG system
#         rag_service = RAGService()
#         rag_service.process_knowledge_base()
#         print("RAG system initialized successfully!")

#     except Exception as e:
#         print(f"Error initializing system: {e}")
#         print("The system will continue but some functionality may not work properly.")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "rag-backend"}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "RAG Backend API",
        "endpoints": {
            "search": "/api/rag-search?q=your_query",
            "health": "/health",
            "docs": "/docs"
        }
    }

