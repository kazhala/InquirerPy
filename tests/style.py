from typing import Dict


def get_sample_style(val=None) -> Dict[str, str]:
    """For testing styles."""
    if not val:
        val = {}
    return {
        "questionmark": "#e5c07b",
        "answermark": "#e5c07b",
        "answer": "#61afef",
        "input": "#98c379",
        "question": "",
        "answered_question": "",
        "instruction": "",
        "pointer": "#61afef",
        "checkbox": "#98c379",
        "separator": "",
        "skipped": "#5c6370",
        "marker": "#e5c07b",
        "validator": "",
        "fuzzy_prompt": "#c678dd",
        "fuzzy_info": "#56b6c2",
        "frame.border": "#4b5263",
        "fuzzy_match": "#c678dd",
        "spinner_pattern": "#e5c07b",
        "spinner_text": "",
        **val,
    }
