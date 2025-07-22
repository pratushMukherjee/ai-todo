from backend.agents.task_agent import TaskAgent
from backend.agents.email_agent import EmailAgent
from backend.models.crud import get_tasks, create_task
from backend.models.task_model import TaskCreate

task_agent = TaskAgent()
email_agent = EmailAgent()

def email_to_all_node(state):
    emails = state.get("emails") or email_agent.get_recent_emails(5)
    existing_titles = set(t.title.strip().lower() for t in get_tasks())
    results = []
    for email in emails:
        email_text = f"From: {email['from']}\nSubject: {email['subject']}\nBody: {email['body']}"
        analysis = task_agent.get_email_analysis(email_text)
        suggestions = task_agent.get_task_suggestions(email_text)
        created_tasks = []
        for s in suggestions:
            title_clean = s.strip().lower()
            if title_clean in existing_titles:
                continue
            details = task_agent.parse_task_details(s)
            start = details['dates'][0] if details['dates'] else None
            assignees = details['people']
            t = create_task(TaskCreate(title=s, start=start))
            created_tasks.append({
                "id": t.id,
                "title": t.title,
                "start": start,
                "subtasks": details['subtasks'],
                "assignees": assignees
            })
            existing_titles.add(title_clean)
        results.append({
            "email": email,
            "suggested_tasks": suggestions,
            "created_tasks": created_tasks,
            "ai_analyses": [analysis]
        })
    return {"emails": emails, "results": results} 