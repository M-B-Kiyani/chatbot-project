# backend/services/hubspot_service.py
import os
import re
import logging
import requests
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

BASE_URL = "https://api.hubapi.com"
APP_BASE_URL = os.environ.get("APP_BASE_URL", "").rstrip("/")
SESSIONS_API_URL = os.environ.get("SESSIONS_API_URL")  # optional: e.g. http://localhost:8001

def get_headers(access_token: str) -> Dict[str, str]:
    """Get headers with access token."""
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")

def _split_name(name: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if not name:
        return None, None
    parts = name.strip().split()
    first = parts[0]
    last = " ".join(parts[1:]) if len(parts) > 1 else ""
    return first, last

def _ensure_int_if_digits(s: Any):
    s = str(s)
    return int(s) if s.isdigit() else s

def search_contact_by_email(email: str, access_token: str) -> Tuple[Optional[str], Optional[dict]]:
    """
    Returns (contact_id, properties) or (None, None) if not found.
    """
    url = f"{BASE_URL}/crm/v3/objects/contacts/search"
    payload = {
        "filterGroups": [
            {"filters": [{"propertyName": "email", "operator": "EQ", "value": email}]}
        ],
        "limit": 1,
    }
    headers = get_headers(access_token)
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", [])
    if results:
        return results[0]["id"], results[0].get("properties", {})
    return None, None

def create_contact(name: str, email: str, company: Optional[str] = None, access_token: str = None) -> str:
    url = f"{BASE_URL}/crm/v3/objects/contacts"
    first, last = _split_name(name)
    properties = {"email": email}
    if first:
        properties["firstname"] = first
    if last:
        properties["lastname"] = last
    if company:
        properties["company"] = company
    payload = {"properties": properties}
    headers = get_headers(access_token)
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()["id"]

def update_contact(contact_id: str, name: Optional[str] = None, company: Optional[str] = None, access_token: str = None) -> str:
    url = f"{BASE_URL}/crm/v3/objects/contacts/{contact_id}"
    properties = {}
    if name:
        first, last = _split_name(name)
        if first:
            properties["firstname"] = first
        if last:
            properties["lastname"] = last
    if company:
        properties["company"] = company
    if not properties:
        return contact_id
    payload = {"properties": properties}
    headers = get_headers(access_token)
    resp = requests.patch(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()["id"]

def create_note_for_contact(contact_id: str, note_body: str, timestamp_iso: Optional[str] = None, access_token: str = None) -> str:
    """
    Creates a note and associates it to the contact. Uses the 'note_to_contact' association type (HubSpot accepts snake_case).
    """
    url = f"{BASE_URL}/crm/v3/objects/notes"
    if not timestamp_iso:
        timestamp_iso = datetime.utcnow().isoformat() + "Z"
    # associationTypeId can be the snake_case id e.g. 'note_to_contact'
    associations = [
        {
            "to": {"id": _ensure_int_if_digits(contact_id)},
            "types": [
                {"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": "note_to_contact"}
            ],
        }
    ]
    payload = {
        "properties": {"hs_timestamp": timestamp_iso, "hs_note_body": note_body},
        "associations": associations,
    }
    headers = get_headers(access_token)
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()["id"]

def _fetch_session_text_from_service(session_id: str) -> Optional[str]:
    """
    Optional: try to fetch conversation text from SESSIONS_API_URL if configured.
    Expected response shape can vary; this reads common keys.
    """
    if not SESSIONS_API_URL or not session_id:
        return None
    try:
        url = SESSIONS_API_URL.rstrip("/") + f"/api/sessions/{session_id}"
        r = requests.get(url, timeout=6)
        if not r.ok:
            return None
        data = r.json()
        # try common keys
        for k in ("conversation", "transcript", "messages", "chat"):
            if k in data:
                val = data[k]
                if isinstance(val, list):
                    # attempt to join message texts if dicts
                    texts = []
                    for item in val:
                        if isinstance(item, dict):
                            # common keys
                            texts.append(item.get("text") or item.get("message") or str(item))
                        else:
                            texts.append(str(item))
                    return " ".join(texts)
                return str(val)
        # fallback: stringified JSON
        return str(data)
    except Exception as e:
        logging.debug("Failed to fetch session text: %s", e)
        return None

def upsert_contact_and_add_note(
    name: str,
    email: str,
    company: Optional[str],
    interest: Optional[str],
    session_id: Optional[str],
    conversation: Optional[str] = None,
    access_token: str = None,
) -> Dict[str, str]:
    """
    Upsert a HubSpot contact and attach a note containing:
      - first 200 chars of conversation (either provided or fetched from SESSIONS_API_URL)
      - interest and session link
    Returns dict {contact_id, note_id, action}
    """
    if not email or not EMAIL_RE.match(email):
        raise ValueError("Invalid email")

    # 1) search
    contact_id, _ = search_contact_by_email(email, access_token)

    # 2) create or update
    if contact_id:
        action = "updated"
        update_contact(contact_id, name=name, company=company, access_token=access_token)
    else:
        action = "created"
        contact_id = create_contact(name=name, email=email, company=company, access_token=access_token)

    # 3) get conversation snippet
    text = conversation or _fetch_session_text_from_service(session_id) or ""
    snippet = (text[:200] + "...") if len(text) > 200 else text

    # 4) build note
    note_lines = []
    if snippet:
        note_lines.append("Conversation (first 200 chars):")
        note_lines.append(snippet)
        note_lines.append("")  # blank line
    if interest:
        note_lines.append(f"Interest: {interest}")
    if session_id:
        link = f"{APP_BASE_URL}/session/{session_id}" if APP_BASE_URL else f"session_id:{session_id}"
        note_lines.append(f"Session link: {link}")

    note_body = "\n".join(note_lines).strip() or f"Lead from chatbot. Session: {session_id or 'N/A'}"

    note_id = create_note_for_contact(contact_id, note_body, access_token=access_token)

    return {"contact_id": str(contact_id), "note_id": str(note_id), "action": action}
