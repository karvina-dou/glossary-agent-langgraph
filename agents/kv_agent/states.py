from typing import Dict, List, TypedDict


class DetectState(TypedDict):
    input_text: str
    external_args: Dict


class LookupState(TypedDict):
    detected_abbr: List[str]
    current_abbr: str
    external_args: Dict
    processed_abbr: List[Dict]


class ProcessState(TypedDict):
    external_args: Dict
    input_text: str
    process_text: str
    detected_abbr: List[str]
    current_abbr: str
    processed_abbr: List[Dict]
    expansions: List[Dict[str, str]]
    replacement: str
    abbr_expansions: Dict[str, str]
