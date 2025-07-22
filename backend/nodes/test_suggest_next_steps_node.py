import pytest
from backend.nodes.suggest_next_steps_node import suggest_next_steps_node

def test_suggest_next_steps_node_smoke():
    dummy_state = {"emails": [{"from": "a@b.com", "subject": "Test", "body": "Hello"}], "email_idx": 0}
    result = suggest_next_steps_node(dummy_state)
    assert isinstance(result, dict) or result is not None 