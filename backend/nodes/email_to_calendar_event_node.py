from backend.agents.ui_orchestration_agent import UIOrchestrationAgent
orchestrator = UIOrchestrationAgent()

def email_to_calendar_event_node(state):
    return orchestrator.email_to_calendar_event() 