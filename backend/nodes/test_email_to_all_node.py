import pytest
from backend.nodes.email_to_all_node import email_to_all_node

def test_email_to_all_node_smoke():
    dummy_state = {"emails": []}
    result = email_to_all_node(dummy_state)
    assert isinstance(result, dict) 