from .inspector import INSPECTORS
from .detector import detect_violations

def sanitize_code(lang: str, code: str) -> dict:
    """Two-pass scan: 1. Whitelist (AST) 2. Blacklist (Regex)."""
    violations = []

    if lang in INSPECTORS:
        wl = INSPECTORS[lang](code)
        if not wl.get("safe", True):
            violations.append("Functionality or library not found in the allowed runtime environment.")

    bl = detect_violations(lang, code)
    if not bl.get("safe", True):
        violations.extend(bl.get("violations", []))
            
    return {
        "safe": len(violations) == 0,
        "violations": violations
    }
