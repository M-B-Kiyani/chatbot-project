from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from services.calendar_service import calendar_service
from db.database import get_db
from db.models import Lead
from services.hubspot_service import upsert_contact_and_add_note

router = APIRouter()

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
                            state: str = Query(..., description="State parameter"),
                            db: Session = Depends(get_db)):
    """Handle OAuth callback."""
    try:
        success = calendar_service.complete_oauth_flow(db, code, state)
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
                            timezone: str = Query("UTC", description="Timezone"),
                            db: Session = Depends(get_db)):
    """Get free/busy information."""
    try:
        result = calendar_service.get_freebusy(db, start, end, calendar_id, timezone)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Freebusy query failed: {str(e)}")

@router.post("/calendar/create")
async def calendar_create_event(event_data: dict, db: Session = Depends(get_db)):
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

        event_id = calendar_service.create_event(db, summary, start, end, timezone, description, attendees, calendar_id)
        return {"event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event creation failed: {str(e)}")

@router.post("/schedule-check", response_model=ScheduleCheckResponse)
async def schedule_check(request: ScheduleCheckRequest, db: Session = Depends(get_db)):
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
            db,
            request.calendar_id,
            request.start,
            request.duration
        )

        # If not allowed, suggest next slot
        suggested_slot = None
        if not check_result["allowed"]:
            suggestion = calendar_service.suggest_next_slot(
                db,
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
            db,
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
        start_dt = datetime.fromisoformat(request.start.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(minutes=request.duration)
        end_iso = end_dt.isoformat().replace('+00:00', 'Z')

        # Create the event
        event_id = calendar_service.create_event(
            db,
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
