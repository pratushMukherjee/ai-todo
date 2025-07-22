from backend.agents.ui_orchestration_agent import UIOrchestrationAgent
orchestrator = UIOrchestrationAgent()

def task_to_task_and_calendar_node(state):
    return orchestrator.task_to_task_and_calendar(state.task_title, state.start_dt, state.end_dt) 