import pytest
from backend.nodes.fetch_emails_node import fetch_emails_node

def test_fetch_emails_node_smoke():
    dummy_state = {}
    result = fetch_emails_node(dummy_state)
    assert isinstance(result, dict) 