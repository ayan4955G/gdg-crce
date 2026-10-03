import re
from typing import Dict, Any

class CodeFeatureExtractor:
    """
    Extracts surface and lexical code characteristics such as token lengths,
    cyclomatic indicators, and keyword densities.
    """

    def extract(self, code: str) -> Dict[str, Any]:
        if not code:
            return {
                "num_lines": 0,
                "character_count": 0,
                "has_loops": False,
                "has_conditionals": False,
                "has_functions": False,
                "has_equality_checks": False
            }

        lines = [l for l in code.splitlines() if l.strip()]
        return {
            "num_lines": len(lines),
            "character_count": len(code),
            "has_loops": bool(re.search(r"\b(for|while)\b", code)),
            "has_conditionals": bool(re.search(r"\b(if|elif|else)\b", code)),
            "has_functions": bool(re.search(r"\bdef\b", code)),
            "has_equality_checks": "==" in code or "!=" in code,
            "has_reassignment": bool(re.search(r"[a-zA-Z_]\w*\s*=\s*", code))
        }
