#!/usr/bin/env python3
"""
Chatbot Backend Main Entry Point
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%S%z'
)

# Add the project root to Python path for imports
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))

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

from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware

print("Main module loaded")
from backend.api.routes import router
from backend.api.calender import router as calendar_router
from backend.api.chat import router as chat_router
from backend.api.hubspot import router as hubspot_router
from backend.api.intent import router as intent_router
from backend.api.health import router as health_router
from backend.services.rag_service import RAGService
from backend.db.database import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the RAG system and create database tables on startup."""
    logging.info("Starting system initialization")
    try:
        # Create database tables
        create_tables()
        logging.info("Database tables created successfully")

        # Initialize RAG system
        rag_service = RAGService()
        rag_service.process_knowledge_base()
        logging.info("RAG system initialized successfully")

    except Exception as e:
        logging.error(f"Error initializing system: {e}")
        logging.warning("The system will continue but some functionality may not work properly.")
    yield

app = FastAPI(lifespan=lifespan)

# Get allowed origins from environment
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000,http://localhost:4173,http://127.0.0.1:4173')
allow_origins_list = [origin.strip() for origin in allowed_origins.split(',') if origin.strip()]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(calendar_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(hubspot_router, prefix="/api")
app.include_router(intent_router, prefix="/api")
app.include_router(health_router, prefix="/api")

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

