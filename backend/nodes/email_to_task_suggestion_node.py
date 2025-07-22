from backend.agents.ui_orchestration_agent import UIOrchestrationAgent
from backend.agents.email_agent import EmailAgent

orchestrator = UIOrchestrationAgent()
email_agent = EmailAgent()

def email_to_task_suggestion_node(state):
    emails = state.get("emails") or email_agent.get_recent_emails(5)
    results = []
    created_ids = []
    for email in emails:
        out = orchestrator.email_to_task_suggestions_for_email(email)
        results.append(out)
        for t in out.get("created_tasks", []):
            created_ids.append(t.get("id"))
    return {
        "emails": emails,
        "results": results,
        "created_task_ids": created_ids,
    } 