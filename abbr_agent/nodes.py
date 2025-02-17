import re
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from .utils import load_grocery, replace_abbr_in_text
from .state import DetectState, LookupState, GuessState, ValidateState, ReplaceState, ProcessState

grocery = load_grocery()

class AbbrNodes:
    def __init__(self):
        self.model = ChatOpenAI(
            model="qwen/qwen2.5-3B-instruct",
            api_key="12345678",
            openai_api_base = "http://localhost:8000/v1",
            max_tokens=2048,
            temperature=1,
        )
        
    def detect_abbr(self, state: DetectState) -> Dict[str, Any]:

        prompt = f"""
        You are a professional abbreviation detection assistant. Your task is to correctly detect all possible abbreviations in the input text.
        Following the steps:
        1. Detect all possible abbreviations (there are very likeyly more than one) in the text, please don't miss any one. **Ensure no abbreviation is missed.**
        2. Respond only with the detected abbreviations, separated by commas, with no additional words. **Only list abbreviations, nothing else.**
        3. If there are no abbreviations in the sentence, respond with 'None'. **Respond with 'None' if no abbreviations are found.**
        4. If you see a single letter and it is commonly used as a pronoun or common word (e.g., 'I', 'a', 'u'), do not detect it as an abbr. **Do not consider common single letters as abbreviations.**
        5. All abbreviations will appear in uppercase letters only. **Only detect uppercase abbreviations.**
        Example:
        - Input: "The CPU and RAM are essential components."
        - Output: "CPU, RAM"
        - Input: "The CEO of the company gave a speech."
        - Output: "CEO"
        - Input: "I went to the store."
        - Output: "None"
        
        Follow the above instructions, only respond with the detected abbreviation (separated by commas) from the given text: {state['input_text']}
        """
        
        # print(prompt)
    
        response = self.model.invoke([HumanMessage(content=prompt)])
        # print("detecting the abbreviation......")
        # print(response)
        # print("")
        detected_abbr = [abbr.strip()
                    for abbr in response.content.split(',') 
                    if abbr.strip()]
        
        return {"detected_abbr": detected_abbr}

    def lookup_abbr(self, state: LookupState) -> Dict[str, Any]:
        expansions = grocery.get(state["current_abbr"], [])
        # print("looking up the grocery......")
        # print("")
        return {"expansions": expansions}

    def guess_abbr(self, state: GuessState) -> Dict[str, Any]:
        
        prompt = f"""
        You are a professional abbreviation guessing assistant. Your task is to guess the full form of a given abbreviation based on the provided context.
        Steps:
        1. Given an abbreviation and its context, guess the most likely full form.
        2. Respond only with the full form of the abbreviation, with no additional explanation or words.
        Example:
        - Input: "What is the expansion of the abbreviation 'AI' in the following context: 'AI is transforming industries.'"
        - Output: "Artificial Intelligence"
        
        Follow the above instructions, what is the expansion of the abbreviation '{state['current_abbr']}' in the given context: {state['input_text']}
        Please respond only with the full form of the abbreviation, no additional explanation or word.
        """
        # print(prompt)
        
        response = self.model.invoke([HumanMessage(content=prompt)])
        # print("guessing the meaning of abbreviation......")
        # print(response)
        # print("")
        
        return {"replacement": response.content.strip()}

    def validate_abbr(self, state: ValidateState) -> Dict[str, Any]:
        options = "\n".join([f"{i+1}. {exp}" for i, exp in enumerate(state["expansions"])])
        
        prompt = f"""
        You are a professional abbreviation explanation assistant. Your task is to choose the most contextually appropriate full form of an abbreviation from a list of options.
        Please follow the steps:
        1. Given an abbreviation, its context, and a list of possible full expansions, choose the most suitable one.
        2. If there is only one possible expansion, determine if it is suitable for the given context. If it is not suitable, suggest a more appropriate expansion.
        3. If there are multiple possible expansions, choose the most suitable one. If none of them are suitable, suggest a more appropriate expansion.
        4. Respond only with the exact expansion provided or you suggest, no other words or futher description needed.
        Example:
        - Input: "The UX of this app is great.' Options: 1. User Experience 2. User Exchange"
        - Output: "User Experience"
        - Input: "There are many digital arts in the AI exhibition.' Options: 1. Artificial Intelligence"
        - Output: "Art Interface"
        
        Consider the content of the whole text, which expansion is more suitable for the abbreviation '{state['current_abbr']}'? 
        Text: {state['input_text']}
        Options: {options}
        Follow the above instructions, please respond only with the exact expansion.
        """
        
        # print(prompt)
        
        response = self.model.invoke([HumanMessage(content=prompt)])
        # print("choosing the meaning of abbreviation......")
        # print(response)
        # print("")
        
        return {"replacement": response.content.strip()}

    def replace_abbr(self, state: ReplaceState) -> Dict[str, Any]:
        text = state['input_text']
        abbr = state['current_abbr']
        replacement = state['replacement']
        
        new_text = replace_abbr_in_text(text, abbr, replacement)
        
        return {"process_text": new_text}

    def process_abbr(self, state: ProcessState):
        workflow = StateGraph(ProcessState)
        
        workflow.add_node("lookup_abbr", self.lookup_abbr)
        workflow.add_node("guess_abbr", self.guess_abbr)
        workflow.add_node("validate_abbr", self.validate_abbr)
        workflow.add_node("replace_abbr", self.replace_abbr)
        
        workflow.set_entry_point("lookup_abbr")
        
        def exist_expansions(state: LookupState):
            if len(state["expansions"]) >= 1:
                return "validate_abbr"
            else:
                return "guess_abbr"
            
        workflow.add_conditional_edges(
            "lookup_abbr",
            exist_expansions,
            {
                "validate_abbr": "validate_abbr",
                "guess_abbr": "guess_abbr"
            }
        )
        
        workflow.add_edge("validate_abbr", "replace_abbr")
        workflow.add_edge("guess_abbr", "replace_abbr")
        workflow.add_edge("replace_abbr", END)
        
        app = workflow.compile()
        
        process_text = state["input_text"]
        detected_abbr = state["detected_abbr"]
        abbr_expansions = {}
        print(detected_abbr)
        for abbr in detected_abbr:
            
            result = app.invoke({
                "input_text": process_text,
                "current_abbr": abbr,
                "expansions": [],
                "replacement": ""
            })
            # print(result)
            process_text = result["process_text"]
            abbr_expansions[abbr] = result["replacement"]
            
        state["process_text"] = process_text
        state["abbr_expansions"] = abbr_expansions
        
        return {"process_text": process_text, "abbr_expansions": abbr_expansions}
