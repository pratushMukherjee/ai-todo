from langgraph.graph import END

def suggest_next_steps_node(state):
    idx = state.get("email_idx", 0)
    emails = state.get("emails", [])
    # Optionally, suggest next actions or loop to next email
    if idx + 1 < len(emails):
        return {**state, "email_idx": idx + 1, "step": "parse_email"}
    else:
        return {**state, "step": END} 