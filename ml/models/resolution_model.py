import os
import sys
sys.path.insert(0, os.path.abspath("."))

from typing import Dict, Any, List, Optional
from ml.models.hybrid_diagnoser import HybridMisconceptionDiagnoser

class IndependentResolutionAssessor:
    """
    Independent Resolution Model:
    Evaluates new student responses across isomorphic problems and structurally
    novel transfer questions to objectively assess whether the original misconception
    is truly resolved, improving, or persistent.
    
    CRITICAL PRINCIPLE:
    Independent of the intervention generator. It evaluates only post-intervention
    evidence using the diagnostic pipeline and multi-attempt performance trajectories.
    """

    def __init__(self, diagnoser: Optional[HybridMisconceptionDiagnoser] = None):
        self.diagnoser = diagnoser or HybridMisconceptionDiagnoser(model_version="resolution-assessor-v1.0")

    def assess_resolution(
        self,
        misconception_id: str,
        attempts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Input attempts list structure:
        [
          {
            "question_type": "isomorphic" | "different_surface" | "transfer",
            "question_text": "...",
            "student_answer": "...",
            "expected_answer": "...",
            "reasoning": "...",
            "code": "..."
          },
          ...
        ]
        """
        if not attempts:
            return {
                "status": "INSUFFICIENT_EVIDENCE",
                "confidence": 0.50,
                "evidence": {
                    "isomorphic_passed": False,
                    "different_surface_passed": False,
                    "transfer_passed": False,
                    "attempts_evaluated": 0
                },
                "summary": "No post-intervention attempts provided to assess resolution."
            }

        evaluated_attempts = []
        misconception_still_detected = False
        isomorphic_passed = False
        different_surface_passed = False
        transfer_passed = False

        for att in attempts:
            q_type = att.get("question_type", "isomorphic")
            q_text = att.get("question_text", "")
            student_ans = att.get("student_answer", "")
            expected_ans = att.get("expected_answer", "")
            code = att.get("code", "")
            reasoning = att.get("reasoning", "")

            # Diagnose the attempt INDEPENDENTLY
            diag = self.diagnoser.diagnose(
                question_id="ATTEMPT_Q",
                question_text=q_text,
                student_answer=student_ans,
                reasoning=reasoning,
                code=code,
                expected_answer=expected_ans
            )

            is_correct = (diag["status"] == "CORRECT")
            has_original_misc = (
                diag["status"] == "DIAGNOSED" and
                diag.get("primary", {}).get("id") == misconception_id
            )

            if has_original_misc:
                misconception_still_detected = True

            if is_correct:
                if q_type == "isomorphic":
                    isomorphic_passed = True
                elif q_type == "different_surface":
                    different_surface_passed = True
                elif q_type == "transfer":
                    transfer_passed = True

            evaluated_attempts.append({
                "type": q_type,
                "is_correct": is_correct,
                "diagnosed_status": diag["status"],
                "diagnosed_misconception": diag.get("primary", {}).get("id"),
                "confidence": diag.get("primary", {}).get("confidence", 0.0)
            })

        # Calculate final resolution status & confidence
        # Criteria:
        # LIKELY_RESOLVED: Transfer passed + at least one isomorphic/different passed + misconception not detected
        # IMPROVING: Isomorphic passed, but transfer not yet passed or minor lingering issues
        # UNRESOLVED: Misconception actively rediagnosed or all attempts failed
        # INSUFFICIENT_EVIDENCE: Only 1 attempt or inconclusive answers
        
        num_passed = sum([isomorphic_passed, different_surface_passed, transfer_passed])
        
        if transfer_passed and (isomorphic_passed or different_surface_passed) and not misconception_still_detected:
            status = "LIKELY_RESOLVED"
            confidence = 0.92
            summary = f"Student solved transfer and isomorphic problems. Conceptual misconception {misconception_id} is successfully remediated."
        elif transfer_passed and not misconception_still_detected:
            status = "LIKELY_RESOLVED"
            confidence = 0.85
            summary = "Transfer question passed without recurrence of the diagnosed misconception."
        elif (isomorphic_passed or different_surface_passed) and not misconception_still_detected:
            status = "IMPROVING"
            confidence = 0.76
            summary = "Student resolved the immediate isomorphic case, but transfer generalizability has not yet been demonstrated."
        elif misconception_still_detected:
            status = "UNRESOLVED"
            confidence = 0.88
            summary = f"Original misconception {misconception_id} was repeatedly rediagnosed during reassessment."
        else:
            status = "UNRESOLVED"
            confidence = 0.70
            summary = "Learner responses were incorrect without resolving the target conceptual barrier."

        return {
            "status": status,
            "confidence": round(confidence, 2),
            "evidence": {
                "similar_problem": isomorphic_passed,
                "different_problem": different_surface_passed,
                "transfer_problem": transfer_passed,
                "misconception_still_detected": misconception_still_detected,
                "attempts_evaluated": len(attempts)
            },
            "summary": summary,
            "attempt_evaluations": evaluated_attempts
        }

if __name__ == "__main__":
    assessor = IndependentResolutionAssessor()
    
    # Test Resolution: Learner solves isomorphic and transfer loop question
    mock_attempts = [
        {
            "question_type": "isomorphic",
            "question_text": "What does range(2, 6) print?",
            "student_answer": "2 3 4 5",
            "expected_answer": "2 3 4 5",
            "reasoning": "range(2, 6) starts at 2 and stops at 6 exclusive, so 2, 3, 4, 5.",
            "code": "for i in range(2, 6): print(i)"
        },
        {
            "question_type": "transfer",
            "question_text": "How many times does this while loop execute: i = 0; while i < 5: i += 1?",
            "student_answer": "5",
            "expected_answer": "5",
            "reasoning": "i takes values 0, 1, 2, 3, 4, which is 5 iterations total.",
            "code": "i = 0\nwhile i < 5:\n    i += 1"
        }
    ]

    res = assessor.assess_resolution("P003", mock_attempts)
    print("Resolution Assessment Result:")
    import json
    print(json.dumps(res, indent=2))
