"""
API Routes for Chatbot Backend
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import sys
import os
import re
import json
from pathlib import Path
from sqlalchemy.orm import Session

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Add the services directory to the path
sys.path.append(str(Path(__file__).parent.parent / "services"))

from services.rag_service import RAGService
from db.database import get_db
from db.models import Session as SessionModel, Lead
import json
from sqlalchemy.orm import Session as DBSession

# Calendar imports
from services.calendar_service import calendar_service

# HubSpot imports
from services.hubspot_service import upsert_contact_and_add_note

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

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str

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

class HubSpotUpsertRequest(BaseModel):
    name: str
    email: str
    company: Optional[str] = None
    interest: Optional[str] = None
    session_id: str

class HubSpotUpsertResponse(BaseModel):
    hubspot_contact_id: str
    status: str

class IntentHintRequest(BaseModel):
    intent: str
    session_id: str

class LogMessageRequest(BaseModel):
    session_id: str
    user_id: Optional[int] = None
    message: str
    role: str  # "user" or "bot"
    timestamp: Optional[str] = None

class LogMessageResponse(BaseModel):
    status: str
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """
    Main chat endpoint for processing user messages using RAG.
    """
    try:
        # Search for relevant documents
        documents = rag_service.search_documents(message.message, 5)

        # Generate answer using RAG service
        result = rag_service.generate_answer(message.message, documents)

        return ChatResponse(
            response=result["answer"],
            session_id=message.session_id or "default",
            timestamp=datetime.utcnow().isoformat()
        )
    except Exception as e:
        return ChatResponse(
            response=f"Sorry, I encountered an error: {str(e)}",
            session_id=message.session_id or "default",
            timestamp=datetime.utcnow().isoformat()
        )

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

# Calendar endpoints
@router.get("/calendar/auth")
async def calendar_auth():
    """Initiate Google Calendar OAuth flow."""
    try:
        auth_url = calendar_service.initiate_oauth_flow()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth initiation failed: {str(e)}")

@router.get("/calendar/callback")
async def calendar_callback(code: str = Query(..., description="Authorization code"),
                           state: str = Query(..., description="State parameter")):
    """Handle OAuth callback."""
    try:
        success = calendar_service.complete_oauth_flow(code, state)
        if success:
            return {"message": "Authentication successful"}
        else:
            raise HTTPException(status_code=400, detail="Authentication failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

@router.get("/calendar/freebusy")
async def calendar_freebusy(start: str = Query(..., description="Start time in ISO format"),
                           end: str = Query(..., description="End time in ISO format"),
                           calendar_id: str = Query("primary", description="Calendar ID"),
                           timezone: str = Query("UTC", description="Timezone")):
    """Get free/busy information."""
    try:
        result = calendar_service.get_freebusy(start, end, calendar_id, timezone)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Freebusy query failed: {str(e)}")

@router.post("/calendar/create")
async def calendar_create_event(event_data: dict):
    """Create a calendar event."""
    try:
        summary = event_data.get("summary")
        start = event_data.get("start")
        end = event_data.get("end")
        timezone = event_data.get("timezone", "UTC")
        description = event_data.get("description")
        attendees = event_data.get("attendees", [])
        calendar_id = event_data.get("calendar_id", "primary")

        if not summary or not start or not end:
            raise HTTPException(status_code=400, detail="Missing required fields: summary, start, end")

        event_id = calendar_service.create_event(summary, start, end, timezone, description, attendees, calendar_id)
        return {"event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event creation failed: {str(e)}")

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

@router.post("/intent-hint")
async def intent_hint(request: IntentHintRequest):
    """
    Get upsell suggestions based on detected intent.

    Args:
        request: IntentHintRequest with intent and session_id

    Returns:
        Upsell suggestions with services, reasons, and pricing links
    """
    if request.intent == "web-development":
        upsells = [
            {
                "service": "SEO",
                "reason": "improves visibility",
                "pricing_link": "/api/pricing?service=seo"
            },
            {
                "service": "Graphic Design",
                "reason": "improves UX",
                "pricing_link": "/api/pricing?service=graphic-design"
            }
        ]
        return {"upsells": upsells}
    else:
        return {"upsells": []}

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

@router.post("/upsert-hubspot", response_model=HubSpotUpsertResponse)
async def upsert_hubspot(request: HubSpotUpsertRequest, db: Session = Depends(get_db)):
    """
    Upsert a HubSpot contact and link to leads table.

    Args:
        request: HubSpotUpsertRequest with name, email, company, interest, session_id

    Returns:
        HubSpot contact ID and status
    """
    try:
        # Call HubSpot upsert
        result = upsert_contact_and_add_note(
            name=request.name,
            email=request.email,
            company=request.company,
            interest=request.interest,
            session_id=request.session_id
        )

        hubspot_id = result["contact_id"]

        # Insert or update lead in database
        lead = db.query(Lead).filter(Lead.email == request.email).first()
        if lead:
            lead.hubspot_id = hubspot_id
            lead.session_id = request.session_id
            lead.name = request.name
        else:
            lead = Lead(
                hubspot_id=hubspot_id,
                session_id=request.session_id,
                email=request.email,
                name=request.name
            )
            db.add(lead)

        db.commit()

        return HubSpotUpsertResponse(
            hubspot_contact_id=hubspot_id,
            status=result["action"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HubSpot upsert failed: {str(e)}")

class ScheduleCheckRequest(BaseModel):
    user: str
    start: str  # ISO format datetime
    duration: int  # minutes
    calendar_id: Optional[str] = "primary"

class ScheduleCheckResponse(BaseModel):
    allowed: bool
    reason: str
    blocking_events: List[dict]
    suggested_slot: Optional[str] = None

@router.post("/schedule-check", response_model=ScheduleCheckResponse)
async def schedule_check(request: ScheduleCheckRequest):
    """
    Check if a booking can be made at the specified time and duration.

    Args:
        request: ScheduleCheckRequest with user, start (ISO), duration (minutes)

    Returns:
        Whether booking is allowed, reason, blocking events, and suggested alternative slot
    """
    try:
        # Check booking rules
        check_result = calendar_service.check_booking_rules(
            request.calendar_id,
            request.start,
            request.duration
        )

        # If not allowed, suggest next slot
        suggested_slot = None
        if not check_result["allowed"]:
            suggestion = calendar_service.suggest_next_slot(
                request.calendar_id,
                request.start,
                request.duration
            )
            if "slot" in suggestion:
                suggested_slot = suggestion["slot"]

        return ScheduleCheckResponse(
            allowed=check_result["allowed"],
            reason=check_result["reason"],
            blocking_events=check_result["blockingEvents"],
            suggested_slot=suggested_slot
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule check failed: {str(e)}")

class CreateBookingRequest(BaseModel):
    user: str
    start: str  # ISO format datetime
    duration: int  # minutes
    summary: str
    description: Optional[str] = None
    attendees: Optional[List[str]] = None
    calendar_id: Optional[str] = "primary"
    timezone: Optional[str] = "UTC"
    hubspot_data: Optional[dict] = None  # Optional HubSpot upsert data

class CreateBookingResponse(BaseModel):
    event_id: str
    allowed: bool
    reason: str
    hubspot_contact_id: Optional[str] = None
    hubspot_status: Optional[str] = None

@router.post("/create-booking", response_model=CreateBookingResponse)
async def create_booking(request: CreateBookingRequest, db: Session = Depends(get_db)):
    """
    Create a calendar booking after checking rules, with optional HubSpot integration.

    Args:
        request: CreateBookingRequest with booking details and optional HubSpot data

    Returns:
        Event ID, whether allowed, reason, and HubSpot details if provided
    """
    try:
        # First check if booking is allowed
        check_result = calendar_service.check_booking_rules(
            request.calendar_id,
            request.start,
            request.duration
        )

        if not check_result["allowed"]:
            return CreateBookingResponse(
                event_id="",
                allowed=False,
                reason=check_result["reason"]
            )

        # Calculate end time
        from datetime import datetime, timedelta
        start_dt = datetime.fromisoformat(request.start.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(minutes=request.duration)
        end_iso = end_dt.isoformat().replace('+00:00', 'Z')

        # Create the event
        event_id = calendar_service.create_event(
            summary=request.summary,
            start=request.start,
            end=end_iso,
            timezone=request.timezone,
            description=request.description,
            attendees=request.attendees,
            calendar_id=request.calendar_id
        )

        # Optional HubSpot integration
        hubspot_contact_id = None
        hubspot_status = None
        if request.hubspot_data:
            try:
                hubspot_result = upsert_contact_and_add_note(
                    name=request.hubspot_data.get("name"),
                    email=request.hubspot_data.get("email"),
                    company=request.hubspot_data.get("company"),
                    interest=request.hubspot_data.get("interest", "Booking Created"),
                    session_id=request.hubspot_data.get("session_id", f"booking_{event_id}")
                )
                hubspot_contact_id = hubspot_result["contact_id"]
                hubspot_status = hubspot_result["action"]

                # Link to lead in database
                lead = db.query(Lead).filter(Lead.email == request.hubspot_data.get("email")).first()
                if lead:
                    lead.hubspot_id = hubspot_contact_id
                    lead.session_id = request.hubspot_data.get("session_id", f"booking_{event_id}")
                else:
                    lead = Lead(
                        hubspot_id=hubspot_contact_id,
                        session_id=request.hubspot_data.get("session_id", f"booking_{event_id}"),
                        email=request.hubspot_data.get("email"),
                        name=request.hubspot_data.get("name")
                    )
                    db.add(lead)
                db.commit()

            except Exception as e:
                print(f"HubSpot integration failed: {e}")
                # Don't fail the booking if HubSpot fails

        return CreateBookingResponse(
            event_id=event_id,
            allowed=True,
            reason="Booking created successfully",
            hubspot_contact_id=hubspot_contact_id,
            hubspot_status=hubspot_status
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Booking creation failed: {str(e)}")



