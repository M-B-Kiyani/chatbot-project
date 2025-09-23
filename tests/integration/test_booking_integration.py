# tests/integration/test_booking_integration.py
"""
Integration tests for booking functionality with mocked external services.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from api.routes import router
from db.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base

# Create test database
TEST_DATABASE_URL = "sqlite:///./test_booking.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    """Create a test client with test database."""
    app = FastAPI()
    app.include_router(router)

    # Override dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

class TestBookingIntegration:
    """Integration tests for booking flow."""

    @patch('backend.services.hubspot_service.requests.post')
    @patch('backend.services.hubspot_service.requests.patch')
    @patch('backend.api.routes.calendar_service.create_event')
    def test_booking_flow_success(self, mock_create_event, mock_patch, mock_post, client):
        """Test successful booking flow with mocked services."""
        # Mock calendar create_event
        mock_create_event.return_value = 'test_event_id'

        # Mock HubSpot - search returns no existing contact
        mock_post.side_effect = [
            # search_contact_by_email
            Mock(status_code=200, json=lambda: {"results": []}),
            # create_contact
            Mock(status_code=201, json=lambda: {"id": "hubspot_123"}),
            # create_note
            Mock(status_code=201, json=lambda: {"id": "note_123"})
        ]

        # Test calendar create event
        event_data = {
            "summary": "Consultation with John Doe",
            "start": "2023-10-01T10:00:00Z",
            "end": "2023-10-01T10:15:00Z",
            "timezone": "UTC",
            "description": "Booking for John Doe",
            "attendees": ["john@example.com"]
        }

        response = client.post("/calendar/create", json=event_data)
        assert response.status_code == 200
        assert response.json()["event_id"] == "test_event_id"

        # Test HubSpot upsert
        hubspot_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "company": "Test Corp",
            "interest": "web-development",
            "session_id": "session_123"
        }

        response = client.post("/upsert-hubspot", json=hubspot_data)
        assert response.status_code == 200
        assert response.json()["hubspot_contact_id"] == "hubspot_123"
        assert response.json()["status"] == "created"

    @patch('backend.services.hubspot_service.requests.post')
    @patch('backend.api.routes.calendar_service.create_event')
    def test_booking_flow_booking_rules_violation(self, mock_create_event, mock_post, client):
        """Test booking flow when booking rules are violated."""
        # Mock calendar create_event - still succeeds (rules not enforced in endpoint)
        mock_create_event.return_value = 'test_event_id'

        # Mock HubSpot
        mock_post.side_effect = [
            Mock(status_code=200, json=lambda: {"results": []}),
            Mock(status_code=201, json=lambda: {"id": "hubspot_456"}),
            Mock(status_code=201, json=lambda: {"id": "note_789"})
        ]

        # Test calendar create event - endpoint doesn't check rules
        event_data = {
            "summary": "Consultation with Jane Doe",
            "start": "2023-10-01T10:00:00Z",
            "end": "2023-10-01T10:15:00Z",
            "timezone": "UTC",
            "description": "Booking for Jane Doe",
            "attendees": ["jane@example.com"]
        }

        response = client.post("/calendar/create", json=event_data)
        assert response.status_code == 200
        assert response.json()["event_id"] == "test_event_id"

    @patch('backend.services.hubspot_service.requests.post')
    @patch('backend.services.hubspot_service.requests.patch')
    def test_hubspot_upsert_existing_contact(self, mock_patch, mock_post, client):
        """Test HubSpot upsert when contact already exists."""
        # Mock HubSpot - search returns existing contact
        mock_post.side_effect = [
            # search_contact_by_email
            Mock(status_code=200, json=lambda: {"results": [{"id": "existing_123", "properties": {}}]}),
            # create_note (no create_contact call)
            Mock(status_code=201, json=lambda: {"id": "note_456"})
        ]

        hubspot_data = {
            "name": "Existing User",
            "email": "existing@example.com",
            "company": "Updated Corp",
            "interest": "seo",
            "session_id": "session_456"
        }

        response = client.post("/upsert-hubspot", json=hubspot_data)
        assert response.status_code == 200
        assert response.json()["hubspot_contact_id"] == "existing_123"
        assert response.json()["status"] == "updated"

    @patch('backend.services.hubspot_service.requests.post')
    def test_hubspot_upsert_invalid_email(self, mock_post, client):
        """Test HubSpot upsert with invalid email."""
        hubspot_data = {
            "name": "Invalid User",
            "email": "invalid-email",
            "company": "Test Corp",
            "interest": "web-development",
            "session_id": "session_invalid"
        }

        response = client.post("/upsert-hubspot", json=hubspot_data)
        assert response.status_code == 500  # Should fail validation

    @patch('backend.api.routes.calendar_service.create_event')
    def test_calendar_create_missing_fields(self, mock_create_event, client):
        """Test calendar create with missing required fields."""
        # The endpoint checks for required fields before calling create_event
        event_data = {
            "summary": "Incomplete Event"
            # Missing start, end
        }

        response = client.post("/calendar/create", json=event_data)
        assert response.status_code == 500
        assert "Missing required fields" in response.json()["detail"]

    @patch('backend.api.routes.calendar_service.create_event')
    def test_calendar_operations_no_credentials(self, mock_create_event, client):
        """Test calendar operations when no credentials available."""
        # Mock create_event to raise exception
        mock_create_event.side_effect = Exception("No valid credentials. Please authenticate first.")

        # Test create event
        event_data = {
            "summary": "Test Event",
            "start": "2023-10-01T10:00:00Z",
            "end": "2023-10-01T11:00:00Z"
        }
        response = client.post("/calendar/create", json=event_data)
        assert response.status_code == 500
        assert "No valid credentials" in str(response.json()["detail"])

    @patch('backend.api.routes.calendar_service.check_booking_rules')
    @patch('backend.api.routes.calendar_service.suggest_next_slot')
    def test_schedule_check_allowed(self, mock_suggest, mock_check, client):
        """Test schedule_check when booking is allowed."""
        mock_check.return_value = {
            "allowed": True,
            "reason": "Within limit",
            "blockingEvents": []
        }
        # suggest_next_slot not called since allowed

        schedule_data = {
            "user": "test_user",
            "start": "2023-10-01T10:00:00Z",
            "duration": 30
        }

        response = client.post("/schedule-check", json=schedule_data)
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] is True
        assert data["reason"] == "Within limit"
        assert data["blocking_events"] == []
        assert data["suggested_slot"] is None

    @patch('backend.api.routes.calendar_service.check_booking_rules')
    @patch('backend.api.routes.calendar_service.suggest_next_slot')
    def test_schedule_check_not_allowed_with_suggestion(self, mock_suggest, mock_check, client):
        """Test schedule_check when booking is not allowed but has suggestion."""
        mock_check.return_value = {
            "allowed": False,
            "reason": "Exceeds max 2 bookings",
            "blockingEvents": [{"id": "event1", "summary": "Existing booking"}]
        }
        mock_suggest.return_value = {"slot": "2023-10-01T11:00:00Z", "reason": "Within limit"}

        schedule_data = {
            "user": "test_user",
            "start": "2023-10-01T10:00:00Z",
            "duration": 30
        }

        response = client.post("/schedule-check", json=schedule_data)
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] is False
        assert "Exceeds max 2" in data["reason"]
        assert len(data["blocking_events"]) == 1
        assert data["suggested_slot"] == "2023-10-01T11:00:00Z"

    @patch('backend.api.routes.calendar_service.check_booking_rules')
    @patch('backend.api.routes.calendar_service.suggest_next_slot')
    def test_schedule_check_not_allowed_no_suggestion(self, mock_suggest, mock_check, client):
        """Test schedule_check when booking is not allowed and no suggestion."""
        mock_check.return_value = {
            "allowed": False,
            "reason": "Exceeds max 2 bookings",
            "blockingEvents": [{"id": "event1"}]
        }
        mock_suggest.return_value = {"message": "No available slots found"}

        schedule_data = {
            "user": "test_user",
            "start": "2023-10-01T10:00:00Z",
            "duration": 30
        }

        response = client.post("/schedule-check", json=schedule_data)
        assert response.status_code == 200
        data = response.json()
        assert data["allowed"] is False
        assert data["suggested_slot"] is None

    @patch('backend.services.hubspot_service.requests.post')
    @patch('backend.api.routes.calendar_service.check_booking_rules')
    @patch('backend.api.routes.calendar_service.create_event')
    def test_create_booking_success_with_hubspot(self, mock_create_event, mock_check, mock_post, client):
        """Test successful booking creation with HubSpot integration."""
        # Mock booking rules check - allowed
        mock_check.return_value = {
            "allowed": True,
            "reason": "Within limit",
            "blockingEvents": []
        }

        # Mock calendar create_event
        mock_create_event.return_value = 'event_123'

        # Mock HubSpot - new contact
        mock_post.side_effect = [
            # search_contact_by_email
            Mock(status_code=200, json=lambda: {"results": []}),
            # create_contact
            Mock(status_code=201, json=lambda: {"id": "hubspot_789"}),
            # create_note
            Mock(status_code=201, json=lambda: {"id": "note_999"})
        ]

        booking_data = {
            "user": "test_user",
            "start": "2023-10-01T10:00:00Z",
            "duration": 30,
            "summary": "Demo Call",
            "description": "Demo booking",
            "attendees": ["test@example.com"],
            "hubspot_data": {
                "name": "Test User",
                "email": "test@example.com",
                "company": "Test Corp",
                "interest": "web-development",
                "session_id": "session_789"
            }
        }

        response = client.post("/create-booking", json=booking_data)
        assert response.status_code == 200
        data = response.json()
        assert data["event_id"] == "event_123"
        assert data["allowed"] is True
        assert data["hubspot_contact_id"] == "hubspot_789"
        assert data["hubspot_status"] == "created"

    @patch('backend.api.routes.calendar_service.check_booking_rules')
    def test_create_booking_rules_violation(self, mock_check, client):
        """Test booking creation when rules are violated."""
        # Mock booking rules check - not allowed
        mock_check.return_value = {
            "allowed": False,
            "reason": "Exceeds max 2 bookings",
            "blockingEvents": [{"id": "event1"}]
        }

        booking_data = {
            "user": "test_user",
            "start": "2023-10-01T10:00:00Z",
            "duration": 30,
            "summary": "Demo Call"
        }

        response = client.post("/create-booking", json=booking_data)
        assert response.status_code == 200
        data = response.json()
        assert data["event_id"] == ""
        assert data["allowed"] is False
        assert "Exceeds max 2" in data["reason"]
        assert data["hubspot_contact_id"] is None

    @patch('backend.services.hubspot_service.requests.post')
    @patch('backend.api.routes.calendar_service.check_booking_rules')
    @patch('backend.api.routes.calendar_service.create_event')
    def test_create_booking_without_hubspot(self, mock_create_event, mock_check, mock_post, client):
        """Test booking creation without HubSpot data."""
        # Mock booking rules check - allowed
        mock_check.return_value = {
            "allowed": True,
            "reason": "Within limit",
            "blockingEvents": []
        }

        # Mock calendar create_event
        mock_create_event.return_value = 'event_456'

        booking_data = {
            "user": "test_user",
            "start": "2023-10-01T10:00:00Z",
            "duration": 30,
            "summary": "Demo Call"
        }

        response = client.post("/create-booking", json=booking_data)
        assert response.status_code == 200
        data = response.json()
        assert data["event_id"] == "event_456"
        assert data["allowed"] is True
        assert data["hubspot_contact_id"] is None
        assert data["hubspot_status"] is None
        # HubSpot should not be called
        mock_post.assert_not_called()