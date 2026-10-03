from typing import Dict, Any, List, Optional
from ml.evidence.ast_analyzer import CodeASTAnalyzer
from ml.evidence.execution_analyzer import ExecutionAnalyzer
from ml.evidence.text_features import TextFeatureExtractor
from ml.evidence.code_features import CodeFeatureExtractor
from sandbox.code_runner import SandboxedCodeRunner

class EvidenceFusionEngine:
    """
    Orchestrates the multi-source evidence pipeline:
    Parses AST, executes safely in sandbox, extracts student verbalization signals,
    and fuses them into an auditable evidence package for diagnosis.
    """

    def __init__(self):
        self.ast_analyzer = CodeASTAnalyzer()
        self.exec_analyzer = ExecutionAnalyzer()
        self.text_extractor = TextFeatureExtractor()
        self.code_extractor = CodeFeatureExtractor()
        self.sandbox = SandboxedCodeRunner(timeout_seconds=2.0)

    def extract_and_fuse(
        self,
        code: str,
        reasoning: str,
        student_answer: str,
        expected_answer: str,
        execute_code: bool = True
    ) -> Dict[str, Any]:
        # 1. AST Analysis
        ast_result = self.ast_analyzer.analyze(code)

        # 2. Text/Reasoning Feature Extraction
        text_result = self.text_extractor.extract(reasoning)

        # 3. Surface Code Features
        code_result = self.code_extractor.extract(code)

        # 4. Safe Execution in Sandbox (if code present)
        exec_raw = {"stdout": "", "stderr": "", "exit_code": 0, "timeout": False}
        if execute_code and code and code.strip():
            exec_raw = self.sandbox.run(code)

        exec_result = self.exec_analyzer.analyze(exec_raw, expected_output=expected_answer)

        # 5. Evidence aggregation
        evidence_items = []
        rule_candidates = {}

        # Collect from AST
        for p in ast_result.get("detected_patterns", []):
            misc_id = p.get("misconception_id")
            conf = p.get("confidence", 0.8)
            evidence_items.append(f"AST Pattern ({p['pattern_id']}): {p['evidence']}")
            rule_candidates[misc_id] = max(rule_candidates.get(misc_id, 0.0), conf)

        # Collect from Execution
        for p in exec_result.get("detected_patterns", []):
            misc_id = p.get("misconception_candidate")
            conf = p.get("confidence", 0.75)
            evidence_items.append(f"Runtime Symptom ({p['symptom']}): {p['detail']}")
            rule_candidates[misc_id] = max(rule_candidates.get(misc_id, 0.0), conf)

        # Collect from Text
        for misc_id, cues in text_result.get("detected_cues", {}).items():
            evidence_items.append(f"Reasoning Cue for {misc_id}: Found expressions {cues}")
            rule_candidates[misc_id] = max(rule_candidates.get(misc_id, 0.0), 0.82)

        # Handle answer correctness
        is_answer_correct = (student_answer.strip().lower() == expected_answer.strip().lower()) if student_answer and expected_answer else False
        if is_answer_correct:
            evidence_items.append(f"Student answer '{student_answer}' matches expected answer '{expected_answer}'")

        # Insufficient evidence flag
        is_insufficient = text_result.get("insufficient_evidence", False) and len(rule_candidates) == 0 and not is_answer_correct

        return {
            "ast_analysis": ast_result,
            "text_features": text_result,
            "code_features": code_result,
            "execution_analysis": exec_result,
            "is_answer_correct": is_answer_correct,
            "evidence_list": evidence_items,
            "rule_candidates": rule_candidates,
            "is_insufficient_evidence": is_insufficient
        }
