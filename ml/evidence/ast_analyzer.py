import ast
from typing import Dict, Any, List, Set

class CodeASTAnalyzer:
    """
    Analyzes Python code AST to extract syntactic constructs, structural metrics,
    and detect concrete diagnostic anti-patterns mapped to known programming misconceptions.
    """

    def analyze(self, code: str) -> Dict[str, Any]:
        if not code or not code.strip():
            return {
                "parse_success": False,
                "error": "Empty code snippet",
                "features": {},
                "detected_patterns": []
            }

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "parse_success": False,
                "error": str(e),
                "syntax_error_line": e.lineno,
                "features": {"has_syntax_error": True},
                "detected_patterns": self._check_syntax_error_patterns(code, str(e))
            }

        features = self._extract_ast_features(tree)
        detected_patterns = self._detect_misconception_patterns(tree, code)

        return {
            "parse_success": True,
            "error": None,
            "features": features,
            "detected_patterns": detected_patterns
        }

    def _extract_ast_features(self, tree: ast.AST) -> Dict[str, Any]:
        num_for_loops = 0
        num_while_loops = 0
        num_if_branches = 0
        num_returns = 0
        num_prints = 0
        num_subscripts = 0
        assigned_variables = set()
        loaded_variables = set()
        function_defs = []

        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                num_for_loops += 1
            elif isinstance(node, ast.While):
                num_while_loops += 1
            elif isinstance(node, ast.If):
                num_if_branches += 1
            elif isinstance(node, ast.Return):
                num_returns += 1
            elif isinstance(node, ast.Subscript):
                num_subscripts += 1
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    num_prints += 1
            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    assigned_variables.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    loaded_variables.add(node.id)
            elif isinstance(node, ast.FunctionDef):
                function_defs.append(node.name)

        return {
            "num_for_loops": num_for_loops,
            "num_while_loops": num_while_loops,
            "num_if_branches": num_if_branches,
            "num_returns": num_returns,
            "num_prints": num_prints,
            "num_subscripts": num_subscripts,
            "num_functions": len(function_defs),
            "assigned_variables": list(assigned_variables),
            "loaded_variables": list(loaded_variables),
            "has_syntax_error": False
        }

    def _detect_misconception_patterns(self, tree: ast.AST, code: str) -> List[Dict[str, Any]]:
        patterns = []

        for node in ast.walk(tree):
            # Check P006: Boolean Operator Misunderstanding (e.g. `x == 1 or 2`)
            if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
                for val in node.values:
                    if isinstance(val, ast.Constant) and isinstance(val.value, (int, str)):
                        patterns.append({
                            "pattern_id": "BOOL_CONSTANT_IN_OR",
                            "misconception_id": "P006",
                            "confidence": 0.95,
                            "evidence": f"Found constant '{val.value}' in 'or' expression (e.g. 'x == a or b')"
                        })

            # Check P003: Loop Boundary Off-by-One (e.g. `range(len(arr) + 1)` or `<=` on len)
            if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
                func = node.iter.func
                if isinstance(func, ast.Name) and func.id == "range":
                    args = node.iter.args
                    for arg in args:
                        if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                            if isinstance(arg.right, ast.Constant) and arg.right.value == 1:
                                patterns.append({
                                    "pattern_id": "RANGE_LEN_PLUS_ONE",
                                    "misconception_id": "P003",
                                    "confidence": 0.92,
                                    "evidence": "range() includes + 1 boundary adjustment likely causing IndexError or off-by-one"
                                })

            # Check P007: Return vs Print (Function ends with print, missing return, caller assigns call)
            if isinstance(node, ast.FunctionDef):
                has_return = any(isinstance(sub, ast.Return) and sub.value is not None for sub in ast.walk(node))
                has_print = any(isinstance(sub, ast.Call) and isinstance(getattr(sub, "func", None), ast.Name) and sub.func.id == "print" for sub in ast.walk(node))
                if has_print and not has_return:
                    patterns.append({
                        "pattern_id": "FUNCTION_PRINT_WITHOUT_RETURN",
                        "misconception_id": "P007",
                        "confidence": 0.85,
                        "evidence": f"Function '{node.name}' uses print() but has no return statement."
                    })

            # Check P010: List reference replication (e.g. `[row] * n` or `[[]] * n`)
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
                if isinstance(node.left, ast.List) and len(node.left.elts) > 0:
                    patterns.append({
                        "pattern_id": "SHALLOW_LIST_MULTIPLICATION",
                        "misconception_id": "P010",
                        "confidence": 0.88,
                        "evidence": "Multiplying a list containing mutable elements duplicates object references."
                    })

            # Check P009: Subscript with non-integer or string literal lookup
            if isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                    patterns.append({
                        "pattern_id": "STRING_SUBSCRIPT_ON_SEQUENCE",
                        "misconception_id": "P009",
                        "confidence": 0.80,
                        "evidence": f"Indexing sequence using string literal '{node.slice.value}'"
                    })

        return patterns

    def _check_syntax_error_patterns(self, code: str, error_msg: str) -> List[Dict[str, Any]]:
        patterns = []
        # Check P001: Left-hand side assignment error (e.g. `x + 1 = 5`)
        if "cannot assign to" in error_msg.lower() or "cannot assign to operator" in error_msg.lower():
            patterns.append({
                "pattern_id": "LHS_EXPRESSION_ASSIGNMENT",
                "misconception_id": "P001",
                "confidence": 0.98,
                "evidence": "SyntaxError attempting to assign to an expression/operator on left-hand side."
            })
        return patterns

if __name__ == "__main__":
    analyzer = CodeASTAnalyzer()
    
    # Test Boolean operator pattern
    res1 = analyzer.analyze("if x == 1 or 2: print('yes')")
    print("Bool test patterns:", res1["detected_patterns"])

    # Test Return vs Print pattern
    res2 = analyzer.analyze("def add(a, b):\n    print(a + b)")
    print("Function patterns:", res2["detected_patterns"])

    # Test Assignment SyntaxError pattern
    res3 = analyzer.analyze("x + 1 = 5")
    print("Syntax error patterns:", res3["detected_patterns"])
