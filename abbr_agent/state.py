from typing import Dict, List, TypedDict

class DetectState(TypedDict):
    input_text: str

class LookupState(TypedDict):
    detected_abbr: List[str]
    current_abbr: str

class GuessState(TypedDict):
    input_text: str
    detected_abbr: List[str]
    current_abbr: str

class ValidateState(TypedDict):
    input_text: str
    detected_abbr: List[str]
    current_abbr: str
    expansions: List[Dict[str, str]]

class ReplaceState(TypedDict):
    input_text: str
    detected_abbr: List[str]
    current_abbr: str
    replacement: str

class ProcessState(TypedDict):
    input_text: str
    process_text: str
    detected_abbr: List[str]
    current_abbr: str
    expansions: List[Dict[str, str]]
    replacement: str
    abbr_expansions: Dict[str, str]