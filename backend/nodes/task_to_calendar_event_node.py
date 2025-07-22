from backend.agents.ui_orchestration_agent import UIOrchestrationAgent
orchestrator = UIOrchestrationAgent()

def task_to_calendar_event_node(state):
    try:
        if not getattr(state, "task_title", None) or not getattr(state, "start_dt", None) or not getattr(state, "end_dt", None):
            return {"error": "Missing required event data (task_title, start_dt, end_dt)."}
        result = orchestrator.task_to_calendar_event(state.task_title, state.start_dt, state.end_dt)
        if result is None:
            return {"error": "Failed to create calendar event."}
        return result
    except Exception as e:
        print(f"Error in task_to_calendar_event_node: {e}")
        return {"error": str(e)} 