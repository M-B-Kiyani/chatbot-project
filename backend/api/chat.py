"""
Chat API endpoint for processing user messages.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from backend.services.rag_service import RAGService
from .intent import intent_hint, IntentHintRequest

router = APIRouter()

# Initialize RAG service
rag_service = RAGService()

async def detect_intent(message: str) -> str:
    """Detect user intent from message using LLM."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an intent classifier. Classify the user's message into one of these intents: web-development, seo, graphic-design, or 'none' if it doesn't match any. Return only the intent name in lowercase."},
                {"role": "user", "content": f"Message: {message}"}
            ],
            max_tokens=10,
            temperature=0.1
        )

        intent = response.choices[0].message.content.strip().lower()
        # Validate intent
        valid_intents = ["web-development", "seo", "graphic-design", "none"]
        return intent if intent in valid_intents else "none"
    except Exception as e:
        print(f"Error detecting intent: {e}")
        return "none"

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    intent_hint: Optional[str] = None
    upsell: Optional[List[dict]] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """
    Main chat endpoint for processing user messages using RAG.
    """
    print("Chat endpoint called")
    try:
        # Search for relevant documents
        documents = rag_service.search_documents(message.message, 5)

        # Generate answer using RAG service
        result = rag_service.generate_answer(message.message, documents)

        # Detect intent from user message
        print(f"Detecting intent for message: {message.message}")
        intent_hint_value = await detect_intent(message.message)
        print(f"Detected intent: {intent_hint_value}")

        # Get upsell suggestions if intent detected
        upsell = None
        if intent_hint_value != "none":
            try:
                intent_request = IntentHintRequest(intent=intent_hint_value, session_id=message.session_id or "default")
                upsell_response = await intent_hint(intent_request)
                upsell = upsell_response.get("upsells", [])
            except Exception as e:
                print(f"Error getting upsell suggestions: {e}")
                upsell = []

        return {
            "answer": result["answer"],
            "intent_hint": intent_hint_value if intent_hint_value != "none" else None,
            "upsell": upsell
        }
    except Exception as e:
        return ChatResponse(
            answer=f"Sorry, I encountered an error: {str(e)}",
            intent_hint=None,
            upsell=None
        )