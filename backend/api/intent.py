from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class IntentHintRequest(BaseModel):
    intent: str
    session_id: str

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
