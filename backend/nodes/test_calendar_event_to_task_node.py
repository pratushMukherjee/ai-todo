import pytest
from backend.nodes.calendar_event_to_task_node import calendar_event_to_task_node

def test_calendar_event_to_task_node_smoke():
    dummy_state = type('Dummy', (), {"event_id": "dummy_event_id"})()
    result = calendar_event_to_task_node(dummy_state)
    assert result is not None 