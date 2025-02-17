import re
import json
from typing import Dict
from pathlib import Path

def load_grocery(file_path=None):
    if not file_path:
        base_dir = Path(__file__).resolve().parent.parent
        file_path = base_dir / "data" / "grocery.jsonl"
        
    abbr_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            record = json.loads(line.strip())
            abbr_dict[record['abbreviation']] = record['expansions']
    return abbr_dict

def replace_abbr_in_text(text: str, abbr: str, replacement: str) -> str:
    pattern = re.compile(r'\b' + re.escape(abbr) + r'\b', re.IGNORECASE)
    return pattern.sub(replacement, text)