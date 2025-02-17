from langgraph.graph import StateGraph, END
from abbr_agent.nodes import AbbrNodes
from abbr_agent.state import DetectState, ProcessState

class AbbrAgent:
    def __init__(self):
        self.nodes = AbbrNodes()
        
    def build_workflow(self):
        workflow = StateGraph(ProcessState)
        
        workflow.add_node("detect_abbr", self.nodes.detect_abbr)
        workflow.add_node("process_abbr", self.nodes.process_abbr)
        
        def should_process(state: DetectState):
            if state["detected_abbr"] == ['None']:
                return END
            else:
                return "process_abbr"
        
        workflow.set_entry_point("detect_abbr")
        workflow.add_conditional_edges(
            "detect_abbr",
            should_process,
            {
                "process_abbr": "process_abbr",
                END: END
            }
        )
        workflow.add_edge("process_abbr", END)
        
        return workflow.compile()

    def chat(self):
        workflow = self.build_workflow()
        
        print("This is an AI assistant for abbreviation detection. If you want to end the conversation, please enter 'exit'.")
        while True:
            user_input = input("\ninput: ")
            if user_input == 'exit':
                break
            
            self.abbr_expansions = {}
            
            result = workflow.invoke({
                "input_text": user_input,
                "process_text": user_input,
                "detected_abbr": []
            })
            
            if "abbr_expansions" in result:
                self.abbr_expansions.update(result["abbr_expansions"])
            
            print(f"Detected abbreviations and their expansions:\n {self.abbr_expansions}")
            print(f"After expanding all the abbreviations, the full text will be:\n {result['process_text']}")