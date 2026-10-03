import os
import sys
import unittest
sys.path.insert(0, os.path.abspath("."))

from unittest.mock import MagicMock
from ml.models.hybrid_diagnoser import HybridMisconceptionDiagnoser

class TestHybridDiagnosis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.diagnoser = HybridMisconceptionDiagnoser()
        if not cls.diagnoser.nemotron.enabled:
            # Provide mock responses for testing when no NVIDIA_API_KEY is configured
            mock_nemotron = MagicMock()
            def mock_diagnose(question, answer, reasoning, code, expected_answer, deterministic_evidence):
                if answer.strip() == expected_answer.strip():
                    return {
                        "status": "CORRECT",
                        "primary_id": "CORRECT",
                        "primary_name": "Correct",
                        "confidence": 0.95,
                        "summary": "Learner answer matches expected output.",
                        "evidence": ["Exact answer match"]
                    }
                if "inclusive" in reasoning.lower() or "5" in answer:
                    return {
                        "status": "DIAGNOSED",
                        "primary_id": "P003",
                        "primary_name": "Loop Boundary / Off-by-One",
                        "confidence": 0.91,
                        "summary": "Learner included the upper boundary.",
                        "evidence": ["Off-by-one boundary pattern"]
                    }
                return {
                    "status": "INSUFFICIENT_EVIDENCE",
                    "primary_id": "INSUFFICIENT_EVIDENCE",
                    "primary_name": "Insufficient Evidence",
                    "confidence": 0.3,
                    "summary": "Not enough context.",
                    "evidence": []
                }
            mock_nemotron.diagnose.side_effect = mock_diagnose
            mock_nemotron.enabled = True
            mock_nemotron.model = "mock-nemotron"
            cls.diagnoser.nemotron = mock_nemotron


    def test_diagnose_loop_boundary_p003(self):
        res = self.diagnoser.diagnose(
            question_id="Q001",
            question_text="What does range(1, 5) print?",
            student_answer="1 2 3 4 5",
            reasoning="range(1, 5) starts at 1 and stops at 5 inclusive.",
            code="for i in range(1, 5): print(i)",
            expected_answer="1 2 3 4"
        )
        self.assertEqual(res["status"], "DIAGNOSED")
        self.assertEqual(res["primary"]["id"], "P003")
        self.assertGreater(res["primary"]["confidence"], 0.6)

    def test_diagnose_correct_answer(self):
        res = self.diagnoser.diagnose(
            question_id="Q002",
            question_text="What does range(1, 5) print?",
            student_answer="1 2 3 4",
            reasoning="range includes start 1 and excludes stop 5.",
            code="for i in range(1, 5): print(i)",
            expected_answer="1 2 3 4"
        )
        self.assertEqual(res["status"], "CORRECT")

    def test_diagnose_insufficient_evidence(self):
        res = self.diagnoser.diagnose(
            question_id="Q003",
            question_text="What does this print?",
            student_answer="idk maybe 3",
            reasoning="not sure broke",
            code="print(3)",
            expected_answer="5"
        )
        self.assertEqual(res["status"], "INSUFFICIENT_EVIDENCE")

if __name__ == "__main__":
    unittest.main()
