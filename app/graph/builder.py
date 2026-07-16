# src/app/graph/builder.py
from langgraph.graph import StateGraph, END
from pathlib import Path
# Relative imports: go up to 'app', then down into 'state', 'graph', etc.
from ..state.agent_state import GitAgentState
from .nodes import observe_node, plan_node, execute_node, verify_node
from .router import route_after_planning

def create_git_graph():
    workflow = StateGraph(GitAgentState)
    
    workflow.add_node("observe", observe_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("verify", verify_node)
    
    workflow.set_entry_point("observe")
    workflow.add_edge("observe", "plan")
    
    workflow.add_conditional_edges(
        "plan",
        route_after_planning,
        {
            "execute": "execute",
            "end": END
        }
    )
    
    workflow.add_edge("execute", "verify")
    workflow.add_edge("verify", END)
    return workflow.compile()

if __name__ == "__main__":
    graph = create_git_graph()

    # # Generate Mermaid diagram text
    # mermaid = graph.get_graph().draw_mermaid()

    # print(mermaid)

    # # Save Mermaid file
    # Path("git_graph.mmd").write_text(mermaid)

    # # Generate PNG (requires pygraphviz)
    # png = graph.get_graph().draw_mermaid_png()

    # Path("git_graph.png").write_bytes(png)

    # print("Saved git_graph.png")