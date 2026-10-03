import os
import sys
import unittest
sys.path.insert(0, os.path.abspath("."))

from ml.models.intervention_engine import InterventionEngine

class TestInterventionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = InterventionEngine()

    def test_scaffolding_hierarchy_progression(self):
        # 1st level: hint
        int1 = self.engine.generate_intervention("P003")
        self.assertEqual(int1["type"], "hint")
        self.assertTrue(int1["is_validated"])

        # 2nd level: guided reasoning
        int2 = self.engine.generate_intervention("P003", previous_interventions=["hint"])
        self.assertEqual(int2["type"], "guided_reasoning")

        # 3rd level: counterexample
        int3 = self.engine.generate_intervention("P003", previous_interventions=["hint", "guided_reasoning"])
        self.assertEqual(int3["type"], "counterexample")

    def test_answer_leakage_validation(self):
        # Content with direct answer leakage should fail validation
        leaky_content = "Do not worry, the answer is 4."
        val = self.engine.validate_intervention(leaky_content, "P003")
        self.assertFalse(val["is_valid"])

        # Valid pedagogical scaffolding should pass
        valid_content = "Notice that range(start, stop) excludes the stop boundary."
        val2 = self.engine.validate_intervention(valid_content, "P003")
        self.assertTrue(val2["is_valid"])

if __name__ == "__main__":
    unittest.main()
