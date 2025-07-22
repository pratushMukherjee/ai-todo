from backend.agents.task_agent import TaskAgent
task_agent = TaskAgent()

def suggest_tasks_node(state):
    idx = state.get("email_idx", 0)
    emails = state.get("emails", [])
    email = emails[idx]
    suggestions = task_agent.get_task_suggestions(f"From: {email['from']}\nSubject: {email['subject']}\nBody: {email['body']}")
    return {**state, "suggestions": suggestions, "step": "create_tasks"} 