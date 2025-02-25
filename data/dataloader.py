import glob
from typing import List
from pathlib import Path


def get_dataloader(dname: str):
    if dname == 'kv':
        return Path('./data/kv_data/passage.txt').read_text().split('\n'), './data/kv_data/glossary.jsonl'
    elif dname == 'wiki':
        def file_gen(list_of_file: List[str]):
            for file in list_of_file:
                yield Path(file).read_text()
        return file_gen(sorted(glob.glob('./wiki_data/*.txt'))), './data/wiki_data/glossary.jsonl'
