from agents.kv_agent import nodes, states
from langgraph.graph import StateGraph, END


def build_minigraph():
    sub_workflow = StateGraph(states.ProcessState)
    sub_workflow.add_node("lookup_abbr", nodes.lookup_abbr)
    sub_workflow.add_node("guess_abbr", nodes.guess_abbr)
    sub_workflow.add_node("validate_abbr", nodes.validate_abbr)
    sub_workflow.add_node("replace_abbr", nodes.replace_abbr)

    def exist_abbr(state: states.ProcessState):
        if len(state["expansions"]) >= 1:
            return "validate_abbr"
        else:
            return "guess_abbr"

    sub_workflow.set_entry_point("lookup_abbr")
    sub_workflow.add_conditional_edges(
        "lookup_abbr",
        exist_abbr,
        {
            "validate_abbr": "validate_abbr",
            "guess_abbr": "guess_abbr"
        }
    )

    sub_workflow.add_edge("validate_abbr", "replace_abbr")
    sub_workflow.add_edge("guess_abbr", "replace_abbr")
    sub_workflow.add_edge("replace_abbr", END)

    return sub_workflow.compile()


def build_workflow():
    def route_loop(state: states.ProcessState):
        if len(state['detected_abbr']) != 0:
            return "infer_node"
        return END

    def should_process(state: states.DetectState):
        if state["detected_abbr"] == ['None']:
            return END
        else:
            return "infer_node"

    # Define Graph
    workflow = StateGraph(states.ProcessState)

    # Add all nodes here
    workflow.add_node("detect_abbr", nodes.detect_abbr)
    workflow.add_node("infer_node", build_minigraph())

    # Define edges
    workflow.set_entry_point("detect_abbr")
    workflow.add_conditional_edges(
        "detect_abbr",
        should_process,
        {
            "infer_node": "infer_node",
            END: END
        }
    )
    workflow.add_conditional_edges("infer_node", route_loop, {"infer_node": "infer_node", END: END})
    return workflow.compile()
