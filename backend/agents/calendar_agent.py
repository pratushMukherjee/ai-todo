from backend.integrations import calendar

class CalendarAgent:
    def list_events(self, max_results=10):
        return calendar.list_events(max_results)

    def create_event(self, event):
        return calendar.create_event(event)

    def update_event(self, event_id, event):
        return calendar.update_event(event_id, event)

    def delete_event(self, event_id):
        return calendar.delete_event(event_id) 