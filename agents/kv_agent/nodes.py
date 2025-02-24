import re
import copy
import json
from typing import Dict

from agents.kv_agent import states
from agents.kv_agent import prompts
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage


# utility functions
def build_model(model_args):
    return ChatOpenAI(**model_args)


def insert_(prompt: str, insert: Dict[str, str]):
    prompt = copy.deepcopy(prompt)
    for k, v in insert.items():
        if isinstance(k, str) and isinstance(v, str):
            prompt = prompt.replace("{" + k + "}", v)
    return prompt


def get_glossary(file_path):
    abbr_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            record = json.loads(line.strip())
            abbr_dict[record['abbreviation']] = record['expansions']
    return abbr_dict


# nodes
def detect_abbr(state: states.DetectState) -> states.ProcessState:
    model = build_model(state['external_args']["model_args"])
    prompt = insert_(prompts.detect_prompt, state)
    response = model.invoke([HumanMessage(content=prompt)])
    detected_abbr = [
        abbr.strip() for abbr in response.content.split(',')
        if abbr.strip()
    ]
    return {"detected_abbr": detected_abbr, "process_text": state['input_text']}


def lookup_abbr(state: states.ProcessState) -> states.ProcessState:
    state['current_abbr'] = state['detected_abbr'].pop(0)
    glossary = get_glossary(state['external_args']['glossary_path'])
    expansions = glossary.get(state["current_abbr"], [])
    return {"expansions": expansions, 'current_abbr': state['current_abbr']}


def guess_abbr(state: states.ProcessState) -> states.ProcessState:
    model = build_model(state['external_args']["model_args"])
    prompt = insert_(prompts.guess_prompt, state)
    response = model.invoke([HumanMessage(content=prompt)])
    return {"replacement": response.content.strip()}


def validate_abbr(state: states.ProcessState) -> states.ProcessState:
    model = build_model(state['external_args']["model_args"])
    state['options'] = "\n".join(
            [f"{i+1}. {exp}" for i, exp in enumerate(state["expansions"])])
    prompt = insert_(prompts.validate_prompt, state)
    response = model.invoke([HumanMessage(content=prompt)])
    return {"replacement": response.content.strip()}


def replace_abbr(state: states.ProcessState) -> states.ProcessState:
    text = state['process_text']
    abbr = state['current_abbr']
    replacement = state['replacement']

    pattern = re.compile(r'\b' + re.escape(abbr) + r'\b', re.IGNORECASE)
    new_text = pattern.sub(replacement, text)

    state.setdefault('processed_abbr', []).append({state["current_abbr"]: replacement})
    return {"process_text": new_text, 'processed_abbr': state['processed_abbr']}
