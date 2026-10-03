import json

from typing import Dict, Any, List, Optional
from ml.evidence.evidence_fusion import EvidenceFusionEngine
from ml.models.nvidia_nemotron import NvidiaNemotron

class HybridMisconceptionDiagnoser:
    """Uses Nemotron as primary diagnosis with local evidence extraction."""

    def __init__(self, model_version: str = "relearn-hybrid-v1.1"):
        self.model_version = model_version
        self.evidence_engine = EvidenceFusionEngine()
        self.nemotron = NvidiaNemotron()

    def train_or_ensure(self, *args: Any, **kwargs: Any) -> None:
        """Compatibility hook for existing evaluation scripts; Nemotron is hosted."""
        return None

    def diagnose(
        self,
        question_id: str,
        question_text: str,
        student_answer: str,
        reasoning: str,
        code: str,
        expected_answer: str = "",
        previous_attempts: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        # Deterministic analysis supplies evidence to Nemotron; it does not decide the label.
        fusion = self.evidence_engine.extract_and_fuse(
            code=code,
            reasoning=reasoning,
            student_answer=student_answer,
            expected_answer=expected_answer,
            execute_code=True
        )
        analysis = self.nemotron.diagnose(
            question=question_text,
            answer=student_answer,
            reasoning=reasoning,
            code=code,
            expected_answer=expected_answer,
            deterministic_evidence=fusion["evidence_list"],
        )
        if analysis is None:
            reason = (
                "Set NVIDIA_API_KEY and restart the backend to run diagnosis with Nemotron."
                if not self.nemotron.enabled
                else "The NVIDIA NIM request failed or returned an invalid diagnosis. Check the API key, model access, and backend logs, then retry."
            )
            return {
                "status": "MODEL_UNAVAILABLE",
                "primary": {"id": "MODEL_UNAVAILABLE", "name": "Nemotron unavailable", "confidence": 0.0},
                "alternatives": [],
                "evidence": [],
                "model_version": self.nemotron.model,
                "expert_reasoning": reason,
            }

        primary_id = analysis["primary_id"]
        return {
            "status": analysis["status"],
            "primary": {
                "id": primary_id,
                "name": analysis["primary_name"] or primary_id.replace("_", " ").title(),
                "confidence": round(analysis["confidence"], 2),
            },
            "alternatives": [],
            "evidence": fusion["evidence_list"] + analysis["evidence"],
            "model_version": self.nemotron.model,
            "expert_reasoning": analysis["summary"],
        }

if __name__ == "__main__":
    diagnoser = HybridMisconceptionDiagnoser()

    # Test Diagnosis on Loop Boundary Off-by-One
    res = diagnoser.diagnose(
        question_id="Q003",
        question_text="What does for i in range(1, 5) print?",
        student_answer="1 2 3 4 5",
        reasoning="range(1, 5) starts at 1 and stops at 5 inclusive, so it prints 1 through 5.",
        code="for i in range(1, 5):\n    print(i, end=' ')",
        expected_answer="1 2 3 4"
    )
    print("Diagnosis Result for Loop Boundary:")
    print(json.dumps(res, indent=2))
