from langgraph.graph import END
from backend.agents.task_agent import TaskAgent

task_agent = TaskAgent()

def parse_email_node(state):
    idx = state.get("email_idx", 0)
    emails = state.get("emails", [])
    if idx >= len(emails):
        return {**state, "step": END}
    email = emails[idx]
    parsed = task_agent.parse_task_details(f"From: {email['from']}\nSubject: {email['subject']}\nBody: {email['body']}")
    # Decide next step based on parsed content
    if parsed['dates']:
        return {**state, "parsed": parsed, "step": "create_calendar_events"}
    elif parsed['subtasks'] or parsed['people']:
        return {**state, "parsed": parsed, "step": "create_tasks"}
    else:
        return {**state, "parsed": parsed, "step": "suggest_tasks"} 