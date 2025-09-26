from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.services.hubspot_service import search_contact_by_email, create_contact, update_contact

router = APIRouter()

class SimpleHubSpotUpsertRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None

class HubSpotUpsertResponse(BaseModel):
    hubspot_contact_id: str
    status: str

@router.post("/upsert-hubspot", response_model=HubSpotUpsertResponse)
async def upsert_hubspot(request: SimpleHubSpotUpsertRequest):
    """
    Upsert a HubSpot contact.

    Args:
        request: SimpleHubSpotUpsertRequest with name, email, company

    Returns:
        HubSpot contact ID
    """
    try:
        # Search for existing contact
        contact_id, _ = search_contact_by_email(request.email)

        if contact_id:
            # Update existing contact
            contact_id = update_contact(contact_id, name=request.name, company=request.company)
            status = "updated"
        else:
            # Create new contact
            contact_id = create_contact(request.name, request.email, request.company)
            status = "created"

        return HubSpotUpsertResponse(hubspot_contact_id=contact_id, status=status)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HubSpot upsert failed: {str(e)}")


@router.get("/hubspot/auth")
async def hubspot_auth():
    """Initiate HubSpot OAuth flow."""
    try:
        # For HubSpot, OAuth is typically handled differently, but for simplicity, we'll return a placeholder
        # In a real implementation, you'd redirect to HubSpot's OAuth URL
        auth_url = "https://app.hubspot.com/oauth/authorize?client_id=YOUR_CLIENT_ID&scope=contacts&redirect_uri=YOUR_REDIRECT_URI"
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth initiation failed: {str(e)}")
