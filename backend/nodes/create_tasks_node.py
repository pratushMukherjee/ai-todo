from backend.agents.task_agent import TaskAgent
from backend.models.crud import create_task
from backend.models.task_model import TaskCreate
task_agent = TaskAgent()

def create_tasks_node(state):
    idx = state.get("email_idx", 0)
    emails = state.get("emails", [])
    email = emails[idx]
    suggestions = state.get("suggestions") or [email['subject']]
    created_tasks = []
    for s in suggestions:
        details = task_agent.parse_task_details(s)
        t = create_task(TaskCreate(title=s, start=details['dates'][0] if details['dates'] else None))
        # Add to memory
        task_agent.add_task_to_memory(t.id, s)
        # Create subtasks if found
        for sub in details['subtasks']:
            subtask = create_task(TaskCreate(title=sub))
            task_agent.add_task_to_memory(subtask.id, sub)
        created_tasks.append({"id": t.id, "title": t.title, "start": t.start, "subtasks": details['subtasks'], "assignees": details['people']})
    return {**state, "created_tasks": created_tasks, "step": "create_calendar_events"} 