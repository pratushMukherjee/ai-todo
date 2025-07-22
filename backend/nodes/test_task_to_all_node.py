import pytest
from backend.nodes.task_to_all_node import task_to_all_node

def test_task_to_all_node_smoke():
    dummy_state = {"task_title": "Test Task", "start_dt": None, "end_dt": None}
    result = task_to_all_node(dummy_state)
    assert isinstance(result, dict) 