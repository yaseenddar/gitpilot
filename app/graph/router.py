from app.state.agent_state import GitAgentState

def route_after_planning(state: GitAgentState) -> str:
    plan = state["plan"]
    if plan and plan.action != "none":
        return "execute"
    return "end"