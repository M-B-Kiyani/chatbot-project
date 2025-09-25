"""
API Routes for Chatbot Backend
"""

print("Routes module loaded")

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
import os
import re
import json
from pathlib import Path
from sqlalchemy.orm import Session


from backend.services.rag_service import RAGService
from backend.db.database import get_db
from backend.db.models import Session as SessionModel, Lead
import json
from sqlalchemy.orm import Session as DBSession
import httpx


router = APIRouter()

# Initialize RAG service
rag_service = RAGService()

# Pricing templates
pricing_templates = {
    "web-development": {
        "service": "web-development",
        "duration_options": [
            {"duration": "1 month", "price": 1500, "breakdown": "Design: $500, Development: $800, Testing: $200"},
            {"duration": "2 months", "price": 2500, "breakdown": "Design: $700, Development: $1400, Testing: $400"},
            {"duration": "3 months", "price": 3500, "breakdown": "Design: $900, Development: $2000, Testing: $600"}
        ],
        "default_cta": "Get Started"
    },
    "seo": {
        "service": "seo",
        "duration_options": [
            {"duration": "1 month", "price": 800, "breakdown": "Keyword Research: $200, On-page: $300, Off-page: $300"},
            {"duration": "3 months", "price": 2000, "breakdown": "Keyword Research: $400, On-page: $900, Off-page: $700"},
            {"duration": "6 months", "price": 3500, "breakdown": "Keyword Research: $600, On-page: $1500, Off-page: $1400"}
        ],
        "default_cta": "Optimize Now"
    },
    "graphic-design": {
        "service": "graphic-design",
        "duration_options": [
            {"duration": "1 week", "price": 300, "breakdown": "Concept: $100, Design: $150, Revisions: $50"},
            {"duration": "2 weeks", "price": 500, "breakdown": "Concept: $150, Design: $250, Revisions: $100"},
            {"duration": "1 month", "price": 800, "breakdown": "Concept: $200, Design: $400, Revisions: $200"}
        ],
        "default_cta": "Design My Brand"
    }
}

class RAGSearchResponse(BaseModel):
    query: str
    documents: List[dict]
    total_results: int
    timestamp: str

class RAGAnswerResponse(BaseModel):
    query: str
    answer: str
    documents_used: List[dict]
    timestamp: str


class LogMessageRequest(BaseModel):
    session_id: str
    user_id: Optional[int] = None
    message: str
    role: str  # "user" or "bot"
    timestamp: Optional[str] = None

class LogMessageResponse(BaseModel):
    status: str
    session_id: str


@router.get("/rag-search", response_model=RAGSearchResponse)
async def rag_search(
    q: str = Query(..., description="Search query"),
    n_results: int = Query(5, description="Number of results to return", ge=1, le=20)
):
    """
    Search the knowledge base for relevant documents.
    
    Args:
        q: Search query
        n_results: Number of results to return (1-20)
        
    Returns:
        List of relevant documents with metadata and relevance scores
        Format: {text, file_name, score} for each document
    """
    try:
        # Search for relevant documents
        documents = rag_service.search_documents(q, n_results)
        
        # Format documents to match expected output format
        formatted_docs = []
        for doc in documents:
            formatted_doc = {
                "text": doc.get("content", ""),
                "file_name": doc.get("metadata", {}).get("file_name", "unknown"),
                "score": doc.get("relevance_score", 0.0),
                "file_path": doc.get("metadata", {}).get("file_path", ""),
                "chunk_index": doc.get("metadata", {}).get("chunk_index", 0)
            }
            formatted_docs.append(formatted_doc)
        
        return RAGSearchResponse(
            query=q,
            documents=formatted_docs,
            total_results=len(formatted_docs),
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/rag-answer")
async def rag_answer(
    query: str,
    session_context: Optional[str] = None,
    relevance_threshold: float = 0.7
):
    """
    Generate an answer using RAG (Retrieval-Augmented Generation).
    
    Args:
        query: User's question
        session_context: Optional session context
        relevance_threshold: Minimum relevance score for documents (0.0-1.0)
        
    Returns:
        Generated answer with source documents and confidence metrics
    """
    try:
        # Search for relevant documents
        documents = rag_service.search_documents(query, 5)
        
        # Generate answer using retrieved documents
        result = rag_service.generate_answer(query, documents, session_context, relevance_threshold)
        
        return {
            "query": query,
            "answer": result["answer"],
            "confidence": result["confidence"],
            "reason": result["reason"],
            "documents_used": result["documents_used"],
            "avg_relevance": result.get("avg_relevance", 0.0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")

@router.get("/knowledge")
async def get_knowledge_base():
    """Retrieve knowledge base information and statistics."""
    try:
        stats = rag_service.get_knowledge_base_stats()
        return {
            "message": "Knowledge base endpoint ready",
            "stats": stats
        }
    except Exception as e:
        return {
            "message": "Knowledge base endpoint ready",
            "error": str(e)
        }

@router.post("/knowledge/process")
async def process_knowledge_base():
    """Process all documents in the knowledge base."""
    try:
        rag_service.process_knowledge_base()
        return {
            "message": "Knowledge base processing completed",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge base processing failed: {str(e)}")


@router.get("/pricing")
async def get_pricing(service: str = Query(..., description="Service type")):
    """
    Get pricing information for a specific service.

    Args:
        service: The service type (e.g., web-development, seo, graphic-design)

    Returns:
        Pricing card with service details, duration options, and default CTA
    """
    if service not in pricing_templates:
        raise HTTPException(status_code=404, detail="Service not found")
    return pricing_templates[service]


@router.post("/api/log-message", response_model=LogMessageResponse)
async def log_message(request: LogMessageRequest, db: DBSession = Depends(get_db)):
    """
    Log a message to the session's messages JSON.

    Args:
        request: LogMessageRequest with session_id, user_id, message, role

    Returns:
        Status and session_id
    """
    # Get or create session
    session = db.query(SessionModel).filter(SessionModel.session_id == request.session_id).first()
    if not session:
        session = SessionModel(
            session_id=request.session_id,
            user_id=request.user_id,
            messages=json.dumps([])
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # Load current messages
    messages = json.loads(session.messages) if session.messages else []

    # Append new message
    new_message = {
        "role": request.role,
        "content": request.message,
        "timestamp": request.timestamp or datetime.utcnow().isoformat()
    }
    messages.append(new_message)

    # Save back
    session.messages = json.dumps(messages)
    db.commit()

    return LogMessageResponse(status="logged", session_id=request.session_id)


