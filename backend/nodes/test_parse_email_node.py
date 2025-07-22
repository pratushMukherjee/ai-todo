import pytest
from backend.nodes.parse_email_node import parse_email_node

def test_parse_email_node_smoke():
    dummy_state = {"emails": [{"from": "a@b.com", "subject": "Test", "body": "Hello"}], "email_idx": 0}
    result = parse_email_node(dummy_state)
    assert isinstance(result, dict) 