from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from backend.models.task_model import TaskCreate, TaskOut
from backend.models.task_model import TaskUpdate
from backend.models.crud import get_tasks, create_task, delete_task, mark_done, delete_all_tasks
from backend.models.crud import update_task
from backend.models.agent_model import AgentRequest
from backend.agent import generate_agent_response, get_task_suggestions, decompose_task
from fastapi import APIRouter
from backend.gmail_reader import get_recent_emails
from backend.integrations.calendar import list_events, create_event, update_event, delete_event
from backend.agentic_graph import run_agentic_flow
from fastapi_utils.tasks import repeat_every
import logging
from backend.agents.task_agent import TaskAgent
import pandas as pd
from datetime import datetime, timedelta
from backend.models.crud import add_feedback, get_feedback_for_task
from pydantic import BaseModel

load_dotenv()
app = FastAPI()

# ✅ Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open to all origins for dev (change in prod)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Task Management Routes
@app.get("/tasks", response_model=list[TaskOut])
def get_all_tasks():
    return get_tasks()

@app.post("/tasks", response_model=TaskOut)
def add_task(task: TaskCreate):
    return create_task(task)

@app.delete("/tasks/{task_id}")
def remove_task(task_id: int):
    if not delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Deleted"}

@app.put("/tasks/{task_id}/done")
def mark_task_done_route(task_id: int):
    if not mark_done(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Marked as done"}

@app.patch("/tasks/{task_id}", response_model=TaskOut)
def patch_task(task_id: int, update: TaskUpdate):
    task = update_task(task_id, update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/clear")
def clear_all_tasks():
    delete_all_tasks()
    return {"message": "All tasks cleared."}

@app.post("/tasks/semantic-search")
def semantic_search_tasks(query: dict = Body(...)):
    q = query.get("query", "")
    task_agent = TaskAgent()
    results = task_agent.search_tasks(q)
    return {"results": results}

# ✅ Agentic Features Routes
@app.post("/agent-response")
def agent_response(input: AgentRequest):
    return {"response": generate_agent_response(input.tasks, input.message)}

@app.post("/suggest-tasks")
def suggest_tasks_route(input: dict = Body(...)):
    text = input.get("text", "")
    suggestions = get_task_suggestions(text)
    return {"suggestions": suggestions}

@app.post("/decompose-task")
def decompose_task_route(input: dict = Body(...)):
    task = input.get("task", "")
    return {"subtasks": decompose_task(task)}


@app.get("/emails")
def fetch_recent_emails():
    try:
        emails = get_recent_emails(5)  # You can change the number as needed
        return {"emails": emails}
    except Exception as e:
        return {"error": str(e)}

@app.get("/calendar/events")
def get_calendar_events():
    try:
        events = list_events(10)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calendar/events")
def add_calendar_event(event: dict = Body(...)):
    try:
        created = create_event(event)
        return {"event": created}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/calendar/events/{event_id}")
def update_calendar_event(event_id: str, event: dict = Body(...)):
    try:
        updated = update_event(event_id, event)
        return {"event": updated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/calendar/events/{event_id}")
def delete_calendar_event(event_id: str):
    try:
        delete_event(event_id)
        return {"message": "Deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agentic/email-to-task")
def agentic_email_to_task():
    emails = get_recent_emails(5)
    result = run_agentic_flow("email_to_task", state={"emails": emails})
    return {
        "processed": len(result.get("results", [])),
        "created_task_ids": result.get("created_task_ids", []),
        "results": result.get("results", []),
    }

@app.post("/agentic/email-to-calendar")
def agentic_email_to_calendar():
    result = run_agentic_flow("email_to_calendar", state={})
    return {"result": result}

@app.post("/agentic/task-to-calendar")
def agentic_task_to_calendar(input: dict = Body(...)):
    # expects input: {"task_title": ..., "start_dt": ..., "end_dt": ...}
    result = run_agentic_flow("task_to_calendar", state=input)
    return {"result": result}

@app.post("/agentic/calendar-to-task")
def agentic_calendar_to_task(input: dict = Body(...)):
    # expects input: {"event_id": ...}
    result = run_agentic_flow("calendar_to_task", state=input)
    return {"result": result}

@app.post("/agentic/task-to-task-and-calendar")
def agentic_task_to_task_and_calendar(input: dict = Body(...)):
    # expects input: {"task_title": ..., "start_dt": ..., "end_dt": ...}
    result = run_agentic_flow("task_to_task_and_calendar", state=input)
    return {"result": result}

@app.post("/agentic/email-to-all")
def agentic_email_to_all():
    from backend.gmail_reader import get_recent_emails
    emails = get_recent_emails(5)
    result = run_agentic_flow("email_to_all", state={"emails": emails})
    return result

@app.post("/agentic/task-to-all")
def agentic_task_to_all(input: dict = Body(...)):
    # expects input: {"task_title": ..., "start_dt": ..., "end_dt": ...}
    result = run_agentic_flow("task_to_all", state=input)
    return result

@app.post("/agentic/nonlinear-email-to-all")
def nonlinear_email_to_all():
    result = run_agentic_flow("nonlinear_email_to_all", state={})
    return result

@app.on_event("startup")
@repeat_every(seconds=60)  # every 60 seconds
async def background_agent_loop() -> None:
    try:
        print("[Agentic Loop] Polling Gmail and Calendar...")
        from backend.gmail_reader import get_recent_emails
        emails = get_recent_emails(5)
        result = run_agentic_flow("email_to_all", state={"emails": emails})
        # Deduplication: only create tasks if title does not exist
        from backend.models.crud import get_tasks, create_task
        from backend.models.task_model import TaskCreate
        existing_titles = set(t.title for t in get_tasks())
        for email_result in result.get('results', []):
            for suggestion in email_result.get('suggested_tasks', []):
                if suggestion not in existing_titles:
                    create_task(TaskCreate(title=suggestion))
                    print(f"[Agentic Loop] Created task: {suggestion}")
                else:
                    print(f"[Agentic Loop] Skipped duplicate task: {suggestion}")
        # Poll Google Calendar for new events (log for now)
        from backend.integrations.calendar import list_events
        events = list_events(10)
        print(f"[Agentic Loop] Calendar events: {[e.get('summary') for e in events]}")
    except Exception as e:
        logging.exception("[Agentic Loop] Error in background agent loop:")

@app.on_event("startup")
@repeat_every(seconds=600)  # every 10 minutes
async def eisenhower_prioritizer_loop() -> None:
    try:
        print("[Eisenhower Prioritizer] Scoring tasks...")
        from backend.models.crud import get_tasks, update_task
        from backend.models.task_model import TaskUpdate
        tasks = get_tasks()
        if not tasks:
            return
        df = pd.DataFrame([
            {
                "id": t.id,
                "title": t.title,
                "start": t.start,
                "is_done": t.is_done,
            } for t in tasks
        ])
        now = datetime.utcnow()
        # Urgency: tasks with a start date within 2 days are more urgent
        def compute_urgency(row):
            if row["start"]:
                try:
                    dt = datetime.fromisoformat(row["start"].replace("Z", "+00:00"))
                    days = (dt - now).days
                    if days <= 1:
                        return 1  # Most urgent
                    elif days <= 3:
                        return 2
                    elif days <= 7:
                        return 3
                except Exception:
                    pass
            return 4  # Not urgent
        # Importance: tasks with 'project', 'important', or subtasks in title are more important
        def compute_priority(row):
            title = row["title"].lower()
            if any(kw in title for kw in ["project", "important", "strategy", "plan"]):
                return 1  # Most important
            elif len(title.split()) > 5:
                return 2
            else:
                return 3
        df["urgency"] = df.apply(compute_urgency, axis=1)
        df["priority"] = df.apply(compute_priority, axis=1)
        # Update tasks in DB
        for _, row in df.iterrows():
            update_task(int(row["id"]), TaskUpdate(priority=int(row["priority"]), urgency=int(row["urgency"])))
        print("[Eisenhower Prioritizer] Updated priorities/urgencies.")
    except Exception as e:
        logging.exception("[Eisenhower Prioritizer] Error in prioritizer loop:")

class FeedbackIn(BaseModel):
    task_id: int
    rating: int | None = None
    comment: str | None = None

@app.post("/feedback")
def post_feedback(feedback: FeedbackIn):
    fb = add_feedback(feedback.task_id, feedback.rating, feedback.comment)
    return {"id": fb.id, "task_id": fb.task_id, "rating": fb.rating, "comment": fb.comment, "timestamp": fb.timestamp}

@app.get("/feedback/{task_id}")
def get_feedback(task_id: int):
    feedback = get_feedback_for_task(task_id)
    return [{"id": fb.id, "task_id": fb.task_id, "rating": fb.rating, "comment": fb.comment, "timestamp": fb.timestamp} for fb in feedback]

@app.post("/rag/context")
def rag_context(query: dict = Body(...)):
    q = query.get("query", "")
    task_agent = TaskAgent()
    docs = task_agent.retrieve_context(q)
    return {"results": [str(doc) for doc in docs]}