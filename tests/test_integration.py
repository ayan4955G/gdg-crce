import os
import sys
import unittest
sys.path.insert(0, os.path.abspath("."))

from fastapi.testclient import TestClient
from backend.app.main import app

class TestReLearnEndToEndIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.learner_id = "L_INTEGRATION_TEST_99"

    def test_complete_learning_and_remediation_lifecycle(self):
        # 1. Fetch Question Catalog
        q_res = self.client.get("/api/v1/questions")
        self.assertEqual(q_res.status_code, 200)
        questions = q_res.json()
        self.assertGreater(len(questions), 0)
        q = questions[0]

        # 2. Submit initial answer with misconception P003
        diag_payload = {
            "question_id": q["id"],
            "question": q["prompt"],
            "response": "1 2 3 4 5",
            "reasoning": "range(1, 5) starts at 1 and stops at 5 inclusive.",
            "code": q["starter_code"],
            "expected_answer": q["expected_answer"]
        }
        d_res = self.client.post("/api/v1/diagnose", json=diag_payload)
        self.assertEqual(d_res.status_code, 200)
        diag_data = d_res.json()
        self.assertEqual(diag_data["status"], "DIAGNOSED")
        self.assertEqual(diag_data["primary"]["id"], "P003")

        # 3. Update learner model with initial struggle
        rec_res = self.client.post(
            f"/api/v1/learner/{self.learner_id}/record-interaction?question_id={q['id']}&concept={q['concept']}&is_correct=false&misconception_id=P003"
        )
        self.assertEqual(rec_res.status_code, 200)
        profile_after_fail = rec_res.json()
        self.assertIn("P003", profile_after_fail["misconceptions"])
        self.assertFalse(profile_after_fail["misconceptions"]["P003"]["resolved"])

        # 4. Generate targeted pedagogical intervention
        int_payload = {
            "misconception_id": "P003",
            "learner_response": "1 2 3 4 5"
        }
        int_res = self.client.post("/api/v1/intervention", json=int_payload)
        self.assertEqual(int_res.status_code, 200)
        int_data = int_res.json()
        self.assertEqual(int_data["target_misconception"], "P003")
        self.assertTrue(int_data["is_validated"])

        # 5. Submit transfer battery for independent resolution assessment
        res_payload = {
            "misconception_id": "P003",
            "attempts": [
                {
                    "question_type": "isomorphic",
                    "question_text": "range(2, 6) check",
                    "student_answer": "2 3 4 5",
                    "expected_answer": "2 3 4 5",
                    "reasoning": "stops before 6.",
                    "code": "for i in range(2, 6):\n    print(i, end=' ')"
                },
                {
                    "question_type": "transfer",
                    "question_text": "while i < 5 check",
                    "student_answer": "5",
                    "expected_answer": "5",
                    "reasoning": "i takes values 0, 1, 2, 3, 4 so 5 iterations.",
                    "code": "i = 0\nwhile i < 5:\n    i += 1\nprint(i)"
                }
            ]
        }
        res_res = self.client.post("/api/v1/assess-resolution", json=res_payload)
        self.assertEqual(res_res.status_code, 200)
        res_data = res_res.json()
        self.assertEqual(res_data["status"], "LIKELY_RESOLVED")

        # 6. Verify final cognitive state in learner profile
        rec_pass = self.client.post(
            f"/api/v1/learner/{self.learner_id}/record-interaction?question_id=TRANSFER_Q&concept={q['concept']}&is_correct=true&misconception_id=P003"
        )
        self.assertEqual(rec_pass.status_code, 200)
        final_profile = self.client.get(f"/api/v1/learner/{self.learner_id}/profile").json()
        self.assertEqual(final_profile["learner_id"], self.learner_id)
        self.assertGreater(final_profile["total_interactions"], 1)

if __name__ == "__main__":
    unittest.main()
