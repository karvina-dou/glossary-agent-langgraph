from langgraph.graph import StateGraph, END
from abbr_agent.nodes import AbbrNodes
from abbr_agent.state import DetectState, LookupState, GuessState, ValidateState, ReplaceState, ProcessState

class AbbrAgent:
    def __init__(self):
        self.nodes = AbbrNodes()
        self.workflow = self.build_workflow()
        
    def build_workflow(self):
        workflow = StateGraph(ProcessState)
        
        # Add all nodes here
        workflow.add_node("detect_abbr", self.nodes.detect_abbr)
        workflow.add_node("lookup_abbr", self.nodes.lookup_abbr)
        workflow.add_node("guess_abbr", self.nodes.guess_abbr)
        workflow.add_node("validate_abbr", self.nodes.validate_abbr)
        workflow.add_node("replace_abbr", self.nodes.replace_abbr)
        
        def should_process(state: DetectState):
            if state["detected_abbr"] == ['None']:
                return END
            else:
                return "lookup_abbr"
        
        def exist_abbr(state: LookupState):
            if len(state["expansions"]) >= 1:
                return "validate_abbr"
            else:
                return "guess_abbr"
        
        workflow.set_entry_point("detect_abbr")
        workflow.add_conditional_edges(
            "detect_abbr",
            should_process,
            {
                "lookup_abbr": "lookup_abbr",
                END: END
            }
        )

        workflow.add_conditional_edges(
            "lookup_abbr",
            exist_abbr,
            {
                "validate_abbr": "validate_abbr",
                "guess_abbr": "guess_abbr"
            }
        )
        
        workflow.add_edge("validate_abbr", "replace_abbr")
        workflow.add_edge("guess_abbr", "replace_abbr")
        workflow.add_edge("replace_abbr", END)
        
        return workflow.compile()
    
agent = AbbrAgent()
graph = agent.workflow