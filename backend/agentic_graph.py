from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from typing import List, Optional, Any, TypedDict, Dict
from backend.agents.email_agent import EmailAgent
from backend.agents.task_agent import TaskAgent
from backend.agents.calendar_agent import CalendarAgent
from backend.agents.ui_orchestration_agent import UIOrchestrationAgent
from backend.models.crud import create_task, get_tasks
from backend.models.task_model import TaskCreate
from backend.nodes.email_to_task_suggestion_node import email_to_task_suggestion_node
from backend.nodes.email_to_calendar_event_node import email_to_calendar_event_node
from backend.nodes.task_to_calendar_event_node import task_to_calendar_event_node
from backend.nodes.calendar_event_to_task_node import calendar_event_to_task_node
from backend.nodes.task_to_task_and_calendar_node import task_to_task_and_calendar_node
from backend.nodes.email_to_all_node import email_to_all_node
from backend.nodes.task_to_all_node import task_to_all_node
from backend.nodes.fetch_emails_node import fetch_emails_node
from backend.nodes.parse_email_node import parse_email_node
from backend.nodes.suggest_tasks_node import suggest_tasks_node
from backend.nodes.create_tasks_node import create_tasks_node
from backend.nodes.create_calendar_events_node import create_calendar_events_node
from backend.nodes.suggest_next_steps_node import suggest_next_steps_node

# Node wrappers for LangGraph
email_agent = EmailAgent()
task_agent = TaskAgent()
calendar_agent = CalendarAgent()
orchestrator = UIOrchestrationAgent()

# --- State Schemas ---
class EmailToTaskState(TypedDict, total=False):
    emails: List[Dict[str, Any]]
    results: List[Dict[str, Any]]
    created_task_ids: List[int]

class EmailToCalendarState(BaseModel):
    # No input required, output is a list of email-calendar events
    pass

class TaskToCalendarState(BaseModel):
    event_id: str

class TaskToTaskAndCalendarState(BaseModel):
    task_title: str
    start_dt: Optional[str] = None
    end_dt: Optional[str] = None

class CalendarToTaskState(BaseModel):
    event_id: str

# --- New Unified Flows ---
class EmailToAllState(TypedDict, total=False):
    emails: List[Dict[str, Any]]
    results: List[Dict[str, Any]]

class TaskToAllState(TypedDict, total=False):
    task_title: str
    start_dt: str
    end_dt: str
    created_task: Dict[str, Any]
    created_event: Dict[str, Any]
    suggestions: List[str]

# --- Nonlinear Agentic Flow Nodes ---
def fetch_emails_node(state):
    emails = email_agent.get_recent_emails(5)
    return {**state, "emails": emails, "step": "parse_email", "email_idx": 0}

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

def suggest_tasks_node(state):
    idx = state.get("email_idx", 0)
    emails = state.get("emails", [])
    email = emails[idx]
    suggestions = task_agent.get_task_suggestions(f"From: {email['from']}\nSubject: {email['subject']}\nBody: {email['body']}")
    return {**state, "suggestions": suggestions, "step": "create_tasks"}

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

def suggest_next_steps_node(state):
    idx = state.get("email_idx", 0)
    emails = state.get("emails", [])
    # Optionally, suggest next actions or loop to next email
    if idx + 1 < len(emails):
        return {**state, "email_idx": idx + 1, "step": "parse_email"}
    else:
        return {**state, "step": END}

# --- Nonlinear Graph Construction ---
def build_agentic_graph(flow_type):
    if flow_type == 'nonlinear_email_to_all':
        graph = StateGraph(state_schema=EmailToAllState)
        graph.add_node('fetch_emails', fetch_emails_node)
        graph.add_node('parse_email', parse_email_node)
        graph.add_node('suggest_tasks', suggest_tasks_node)
        graph.add_node('create_tasks', create_tasks_node)
        graph.add_node('create_calendar_events', create_calendar_events_node)
        graph.add_node('suggest_next_steps', suggest_next_steps_node)
        graph.add_edge('fetch_emails', 'parse_email')
        graph.add_edge('parse_email', 'create_calendar_events')
        graph.add_edge('parse_email', 'create_tasks')
        graph.add_edge('parse_email', 'suggest_tasks')
        graph.add_edge('suggest_tasks', 'create_tasks')
        graph.add_edge('create_tasks', 'create_calendar_events')
        graph.add_edge('create_calendar_events', 'suggest_next_steps')
        graph.add_edge('suggest_next_steps', 'parse_email')  # loop
        graph.add_edge('suggest_next_steps', END)
        graph.set_entry_point('fetch_emails')
        return graph
    elif flow_type == 'email_to_task':
        graph = StateGraph(state_schema=EmailToTaskState)
        graph.add_node('email_to_task', email_to_task_suggestion_node)
        graph.add_edge('email_to_task', END)
        graph.set_entry_point('email_to_task')
    elif flow_type == 'email_to_calendar':
        graph = StateGraph(state_schema=EmailToCalendarState)
        graph.add_node('email_to_calendar', email_to_calendar_event_node)
        graph.add_edge('email_to_calendar', END)
        graph.set_entry_point('email_to_calendar')
    elif flow_type == 'task_to_calendar':
        graph = StateGraph(state_schema=TaskToCalendarState)
        graph.add_node('task_to_calendar', task_to_calendar_event_node)
        graph.add_edge('task_to_calendar', END)
        graph.set_entry_point('task_to_calendar')
    elif flow_type == 'calendar_to_task':
        graph = StateGraph(state_schema=CalendarToTaskState)
        graph.add_node('calendar_to_task', calendar_event_to_task_node)
        graph.add_edge('calendar_to_task', END)
        graph.set_entry_point('calendar_to_task')
    elif flow_type == 'task_to_task_and_calendar':
        graph = StateGraph(state_schema=TaskToTaskAndCalendarState)
        graph.add_node('task_to_task_and_calendar', task_to_task_and_calendar_node)
        graph.add_edge('task_to_task_and_calendar', END)
        graph.set_entry_point('task_to_task_and_calendar')
    elif flow_type == 'email_to_all':
        graph = StateGraph(state_schema=EmailToAllState)
        graph.add_node('email_to_all', email_to_all_node)
        graph.add_edge('email_to_all', END)
        graph.set_entry_point('email_to_all')
    elif flow_type == 'task_to_all':
        graph = StateGraph(state_schema=TaskToAllState)
        graph.add_node('task_to_all', task_to_all_node)
        graph.add_edge('task_to_all', END)
        graph.set_entry_point('task_to_all')
    else:
        raise ValueError('Unknown flow_type')
    return graph

def run_agentic_flow(flow_type, state):
    graph = build_agentic_graph(flow_type)
    compiled = graph.compile()
    return compiled.invoke(state) 