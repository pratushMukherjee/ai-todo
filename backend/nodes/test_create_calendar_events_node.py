import pytest
from backend.nodes.create_calendar_events_node import create_calendar_events_node

def test_create_calendar_events_node_smoke():
    dummy_state = {"emails": [{"from": "a@b.com", "subject": "Test", "body": "Hello"}], "email_idx": 0, "parsed": {"dates": ["2024-01-01T09:00:00"]}}
    result = create_calendar_events_node(dummy_state)
    assert isinstance(result, dict) 