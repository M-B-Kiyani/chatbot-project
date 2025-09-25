# backend/services/calendar_service.py
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from pathlib import Path
from sqlalchemy.orm import Session

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from services.google_token_manager import google_token_manager


# backend/services/calendar_service.py (pseudocode)
from datetime import datetime, timedelta

def check_booking_limits(existing_events, requested_start, duration_minutes):
    # existing_events: list of datetimes/durations for the user
    # enforce:
    # - max 2 bookings of 15m in rolling 1 hour
    # - max 2 bookings of 30m in rolling 2 hours
    # - max 2 bookings of 60m in rolling 3 hours
    windows = {15: 60, 30: 120, 60: 180}
    for d, window_minutes in windows.items():
        if duration_minutes == d:
            window_start = requested_start - timedelta(minutes=window_minutes)
            count = sum(1 for ev in existing_events if ev.start >= window_start and ev.duration == d)
            if count >= 2:
                return False, f"Limit for {d}-minute bookings reached in the last {window_minutes//60} hours."
    return True, ""


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.events']

class CalendarService:
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/calendar/callback')
        self.user_id = os.getenv('GOOGLE_USER_ID', 'default')  # For single user, can be configured

    def get_credentials(self, db: Session) -> Optional[Credentials]:
        """Get valid credentials for Google API."""
        token_data = google_token_manager.get_token(db, self.user_id)
        if not token_data:
            return None

        creds = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=SCOPES
        )

        # If expired and has refresh token, refresh it
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save the refreshed token
                google_token_manager.save_token(
                    db, self.user_id, creds.token, creds.refresh_token,
                    datetime.utcnow() + timedelta(seconds=creds.expiry.timestamp() - datetime.utcnow().timestamp()) if creds.expiry else None
                )
            except Exception as e:
                print(f"Token refresh failed: {e}")
                return None

        return creds

    def initiate_oauth_flow(self) -> str:
        """Initiate OAuth flow and return authorization URL."""
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        # Store state for verification (using a simple in-memory or file approach for now)
        # In production, this should be stored securely
        with open(Path(__file__).parent.parent / 'oauth_state.json', 'w') as f:
            json.dump({'state': state}, f)
        return authorization_url

    def complete_oauth_flow(self, db: Session, code: str, state: str) -> bool:
        """Complete OAuth flow with authorization code."""
        try:
            # Verify state
            state_file = Path(__file__).parent.parent / 'oauth_state.json'
            if state_file.exists():
                with open(state_file, 'r') as f:
                    stored_state = json.load(f).get('state')
                if stored_state != state:
                    return False

            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uris": [self.redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token"
                    }
                },
                SCOPES
            )
            flow.redirect_uri = self.redirect_uri
            flow.fetch_token(code=code)

            creds = flow.credentials
            # Save the credentials using the token manager
            google_token_manager.save_token(
                db, self.user_id, creds.token, creds.refresh_token,
                datetime.utcnow() + timedelta(seconds=creds.expiry.timestamp() - datetime.utcnow().timestamp()) if creds.expiry else None,
                ' '.join(SCOPES)
            )

            # Clean up state file
            if state_file.exists():
                state_file.unlink()

            return True
        except Exception as e:
            print(f"OAuth completion failed: {e}")
            return False

    def get_freebusy(self, db: Session, start: str, end: str, calendar_id: str = 'primary', timezone: str = 'UTC') -> Dict[str, Any]:
        """Get free/busy information for a calendar."""
        creds = self.get_credentials(db)
        if not creds:
            raise Exception("No valid credentials. Please authenticate first.")

        try:
            service = build('calendar', 'v3', credentials=creds)

            body = {
                "timeMin": start,
                "timeMax": end,
                "timeZone": timezone,
                "items": [{"id": calendar_id}]
            }

            result = service.freebusy().query(body=body).execute()
            return result
        except HttpError as error:
            raise Exception(f"Freebusy query failed: {error}")

    def get_events(self, db: Session, calendar_id: str, time_min: str, time_max: str) -> List[Dict[str, Any]]:
        """Get calendar events between time_min and time_max."""
        creds = self.get_credentials(db)
        if not creds:
            raise Exception("No valid credentials. Please authenticate first.")

        try:
            service = build('calendar', 'v3', credentials=creds)
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])
        except HttpError as error:
            raise Exception(f"Events query failed: {error}")

    def check_booking_rules(self, db: Session, calendarId: str, requestedStartISO: str, durationMinutes: int) -> Dict[str, Any]:
        """Check if a booking can be made based on rules."""
        # Determine category and window hours
        if durationMinutes <= 15:
            window_hours = 1
            category = 15
        elif durationMinutes <= 30:
            window_hours = 2
            category = 30
        elif durationMinutes <= 60:
            window_hours = 3
            category = 60
        else:
            return {"allowed": True, "reason": "Duration exceeds maximum allowed (60 minutes)", "blockingEvents": []}

        # Parse requested start time
        start_dt = datetime.fromisoformat(requestedStartISO.replace('Z', '+00:00'))

        # Define rolling window: from start - window_hours to start
        window_start = start_dt - timedelta(hours=window_hours)
        window_end = start_dt

        # Query events in the rolling window
        query_start = window_start.isoformat()
        query_end = window_end.isoformat()
        events = self.get_events(db, calendarId, query_start, query_end)

        # Helper to get category
        def get_category(dur_min: float) -> Optional[int]:
            if dur_min <= 15:
                return 15
            elif dur_min <= 30:
                return 30
            elif dur_min <= 60:
                return 60
            return None

        blocking_events = []
        count = 0

        for event in events:
            if 'dateTime' not in event.get('start', {}):
                continue  # Skip all-day events

            event_start_str = event['start']['dateTime']
            event_end_str = event['end']['dateTime']
            event_start = datetime.fromisoformat(event_start_str.replace('Z', '+00:00'))
            event_end = datetime.fromisoformat(event_end_str.replace('Z', '+00:00'))
            dur = (event_end - event_start).total_seconds() / 60

            if get_category(dur) == category:
                # Event starts within the rolling window
                if window_start <= event_start < window_end:
                    count += 1
                    blocking_events.append(event)

        allowed = count < 2
        if allowed:
            reason = f"Booking allowed. Current count: {count} in last {window_hours} hour(s)."
        else:
            reason = f"Booking rejected: Maximum of 2 {category}-minute bookings allowed in the last {window_hours} hour(s). Current count: {count}."
        return {"allowed": allowed, "reason": reason, "blockingEvents": blocking_events}

    def suggest_next_slot(self, db: Session, calendarId: str, requestedStartISO: str, durationMinutes: int, searchHorizonHours: int = 72) -> Dict[str, Any]:
        """Suggest the next valid slot by scanning future slots in 15-minute increments."""
        start_dt = datetime.fromisoformat(requestedStartISO.replace('Z', '+00:00'))
        horizon_end = start_dt + timedelta(hours=searchHorizonHours)
        current = start_dt

        while current < horizon_end:
            slot_iso = current.isoformat().replace('+00:00', '') + 'Z'
            check = self.check_booking_rules(db, calendarId, slot_iso, durationMinutes)
            if check['allowed']:
                return {"slot": slot_iso, "reason": check['reason']}
            current += timedelta(minutes=15)

        return {"message": f"No available slots found within the next {searchHorizonHours} hours. Please try a different time or contact support for assistance."}

    def create_event(self, db: Session, summary: str, start: str, end: str, timezone: str = 'UTC',
                    description: Optional[str] = None, attendees: Optional[List[str]] = None,
                    calendar_id: str = 'primary') -> str:
        """Create a calendar event."""
        creds = self.get_credentials(db)
        if not creds:
            raise Exception("No valid credentials. Please authenticate first.")

        try:
            service = build('calendar', 'v3', credentials=creds)

            event = {
                'summary': summary,
                'description': description or '',
                'start': {
                    'dateTime': start,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end,
                    'timeZone': timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }

            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            event = service.events().insert(calendarId=calendar_id, body=event).execute()
            return event.get('id')
        except HttpError as error:
            raise Exception(f"Event creation failed: {error}")

# Global instance
calendar_service = CalendarService()