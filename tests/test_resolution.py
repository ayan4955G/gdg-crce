import os
import sys
import unittest
sys.path.insert(0, os.path.abspath("."))

from ml.models.resolution_model import IndependentResolutionAssessor

class TestResolutionAssessor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assessor = IndependentResolutionAssessor()

    def test_likely_resolved_when_transfer_passed(self):
        attempts = [
            {
                "question_type": "isomorphic",
                "question_text": "What does range(2, 5) print?",
                "student_answer": "2 3 4",
                "expected_answer": "2 3 4",
                "reasoning": "range stops before 5.",
                "code": "for i in range(2, 5): print(i)"
            },
            {
                "question_type": "transfer",
                "question_text": "How many iterations for while i < 4 starting at 0?",
                "student_answer": "4",
                "expected_answer": "4",
                "reasoning": "0, 1, 2, 3 gives 4 runs.",
                "code": "i = 0\nwhile i < 4: i += 1"
            }
        ]
        res = self.assessor.assess_resolution("P003", attempts)
        self.assertEqual(res["status"], "LIKELY_RESOLVED")
        self.assertTrue(res["evidence"]["similar_problem"])
        self.assertTrue(res["evidence"]["transfer_problem"])

    def test_unresolved_when_misconception_reoccurs(self):
        attempts = [
            {
                "question_type": "transfer",
                "question_text": "What does range(1, 4) print?",
                "student_answer": "1 2 3 4",
                "expected_answer": "1 2 3",
                "reasoning": "range(1, 4) is inclusive of 4.",
                "code": "for i in range(1, 4): print(i)"
            }
        ]
        res = self.assessor.assess_resolution("P003", attempts)
        self.assertEqual(res["status"], "UNRESOLVED")
        self.assertTrue(res["evidence"]["misconception_still_detected"])

if __name__ == "__main__":
    unittest.main()
