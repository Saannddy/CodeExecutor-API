import os, re

COMPILERS = {
    "c": {"compiler": "gcc", "extension": ".c"},
    "cpp": {"compiler": "g++", "extension": ".cpp"},
    "java": {"compiler": "javac", "extension": ".java"},
    "python": {"interpreter": "python", "extension": ".py"},
    "javascript": {"interpreter": "node", "extension": ".js"},
}

def validate_code(lang: str, code: str, rules: dict) -> bool:
    """Validate code against language-specific rules."""
    patterns = rules.get(lang, [])
    return all(not re.search(p, code) for p in patterns)
