# flake8: noqa:E501
import copy
from typing import Dict


# -------------------------------------VALIDATION MAIN PROMPTS-------------------------------------
VALIDATION_TEMPLATE = """
You are an editor in chief. Your task is to proof-read articles before publication. A junior editor had just converted an abbreviation/acronym into it's full form e.g. CEO -> Chief Executive Officer, and your task is to verify whether the conversion is correct based on its context. Please follow these instructions for your task:
1. I/O Format:
    1.1 Input format: "Convertion: {SOURCE} -> {TARGET}, DESCRIPTION: {DESCRIPTION}, SENTENCE: {SENTENCE}, CONTEXT: {CONTEXT}", where {SOURCE} is the abbreviation/acronym, {TARGET} is the full form, {DESCRIPTION} is a short description of the word's meaning, {SENTENCE} is the full sentence that the change happens, and {CONTEXT} is a larger chunk of text surrounding the sentence.
    1.2 Output format: "{BOOL}", where {BOOL} is a single boolean output a.k.a True or False, for approving the convertion or not. Please strictly follow this output format with no additional explaination etc.
2. Task:
    2.1 Determine whether the abbreviation/acronym is valid under the given context
    2.2 The abbreviation should be highly related to the topics of the passage, which can be learnt from the context. For instance, if the context is relate to psychotherapy, the acronym "NLP" should meant "Neuro-linguistic programming" instead of the computer processing term "Natural language processing".
3. Examples:
    {EXAMPLES}
DO NOT RETURN EXPLAINATIONS!
"""

VALIDATION_TEMPLATE_v2 = """
You are an editor in chief. Your task is to proof-read articles before publication. A junior editor had just converted an abbreviation/acronym into it's full form e.g. CEO -> Chief Executive Officer, and your task is to verify whether the conversion is possible/plausible based on its context. Meaning that the sentence still make sense with the given conversion. Please follow these instructions for your task:
1. I/O Format:
    1.1 Input format: "Convertion: {SOURCE} -> {TARGET}, DESCRIPTION: {DESCRIPTION}, SENTENCE: {SENTENCE}, CONTEXT: {CONTEXT}", where {SOURCE} is the abbreviation/acronym, {TARGET} is the full form, {DESCRIPTION} is a short description of the word's meaning, {SENTENCE} is the full sentence that the change happens, and {CONTEXT} is a larger chunk of text surrounding the sentence.
    1.2 Output format: "{BOOL}", where {BOOL} is a single boolean output a.k.a True or False, for approving the convertion or not. Please strictly follow this output format with no additional explaination etc.
2. Task:
    2.1 Determine whether the abbreviation/acronym is valid under the given context
    2.2 The abbreviation should be highly related to the topics of the passage, which can be learnt from the context. For instance, if the context is relate to psychotherapy, the acronym "NLP" should meant "Neuro-linguistic programming" instead of the computer processing term "Natural language processing".
3. Examples:
    {EXAMPLES}
DO NOT RETURN EXPLAINATIONS!
"""

VALIDATION_TEMPLATE_KV = """
You are a professional abbreviation explaination assistant. Your task is to choose the most contextually appropriate full form of an abbreviation from a list of options.
Please follow the steps:
1. Given an abbreviation, its context, and a list of possible full expansions, choose the most suitable one.
2. If there is only one possible expansion, determine if it is suitable for the given context. If it is not suitable, suggest a more appropriate expansion.
3. If there are multiple possible expansions, choose the most suitable one. If none of them are suitable, suggest a more appropriate expansion.
4. Respond only with the exact expansion provided or you suggest, no other words or futher description needed.
Example:
- Input: "The UX of this app is great.' Options: 1. User Experience 2. User Exchange"
- Output: "User Experience"
"""

VINPUT_TEMPLATE = "Convertion: {SOURCE} -> {TARGET}, DESCRIPTION: {DESCRIPTION}, SENTENCE: {SENTENCE}, CONTEXT: {CONTEXT}"

VINPUT_TEMPLATE_KV = """
Consider the content of the whole text, which expansion is more suitable for the abbreviation '{SRC}'? 
Text: {SENTENCE}
Expansion: {TGT}
Follow the above instructions, please respond only with the exact expansion.
"""

# ---------------------------------------VALIDATION EXAMPLES---------------------------------------
VE0_SRC = '''DA'''
VE0_TGT = '''data analysis'''
VE0_SEN = '''combining established concepts and principles of statistics and with computing.'''
VE0_DESC = '''The process of inspecting, cleansing, transforming, and modeling data to discover useful information, inform conclusions, and support decision-making.'''
VE0_CONTEXT = '''
In 1962, John Tukey described a field he called "data analysis", which resembles modern data science. In 1985, in a lecture given to the Chinese Academy of Sciences in Beijing, C. F. Jeff Wu used the term "data science" for the first time as an alternative name for statistics.Later, attendees at a 1992 statistics symposium at the University of Montpellier  II acknowledged the emergence of a new discipline focused on data of various origins and forms, combining established concepts and principles of statistics and DA with computing.
'''
VE0 = f'''
INPUT: {copy.deepcopy(VINPUT_TEMPLATE).replace("{SOURCE}", VE0_SRC).replace("{TARGET}", VE0_TGT).replace("{DESCRIPTION}", VE0_DESC).replace("{SENTENCE}", VE0_SEN).replace("{CONTEXT}", VE0_CONTEXT)}
OUTPUT: True
EXPLAINATION: The whole passage is related to the etymology of the word data science which is highly related to data analysis.
'''

VE1_SRC = '''NLP'''
VE1_TGT = '''Natural language processing'''
VE1_DESC = '''A field of artificial intelligence that focuses on the interaction between computers and humans through natural language, enabling machines to understand, interpret, and generate human language.'''
VE1_SEN = '''Scientific reviews have shown that NLP is based on outdated metaphors of the brain's inner workings that are inconsistent with current neurological theory'''
VE1_CONTEXT = '''
There is no scientific evidence supporting the claims made by NLP advocates, and it has been called a pseudoscience. Scientific reviews have shown that NLP is based on outdated metaphors of the brain's inner workings that are inconsistent with current neurological theory, and that NLP contains numerous factual errors.Reviews also found that research that favored NLP contained significant methodological flaws, and that there were three times as many studies of a much higher quality that failed to reproduce the claims made by Bandler, Grinder, and other NLP practitioners.
'''
VE1 = f'''
INPUT: {copy.deepcopy(VINPUT_TEMPLATE).replace("{SOURCE}", VE1_SRC).replace("{TARGET}", VE1_TGT).replace("{DESCRIPTION}", VE1_DESC).replace("{SENTENCE}", VE1_SEN).replace("{CONTEXT}", VE1_CONTEXT)}
OUTPUT: False
EXPLAINATION: The whole passage is related to debunking a psychotherapy method is actually pesudoscience, which has nothing related to natural language processing.
'''


def craft_prompt(state: Dict[str, str]) -> str:
    EXAMPLES = f'''Example 1:\n{VE0}\nExample 2:\n{VE1}'''
    SYSTEM_PROMPT = copy.deepcopy(VALIDATION_TEMPLATE_v2).replace("{EXAMPLES}", EXAMPLES)
    USER_PROMPT = 'Verify this conversion: ' + copy.deepcopy(VINPUT_TEMPLATE).replace("{SOURCE}", state["SRC"])\
        .replace("{TARGET}", state["TGT"]).replace("{SENTENCE}", state["SEN"]).replace("{CONTEXT}", state["CONTEXT"])\
        .replace('{DESCRIPTION}', state["DESC"])
    return SYSTEM_PROMPT, USER_PROMPT

