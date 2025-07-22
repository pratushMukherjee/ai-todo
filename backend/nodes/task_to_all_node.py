from backend.agents.task_agent import TaskAgent
from backend.models.crud import create_task
from backend.models.task_model import TaskCreate

task_agent = TaskAgent()

def task_to_all_node(state):
    details = task_agent.parse_task_details(state["task_title"])
    start = details['dates'][0] if details['dates'] else state.get("start_dt")
    assignees = details['people']
    t = create_task(TaskCreate(title=state["task_title"], start=start))
    task_agent.add_task_to_memory(t.id, state["task_title"])
    subtask_ids = []
    for sub in details['subtasks']:
        subtask = create_task(TaskCreate(title=sub))
        task_agent.add_task_to_memory(subtask.id, sub)
        subtask_ids.append(subtask.id)
    created_event = None
    if start and state.get("end_dt"):
        try:
            from backend.agents.calendar_agent import CalendarAgent
            calendar_agent = CalendarAgent()
            created_event = calendar_agent.create_event({
                "summary": t.title,
                "start": {"dateTime": start},
                "end": {"dateTime": state["end_dt"]}
            })
        except Exception:
            created_event = None
    suggestions = task_agent.get_task_suggestions(t.title)
    return {
        "created_task": {
            "id": t.id,
            "title": t.title,
            "start": start,
            "subtasks": details['subtasks'],
            "subtask_ids": subtask_ids,
            "assignees": assignees
        },
        "created_event": created_event,
        "suggestions": suggestions,
        "parsed_details": details
    } 