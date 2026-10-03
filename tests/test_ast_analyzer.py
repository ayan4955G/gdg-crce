import os
import sys
import unittest
sys.path.insert(0, os.path.abspath("."))

from ml.evidence.ast_analyzer import CodeASTAnalyzer

class TestCodeASTAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = CodeASTAnalyzer()

    def test_boolean_or_constant_detection_p006(self):
        code = "if x == 1 or 2:\n    print('Match')"
        res = self.analyzer.analyze(code)
        self.assertTrue(res["parse_success"])
        pattern_ids = [p["pattern_id"] for p in res["detected_patterns"]]
        self.assertIn("BOOL_CONSTANT_IN_OR", pattern_ids)

    def test_range_plus_one_detection_p003(self):
        code = "for i in range(len(items) + 1):\n    print(items[i])"
        res = self.analyzer.analyze(code)
        self.assertTrue(res["parse_success"])
        pattern_ids = [p["pattern_id"] for p in res["detected_patterns"]]
        self.assertIn("RANGE_LEN_PLUS_ONE", pattern_ids)

    def test_print_without_return_p007(self):
        code = "def calculate(a, b):\n    print(a + b)"
        res = self.analyzer.analyze(code)
        self.assertTrue(res["parse_success"])
        pattern_ids = [p["pattern_id"] for p in res["detected_patterns"]]
        self.assertIn("FUNCTION_PRINT_WITHOUT_RETURN", pattern_ids)

    def test_shallow_list_multiplication_p010(self):
        code = "grid = [[0] * 3] * 3"
        res = self.analyzer.analyze(code)
        self.assertTrue(res["parse_success"])
        pattern_ids = [p["pattern_id"] for p in res["detected_patterns"]]
        self.assertIn("SHALLOW_LIST_MULTIPLICATION", pattern_ids)

    def test_syntax_error_assignment_p001(self):
        code = "x + 1 = 5"
        res = self.analyzer.analyze(code)
        self.assertFalse(res["parse_success"])
        pattern_ids = [p["pattern_id"] for p in res["detected_patterns"]]
        self.assertIn("LHS_EXPRESSION_ASSIGNMENT", pattern_ids)

if __name__ == "__main__":
    unittest.main()
