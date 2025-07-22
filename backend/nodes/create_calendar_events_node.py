from backend.agents.calendar_agent import CalendarAgent
calendar_agent = CalendarAgent()

def create_calendar_events_node(state):
    idx = state.get("email_idx", 0)
    emails = state.get("emails", [])
    email = emails[idx]
    parsed = state.get("parsed", {})
    created_events = []
    # Use parsed dates for event
    if parsed.get('dates'):
        start = parsed['dates'][0]
        try:
            event = calendar_agent.create_event({
                "summary": email['subject'],
                "start": {"dateTime": start},
                "end": {"dateTime": start}  # For demo, use same as start
            })
            created_events.append(event)
        except Exception:
            pass
    return {**state, "created_events": created_events, "step": "suggest_next_steps"} 