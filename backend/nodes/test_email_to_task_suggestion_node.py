import pytest
from backend.nodes.email_to_task_suggestion_node import email_to_task_suggestion_node

def test_email_to_task_suggestion_node_smoke():
    dummy_state = {"emails": []}
    result = email_to_task_suggestion_node(dummy_state)
    assert isinstance(result, dict) 