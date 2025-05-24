import json
import re

def loads(s: str):
    """Very small subset of JSON5 parsing used in tests."""
    # Strip line comments
    s = re.sub(r"(?m)^\s*//.*$", "", s)
    # Remove trailing commas before closing braces/brackets
    s = re.sub(r",\s*(?=[\]}])", "", s)
    return json.loads(s)

