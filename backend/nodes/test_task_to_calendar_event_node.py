import pytest
from backend.nodes.task_to_calendar_event_node import task_to_calendar_event_node

def test_task_to_calendar_event_node_smoke():
    dummy_state = type('Dummy', (), {"task_title": "Test Task", "start_dt": None, "end_dt": None})()
    result = task_to_calendar_event_node(dummy_state)
    assert result is not None 