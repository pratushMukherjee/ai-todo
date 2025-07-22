from backend.agents.email_agent import EmailAgent
from backend.agents.task_agent import TaskAgent
from backend.agents.calendar_agent import CalendarAgent
from backend.models.crud import create_task
from backend.models.task_model import TaskCreate

class UIOrchestrationAgent:
    def __init__(self):
        self.email_agent = EmailAgent()
        self.task_agent = TaskAgent()
        self.calendar_agent = CalendarAgent()

    def email_to_task_suggestions(self, max_emails=5):
        emails = self.email_agent.get_recent_emails(max_emails)
        results = []
        for email in emails:
            text = f"From: {email['from']}\nSubject: {email['subject']}\nBody: {email['body']}"
            sugg = self.task_agent.get_task_suggestions(text)
            # Do NOT create tasks here!
            results.append({"email": email, "suggested_tasks": sugg, "created_events": []})
        return results

    def email_to_task_suggestions_for_email(self, email):
        text = f"From: {email['from']}\nSubject: {email['subject']}\nBody: {email['body']}"
        sugg = self.task_agent.get_task_suggestions(text)
        # Do NOT create tasks here!
        return {"email": email, "suggested_tasks": sugg, "created_events": []}

    def email_to_calendar_event(self, max_emails=5):
        emails = self.email_agent.get_recent_emails(max_emails)
        created_events = []
        for email in emails:
            event = {
                "summary": email['subject'],
                "description": email['body'],
                # You may want to parse a date from the email body for real use
                "start": {"dateTime": "2024-01-01T09:00:00-07:00"},
                "end": {"dateTime": "2024-01-01T10:00:00-07:00"}
            }
            created = self.calendar_agent.create_event(event)
            created_events.append({"email": email, "event": created})
        return created_events

    def task_to_calendar_event(self, task_title, start_dt, end_dt):
        event = {
            "summary": task_title,
            "start": {"dateTime": start_dt},
            "end": {"dateTime": end_dt}
        }
        return self.calendar_agent.create_event(event)

    def calendar_event_to_task(self, event_id):
        events = self.calendar_agent.list_events()
        event = next((e for e in events if e['id'] == event_id), None)
        if not event:
            return None
        task_title = event.get('summary', 'Untitled Event')
        # Here you would call your task creation logic
        return {"task_title": task_title, "event": event}

    def task_to_task_and_calendar(self, task_title, start_dt=None, end_dt=None):
        # Create the task in the DB
        task_obj = create_task(TaskCreate(title=task_title))
        # Create the calendar event (if times provided)
        event = None
        if start_dt and end_dt:
            event = self.calendar_agent.create_event({
                "summary": task_title,
                "start": {"dateTime": start_dt},
                "end": {"dateTime": end_dt}
            })
        return {"task": {"id": task_obj.id, "title": task_obj.title, "is_done": getattr(task_obj, 'is_done', False)}, "event": event} 