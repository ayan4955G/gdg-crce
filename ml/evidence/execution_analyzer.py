import re
from typing import Dict, Any, List

class ExecutionAnalyzer:
    """
    Analyzes runtime execution results, stdout, stderr, and exception traces
    to detect symptom indicators of programming misconceptions.
    """

    def analyze(
        self,
        execution_result: Dict[str, Any],
        expected_output: str = ""
    ) -> Dict[str, Any]:
        stdout = (execution_result.get("stdout") or "").strip()
        stderr = (execution_result.get("stderr") or "").strip()
        exit_code = execution_result.get("exit_code", 0)
        timeout = execution_result.get("timeout", False)

        error_type = self._extract_error_type(stderr)
        detected_patterns = []

        # Check for IndexError (frequent in P003 off-by-one or P009 indexing)
        if error_type == "IndexError":
            detected_patterns.append({
                "symptom": "INDEX_ERROR",
                "misconception_candidate": "P003",
                "alternative_candidate": "P009",
                "confidence": 0.85,
                "detail": "Runtime IndexError: list index out of range on boundary."
            })

        # Check for NameError (frequent in P002 scope or P008 parameter mismatch)
        if error_type == "NameError":
            detected_patterns.append({
                "symptom": "NAME_ERROR",
                "misconception_candidate": "P002",
                "alternative_candidate": "P008",
                "confidence": 0.85,
                "detail": f"Runtime NameError: variable referenced outside its scope: {stderr.splitlines()[-1]}"
            })

        # Check for Timeout / Infinite loop (frequent in P004 loop condition logic)
        if timeout:
            detected_patterns.append({
                "symptom": "TIMEOUT_INFINITE_LOOP",
                "misconception_candidate": "P004",
                "confidence": 0.90,
                "detail": "Execution timed out. Loop continuation condition never evaluated to False."
            })

        # Check for implicit None in output (frequent in P007 return vs print)
        if "None" in stdout and expected_output and "None" not in expected_output:
            detected_patterns.append({
                "symptom": "UNEXPECTED_NONE_OUTPUT",
                "misconception_candidate": "P007",
                "confidence": 0.88,
                "detail": "Output contains 'None' when an evaluated value was expected (function likely missing return)."
            })

        # Check output mismatch
        output_matches = (stdout == expected_output.strip()) if expected_output else None

        return {
            "error_type": error_type,
            "stdout_clean": stdout,
            "output_matches_expected": output_matches,
            "has_runtime_error": error_type is not None,
            "detected_patterns": detected_patterns
        }

    def _extract_error_type(self, stderr: str) -> str:
        if not stderr:
            return None
        match = re.search(r"([A-Za-z]+Error):", stderr)
        if match:
            return match.group(1)
        if "TimeoutError" in stderr:
            return "TimeoutError"
        return None
