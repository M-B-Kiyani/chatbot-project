# tests/unit/test_calendar_service.py
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from backend.services.calendar_service import CalendarService


class TestCalendarService:
    @pytest.fixture
    def calendar_service(self):
        return CalendarService()

    def create_mock_event(self, start_iso, duration_minutes, summary="Test Event"):
        """Helper to create a mock event dict."""
        start_dt = datetime.fromisoformat(start_iso.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        return {
            'id': 'event_id',
            'summary': summary,
            'start': {'dateTime': start_dt.isoformat()},
            'end': {'dateTime': end_dt.isoformat()}
        }

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_no_events_allowed(self, mock_creds, mock_build, calendar_service):
        """Test booking allowed when no conflicting events."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': []}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 15)
        assert result['allowed'] is True
        assert result['reason'] == "Within limit"
        assert result['blockingEvents'] == []

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_one_event_allowed(self, mock_creds, mock_build, calendar_service):
        """Test booking allowed with one conflicting event."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # Event at 9:30-9:45, requested at 10:00 for 15m, window 1h (9-11), overlaps
        event = self.create_mock_event('2023-10-01T09:30:00Z', 15)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 15)
        assert result['allowed'] is True
        assert result['reason'] == "Within limit"
        assert len(result['blockingEvents']) == 1

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_two_events_not_allowed(self, mock_creds, mock_build, calendar_service):
        """Test booking not allowed with two conflicting events."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        event1 = self.create_mock_event('2023-10-01T09:30:00Z', 15)
        event2 = self.create_mock_event('2023-10-01T10:30:00Z', 15)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event1, event2]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 15)
        assert result['allowed'] is False
        assert "Exceeds max 2" in result['reason']
        assert len(result['blockingEvents']) == 2

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_overlap_across_window_edge(self, mock_creds, mock_build, calendar_service):
        """Test overlap when event starts before window and ends in window."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # Window for 15m: 9-11, event 8:45-9:15 overlaps, but different category (30m vs 15m)
        event = self.create_mock_event('2023-10-01T08:45:00Z', 30)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 15)
        assert result['allowed'] is True
        assert len(result['blockingEvents']) == 0

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_back_to_back(self, mock_creds, mock_build, calendar_service):
        """Test back-to-back events within window."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # Two 15m events back-to-back: 9:45-10:00 and 10:00-10:15, requested 10:00
        event1 = self.create_mock_event('2023-10-01T09:45:00Z', 15)
        event2 = self.create_mock_event('2023-10-01T10:00:00Z', 15)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event1, event2]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:15:00Z', 15)
        assert result['allowed'] is False  # Two in window
        assert len(result['blockingEvents']) == 2

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_different_category_not_counted(self, mock_creds, mock_build, calendar_service):
        """Test events of different category don't block."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # 30m event, requested 15m
        event = self.create_mock_event('2023-10-01T09:30:00Z', 30)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 15)
        assert result['allowed'] is True
        assert len(result['blockingEvents']) == 0

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_duration_over_60_allowed(self, mock_creds, mock_build, calendar_service):
        """Test durations over 60m are allowed without check."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': []}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 90)
        assert result['allowed'] is True
        assert result['reason'] == "Duration not in rule categories"
        assert result['blockingEvents'] == []

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_all_day_ignored(self, mock_creds, mock_build, calendar_service):
        """Test all-day events are ignored."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        event = {
            'id': 'all_day',
            'summary': 'All Day',
            'start': {'date': '2023-10-01'},
            'end': {'date': '2023-10-02'}
        }
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 15)
        assert result['allowed'] is True
        assert len(result['blockingEvents']) == 0

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_30m_category(self, mock_creds, mock_build, calendar_service):
        """Test 30m duration with 2h window."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # Two 30m events in 2h window
        event1 = self.create_mock_event('2023-10-01T08:00:00Z', 30)
        event2 = self.create_mock_event('2023-10-01T10:00:00Z', 30)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event1, event2]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T09:00:00Z', 30)
        assert result['allowed'] is False
        assert "2h window" in result['reason']
        assert len(result['blockingEvents']) == 2

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_60m_category(self, mock_creds, mock_build, calendar_service):
        """Test 60m duration with 3h window."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        event = self.create_mock_event('2023-10-01T07:00:00Z', 60)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 60)
        assert result['allowed'] is True
        assert len(result['blockingEvents']) == 1

    @patch('backend.services.calendar_service.CalendarService.check_booking_rules')
    def test_suggest_next_slot_first_valid(self, mock_check, calendar_service):
        """Test suggest_next_slot returns the requested slot if valid."""
        mock_check.return_value = {'allowed': True, 'reason': 'Within limit'}

        result = calendar_service.suggest_next_slot('primary', '2023-10-01T10:00:00Z', 15)
        assert result['slot'] == '2023-10-01T10:00:00Z'
        assert result['reason'] == 'Within limit'
        mock_check.assert_called_once_with('primary', '2023-10-01T10:00:00Z', 15)

    @patch('backend.services.calendar_service.CalendarService.check_booking_rules')
    def test_suggest_next_slot_next_valid(self, mock_check, calendar_service):
        """Test suggest_next_slot finds next valid slot."""
        # First call invalid, second valid
        mock_check.side_effect = [
            {'allowed': False, 'reason': 'Exceeds limit'},
            {'allowed': True, 'reason': 'Within limit'}
        ]

        result = calendar_service.suggest_next_slot('primary', '2023-10-01T10:00:00Z', 15)
        assert result['slot'] == '2023-10-01T10:15:00Z'  # 15 min later
        assert result['reason'] == 'Within limit'
        assert mock_check.call_count == 2

    @patch('backend.services.calendar_service.CalendarService.check_booking_rules')
    def test_suggest_next_slot_no_valid(self, mock_check, calendar_service):
        """Test suggest_next_slot returns message if no valid slot found."""
        mock_check.return_value = {'allowed': False, 'reason': 'Exceeds limit'}

        result = calendar_service.suggest_next_slot('primary', '2023-10-01T10:00:00Z', 15, 1)  # 1 hour horizon
        assert 'message' in result
        assert 'No available slots found' in result['message']
        # Should be called 4 times (60/15=4)
        assert mock_check.call_count == 4

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_event_starts_at_window_start(self, mock_creds, mock_build, calendar_service):
        """Test event starting exactly at window start."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # Window for 15m: 9-11, event 9:00-9:15 (starts exactly at window start)
        event = self.create_mock_event('2023-10-01T09:00:00Z', 15)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 15)
        assert result['allowed'] is True
        assert len(result['blockingEvents']) == 1

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_event_ends_at_window_end(self, mock_creds, mock_build, calendar_service):
        """Test event ending exactly at window end."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # Window for 15m: 9-11, event 10:45-11:00 (ends exactly at window end)
        event = self.create_mock_event('2023-10-01T10:45:00Z', 15)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 15)
        assert result['allowed'] is True
        assert len(result['blockingEvents']) == 1

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_duration_16_minutes(self, mock_creds, mock_build, calendar_service):
        """Test 16m duration (fits 30m category)."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # 16m is in 30m category (2h window)
        event = self.create_mock_event('2023-10-01T09:00:00Z', 16)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 16)
        assert result['allowed'] is True  # One event allowed
        assert len(result['blockingEvents']) == 1

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_duration_31_minutes(self, mock_creds, mock_build, calendar_service):
        """Test 31m duration (fits 60m category)."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # 31m is in 60m category (3h window)
        event = self.create_mock_event('2023-10-01T08:00:00Z', 31)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 31)
        assert result['allowed'] is True  # One event allowed
        assert len(result['blockingEvents']) == 1

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_event_without_datetime(self, mock_creds, mock_build, calendar_service):
        """Test event without dateTime is ignored."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        event = {
            'id': 'no_datetime',
            'summary': 'No DateTime',
            'start': {'date': '2023-10-01'},  # date only, no dateTime
            'end': {'date': '2023-10-02'}
        }
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 15)
        assert result['allowed'] is True
        assert len(result['blockingEvents']) == 0

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_multiple_overlapping_events(self, mock_creds, mock_build, calendar_service):
        """Test multiple overlapping events in window."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        events = [
            self.create_mock_event('2023-10-01T09:00:00Z', 15),
            self.create_mock_event('2023-10-01T09:15:00Z', 15),
            self.create_mock_event('2023-10-01T09:30:00Z', 15)
        ]
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': events}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 15)
        assert result['allowed'] is False  # 3 events > 2 limit
        assert len(result['blockingEvents']) == 3

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_event_spans_entire_window(self, mock_creds, mock_build, calendar_service):
        """Test event that spans the entire window."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # Window 9-11, event 8:30-11:30 (spans entire window)
        event = self.create_mock_event('2023-10-01T08:30:00Z', 180)  # 3 hours
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 15)
        assert result['allowed'] is True  # Different category (180m >60m)
        assert len(result['blockingEvents']) == 0

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_boundary_15_to_30(self, mock_creds, mock_build, calendar_service):
        """Test boundary between 15m and 30m categories."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # 15m event, 30m request - should not block
        event = self.create_mock_event('2023-10-01T09:00:00Z', 15)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 30)
        assert result['allowed'] is True
        assert len(result['blockingEvents']) == 0

    @patch('backend.services.calendar_service.build')
    @patch('backend.services.calendar_service.CalendarService.get_credentials')
    def test_check_booking_rules_boundary_30_to_60(self, mock_creds, mock_build, calendar_service):
        """Test boundary between 30m and 60m categories."""
        mock_creds.return_value = Mock()
        mock_service = Mock()
        mock_build.return_value = mock_service
        # 30m event, 60m request - should not block
        event = self.create_mock_event('2023-10-01T08:00:00Z', 30)
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': [event]}

        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', 60)
        assert result['allowed'] is True
        assert len(result['blockingEvents']) == 0