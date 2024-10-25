import re

ABBREVIATIONS = {
    "FE": "Fakultas Ekonomi",
    "FTK": "Fakultas Teknik dan Kejuruan"
}

def expand_abbreviations(question: str, abbreviations: dict) -> str:
    def replace_abbreviation(match):
        return abbreviations.get(match.group(0).upper(), match.group(0))
    pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in abbreviations.keys()) + r')\b', re.IGNORECASE)
    expanded_question = pattern.sub(replace_abbreviation, question)
    return expanded_question