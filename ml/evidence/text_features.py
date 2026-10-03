import re
from typing import Dict, Any, List

class TextFeatureExtractor:
    """
    Extracts lexical indicators, linguistic markers of cognitive uncertainty,
    and misconception-specific semantic cues from student explanations.
    """

    LEXICAL_MARKERS = {
        "P001": ["permanently", "tied to", "algebraic", "equal to both", "swaps simultaneously", "swapped"],
        "P002": ["globally", "inside function", "scope", "outer variable", "accessible anywhere", "stack frame"],
        "P003": ["includes 5", "inclusive", "stop at 5", "up to and including", "runs 5 times", "last index"],
        "P004": ["stops immediately", "aborts", "condition became 0", "exit condition", "checks in the middle"],
        "P005": ["only one if", "first matching if", "second if overwrites", "independent if", "elif ladder"],
        "P006": ["or 2", "or 'b'", "both conditions", "either is true", "truthy", "and requires"],
        "P007": ["printed to screen", "returns 7 into", "prints instead", "void", "implicit none", "terminal"],
        "P008": ["must match", "parameter name", "argument name", "forgot to pass", "global x instead"],
        "P009": ["first element", "index 1 is first", "slices include 3", "zero index", "ordinal"],
        "P010": ["copy of", "independent copy", "modifying b modifies a", "reference", "alias", "pointer"]
    }

    HEDGING_TERMS = ["maybe", "guess", "idk", "not sure", "probably", "might be", "broke"]

    def extract(self, text: str) -> Dict[str, Any]:
        if not text:
            return {
                "word_count": 0,
                "is_hedging": True,
                "detected_cues": {},
                "insufficient_evidence": True
            }

        cleaned = text.lower()
        words = re.findall(r"\w+", cleaned)
        word_count = len(words)

        # Hedging / Insufficient evidence detection
        hedging_hits = [h for h in self.HEDGING_TERMS if h in cleaned]
        is_hedging = len(hedging_hits) > 0 and word_count < 12

        # Cue detection
        detected_cues = {}
        for misc_id, markers in self.LEXICAL_MARKERS.items():
            matches = [m for m in markers if m in cleaned]
            if matches:
                detected_cues[misc_id] = matches

        return {
            "word_count": word_count,
            "is_hedging": is_hedging,
            "hedging_terms": hedging_hits,
            "detected_cues": detected_cues,
            "insufficient_evidence": word_count < 4 or (is_hedging and not detected_cues)
        }
