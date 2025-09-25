#!/usr/bin/env python3
"""
Test script to simulate 5 booking scenarios and validate rule enforcement.
This script tests the booking rules logic with various edge cases and scenarios.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from services.calendar_service import calendar_service

def create_mock_event(start_iso, duration_minutes, summary="Test Event"):
    """Helper to create a mock event dict."""
    start_dt = datetime.fromisoformat(start_iso.replace('Z', '+00:00'))
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    return {
        'id': 'event_id',
        'summary': summary,
        'start': {'dateTime': start_dt.isoformat()},
        'end': {'dateTime': end_dt.isoformat()}
    }

def setup_mock_events(scenario):
    """Set up mock events for each scenario."""
    base_time = "2023-10-01T10:00:00Z"

    scenarios = {
        1: {
            "name": "Scenario 1: No conflicting events - should allow booking",
            "events": [],
            "expected": True,
            "reason": "Within limit"
        },
        2: {
            "name": "Scenario 2: One conflicting 15m event - should allow booking",
            "events": [create_mock_event("2023-10-01T09:30:00Z", 15)],
            "expected": True,
            "reason": "Within limit"
        },
        3: {
            "name": "Scenario 3: Two conflicting 15m events - should deny booking",
            "events": [
                create_mock_event("2023-10-01T09:30:00Z", 15),
                create_mock_event("2023-10-01T09:45:00Z", 15)
            ],
            "expected": False,
            "reason": "Exceeds max 2 bookings"
        },
        4: {
            "name": "Scenario 4: 30m booking with one conflicting 30m event - should allow",
            "events": [create_mock_event("2023-10-01T08:00:00Z", 30)],
            "duration": 30,
            "expected": True,
            "reason": "Within limit"
        },
        5: {
            "name": "Scenario 5: 90m booking (should bypass rules) - should allow",
            "events": [
                create_mock_event("2023-10-01T07:00:00Z", 90),
                create_mock_event("2023-10-01T08:00:00Z", 90)
            ],
            "duration": 90,
            "expected": True,
            "reason": "Duration not in rule categories"
        }
    }

    return scenarios.get(scenario, {})

def run_booking_scenario(scenario_num):
    """Run a single booking scenario."""
    scenario = setup_mock_events(scenario_num)
    if not scenario:
        print(f"ERROR: Scenario {scenario_num}: Invalid scenario number")
        return False

    print(f"\nTesting {scenario['name']}")

    # Mock the get_events method to return our test events
    original_get_events = calendar_service.get_events
    calendar_service.get_events = lambda *args, **kwargs: scenario["events"]

    try:
        duration = scenario.get("duration", 15)
        result = calendar_service.check_booking_rules('primary', '2023-10-01T10:00:00Z', duration)

        allowed = result['allowed']
        reason = result['reason']
        blocking_count = len(result['blockingEvents'])

        print(f"   Duration: {duration} minutes")
        print(f"   Events in window: {len(scenario['events'])}")
        print(f"   Blocking events: {blocking_count}")
        print(f"   Result: {'ALLOWED' if allowed else 'DENIED'}")
        print(f"   Reason: {reason}")

        expected = scenario['expected']
        if allowed == expected:
            print(f"   PASS: Expected {'allowed' if expected else 'denied'}, got {'allowed' if allowed else 'denied'}")
            return True
        else:
            print(f"   FAIL: Expected {'allowed' if expected else 'denied'}, got {'allowed' if allowed else 'denied'}")
            return False

    finally:
        # Restore original method
        calendar_service.get_events = original_get_events

def main():
    """Run all 5 booking scenarios."""
    print("Booking Rules Validation Test")
    print("=" * 50)

    passed = 0
    total = 5

    for scenario in range(1, 6):
        if run_booking_scenario(scenario):
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} scenarios passed")

    if passed == total:
        print("All booking rule validations passed!")
        return 0
    else:
        print("Some booking rule validations failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())