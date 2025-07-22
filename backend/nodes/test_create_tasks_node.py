import pytest
from backend.nodes.create_tasks_node import create_tasks_node

def test_create_tasks_node_smoke():
    dummy_state = {"emails": [{"from": "a@b.com", "subject": "Test", "body": "Hello"}], "email_idx": 0, "suggestions": ["Test Task"]}
    result = create_tasks_node(dummy_state)
    assert isinstance(result, dict) 