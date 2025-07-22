import pytest
from backend.nodes.suggest_tasks_node import suggest_tasks_node

def test_suggest_tasks_node_smoke():
    dummy_state = {"emails": [{"from": "a@b.com", "subject": "Test", "body": "Hello"}], "email_idx": 0}
    result = suggest_tasks_node(dummy_state)
    assert isinstance(result, dict) 