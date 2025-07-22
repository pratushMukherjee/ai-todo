import pytest
from backend.nodes.email_to_calendar_event_node import email_to_calendar_event_node

def test_email_to_calendar_event_node_smoke():
    dummy_state = {}
    result = email_to_calendar_event_node(dummy_state)
    assert result is not None 