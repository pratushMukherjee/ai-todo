from backend.agents.ui_orchestration_agent import UIOrchestrationAgent
orchestrator = UIOrchestrationAgent()

def calendar_event_to_task_node(state):
    try:
        if not getattr(state, "event_id", None):
            return {"error": "Missing event_id."}
        result = orchestrator.calendar_event_to_task(state.event_id)
        if result is None:
            return {"error": "No event found or created."}
        return result
    except Exception as e:
        print(f"Error in calendar_event_to_task_node: {e}")
        return {"error": str(e)} 