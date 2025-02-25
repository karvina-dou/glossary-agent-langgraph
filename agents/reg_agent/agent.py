from agents.reg_agent import nodes, states
from langgraph.graph import StateGraph, END


def build_workflow():
    workflow = StateGraph(states.ValidateState)
    workflow.add_node('validate_node', nodes.validate_node)

    workflow.set_entry_point("validate_node")
    workflow.add_edge("validate_node", END)

    return workflow.compile()