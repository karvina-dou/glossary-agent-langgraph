import os
import re
import json
import glob
from typing import List, Dict, Tuple
from pathlib import Path


# ---- Utils ----
def load_jsonl(file_path: Path, k: str = 'expansions') -> Dict[str, List]:
    abbr_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            record = json.loads(line.strip())
            abbr_dict[record['abbreviation']] = record[k]
    return abbr_dict


# ---- Preprocessing Functions ----
def sentence_split(case, **kwargs):
    return [{'input_text': f'{c}.'} for c in case.split('.')]


def search_abbr(paragraph: str, abbr: str) -> List[int]:
    """
    Searches for all instances of the given abbreviation in the paragraph and returns their positions.

    Args:
        paragraph: The text to search within.
        abbr: The abbreviation to search for.

    Returns:
        A list of integers representing the starting positions of all matches.
        Empty list if no match is found
    """
    # Use regex to find all instances of the abbreviation, \b is for word boundary
    matches = re.finditer(r'\b' + re.escape(abbr) + r'\b', paragraph)
    # Extract the starting positions of the matches
    positions = [match.start() for match in matches]
    return positions


def retrieve_sentence_and_context(paragraph: str, pos: int, n_context: int = 1) -> Tuple[str, str, Dict]:
    meta_data = {}
    S = E = pos
    FOUND_S = FOUND_E = False
    while not FOUND_S and S >= 0:
        if paragraph[S] == '.':
            FOUND_S = True
        S -= 1

    while not FOUND_E and E <= len(paragraph) - 1:
        if paragraph[E] == '.':
            FOUND_E = True
        E += 1

    S, E = max(S, 0), min(E, len(paragraph))  # clamp
    meta_data['SENTENCE'] = {'S': S + 2, 'E': E}
    SENTENCE = paragraph[S + 2:E]

    # move away from full-stops
    S -= 1
    E += 1
    FOUND_CS = FOUND_CE = n_context
    while FOUND_CS > 0 and S >= 0:
        if paragraph[S] == '.':
            FOUND_CS -= 1
        S -= 1

    while FOUND_CE > 0 and E <= len(paragraph) - 1:
        if paragraph[E] == '.':
            FOUND_CE -= 1
        E += 1

    S, E = max(S, 0), min(E, len(paragraph))  # clamp
    meta_data['CONTEXT'] = {'S': S + 2, 'E': E}
    CONTEXT = paragraph[S + 2:E]

    return SENTENCE.lstrip(), CONTEXT.lstrip(), meta_data


def regex(case, **kwargs):
    ret = []
    for ABBR, expansions in kwargs['glossary'].items():
        for position in search_abbr(case, ABBR):
            SENTENCE, CONTEXT, _ = retrieve_sentence_and_context(case, position, 4)
            ret += [{'SRC': ABBR, 'TGT': expansions[0]['expansion'], 'DESC': expansions[0]['description'], 'SEN': SENTENCE, 'CONTEXT': CONTEXT}]  # noqa:E501
    return ret


FUNC_MAP = {
    'sentence_split': sentence_split,
    'reg': regex,
}


# ---- Engine ----
class DataEngine:
    def __init__(self, data_path: str, max_concurrency: int = 5, preprocess_fn: str = 'sentence_split'):
        self.data_path = data_path
        self.max_concurrency = max_concurrency

        self.files = glob.glob(f'{data_path}/*.txt')
        self.glossary_path = os.path.join(data_path, 'glossary.jsonl')

        self.preprocess = FUNC_MAP[preprocess_fn]

    def __call__(self):
        for file_id, file in enumerate(self.files):
            inputs = self.preprocess(Path(file).read_text(), glossary=load_jsonl(self.glossary_path))
            yield file_id, file, Generator(inputs, self.max_concurrency)


class Generator:
    def __init__(self, inputs: List[Dict], max_concurrency: int = 5):
        self.inputs = inputs
        self.max_concurrency = max_concurrency

    def batching(self, inputs):
        return [inputs[i:i + self.max_concurrency]
                for i in range(0, len(inputs), self.max_concurrency) if len(inputs[i:i + self.max_concurrency]) > 1]

    def __call__(self):
        for batch_id, batch in enumerate(self.batching(self.inputs)):
            yield batch_id, batch
