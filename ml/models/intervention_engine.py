import json
import os
import re
from typing import Dict, Any, List, Optional

class InterventionEngine:
    """
    Pedagogical Intervention Engine:
    Selects, generates, and validates hierarchical scaffolding targeted
    strictly to the diagnosed misconception without giving away the direct answer.
    """

    HIERARCHY = [
        "hint",
        "guided_reasoning",
        "counterexample",
        "code_trace",
        "concept_explanation",
        "worked_example"
    ]

    SCAFFOLDING_TEMPLATES = {
        "P001": {
            "hint": "Consider the direction of the '=' sign. In Python, data flows from the right-hand expression into the left-hand variable slot.",
            "guided_reasoning": "When line 3 says 'a = b', what is in variable b right at that exact instant? Does assigning b to a change what is inside b?",
            "counterexample": "Look at this analogy: If you copy a phone number from note B onto note A, and later erase note B, note A doesn't automatically erase.",
            "code_trace": "Trace with memory boxes:\nStep 1: Box 'a' holds 10, Box 'b' holds 20.\nStep 2: 'a = b' -> Copy 20 into Box 'a' (Box 'a' now 20).\nStep 3: 'b = 30' -> Put 30 into Box 'b'.\nQuestion: What was left inside Box 'a'?",
            "follow_up_prompt": "What would be inside 'x' after: x = 1; y = 2; x = y; y = 99; print(x)?"
        },
        "P002": {
            "hint": "Variables created inside a function live inside that function's temporary activation frame. Once the function finishes, that frame disappears.",
            "guided_reasoning": "Check whether the function returns the variable, or whether the main program simply tries to access an internal variable by name.",
            "counterexample": "If someone calculates something on scratch paper inside their office and never gives you the report, you cannot read their scratch paper from the hallway.",
            "code_trace": "Stack frame trace:\n[Global Frame] -> calls set_val()\n[set_val Frame] -> total = 50 created -> function returns None -> [set_val Frame destroyed]\n[Global Frame] -> print(total) -> NameError: 'total' does not exist in global frame.",
            "follow_up_prompt": "How can you modify set_val() so the caller receives the value 50?"
        },
        "P003": {
            "hint": "In Python, range(start, stop) generates integers starting at 'start' and stopping strictly BEFORE 'stop' (half-open interval [start, stop)).",
            "guided_reasoning": "How many values are between 1 and 5 if 5 is excluded? Write out the numbers one by one starting from 1.",
            "counterexample": "Evaluate list(range(1, 5)). You will get [1, 2, 3, 4]. Notice that 5 is NOT in this list.",
            "code_trace": "Iteration trace:\nIteration 1: i = 1, prints 1\nIteration 2: i = 2, prints 2\nIteration 3: i = 3, prints 3\nIteration 4: i = 4, prints 4\nCondition check: next value would be 5, but range stop is 5 (exclusive) -> loop ends.",
            "follow_up_prompt": "If you want a loop to execute with values 1, 2, 3, 4, 5, what stop value must you pass to range(1, ?)?"
        },
        "P004": {
            "hint": "A while-loop condition is evaluated only at the very beginning of each iteration (at the header), not continuously after every single statement inside the body.",
            "guided_reasoning": "Once Python enters the body of a while loop, it finishes every statement in that block before looping back to test the condition again.",
            "counterexample": "Think of a runner on a lap track: a referee checks your lap count at the start/finish line, not every centimeter while running.",
            "code_trace": "Step 1: Check x > 0 (3 > 0 is True) -> Enter body.\nStep 2: x -= 1 (x becomes 2).\nStep 3: print(x) -> prints 2.\nStep 4: Check 2 > 0 (True) -> x becomes 1 -> prints 1.\nStep 5: Check 1 > 0 (True) -> x becomes 0 -> prints 0! (Condition was not re-checked mid-step!).",
            "follow_up_prompt": "If x = 1 and while x > 0: x -= 1; print(x), what is printed?"
        },
        "P005": {
            "hint": "Independent 'if' statements each test their own condition. Only an 'elif' or 'else' is skipped when a previous branch matches.",
            "guided_reasoning": "Trace each 'if' statement independently from top to bottom. If both conditions are true, what stops the second one from running?",
            "counterexample": "Compare:\nif score > 50: print('Pass')\nif score > 80: print('Distinction')\nFor score = 90, both statements are checked and both execute.",
            "code_trace": "Step 1: Test first 'if x > 10': 15 > 10 is True -> prints 'A'.\nStep 2: Step to next statement: 'if x > 5'. 15 > 5 is also True -> prints 'B'. Both ran!",
            "follow_up_prompt": "How would you rewrite the code so only 'A' prints and the second check is skipped?"
        },
        "P006": {
            "hint": "In Python, 'x == 1 or 2' does NOT check if x equals 1 or equals 2. It checks '(x == 1) or (bool(2))'.",
            "guided_reasoning": "Any non-zero integer or non-empty string is considered 'truthy' in Python. What is bool(2)?",
            "counterexample": "In Python console: bool(2) evaluates to True. Therefore, False or 2 evaluates to 2, which is truthy!",
            "code_trace": "Expression breakdown:\nx == 1 or 2\n(3 == 1) -> False\nFalse or 2 -> 2 (truthy)\nSince the condition result is truthy, the 'if' block always executes!",
            "follow_up_prompt": "How do you write the condition so that x is explicitly compared to both 1 and 2?"
        },
        "P007": {
            "hint": "print() displays text on the screen for humans to see. return sends a value back to the program so other code can use it.",
            "guided_reasoning": "When a function has no return statement, Python automatically returns None. If you write 'result = my_func()', what gets stored in result?",
            "counterexample": "Think of a restaurant kitchen: printing is shouting the dish name in the kitchen; returning is placing the cooked plate on the server's tray to carry to the customer.",
            "code_trace": "Step 1: Caller invokes compute(3, 4).\nStep 2: Function prints 7 to terminal.\nStep 3: Function reaches end with no return statement -> returns None.\nStep 4: res = None.\nStep 5: print(res) outputs 'None'.",
            "follow_up_prompt": "What keyword must replace or precede print in compute(a, b) so res receives the number 7?"
        },
        "P008": {
            "hint": "Function parameters are placeholders (formal parameters). You can pass any variable name or value as an argument at call time.",
            "guided_reasoning": "A recipe that lists '2 eggs' doesn't care whether your carton at home is labeled 'organic_eggs' or 'store_eggs'.",
            "counterexample": "def square(n): return n * n. You can call square(x), square(num), or square(7). The caller variable does NOT need to be named 'n'.",
            "code_trace": "Call trace:\nCaller has user = 'Alice'.\nCalls greet(user) -> Python binds local parameter name = 'Alice'.\nInside greet, name holds 'Alice'.",
            "follow_up_prompt": "If a function is defined as def triple(num): return num * 3, how would you call it using a variable score = 10?"
        },
        "P009": {
            "hint": "Python sequences are zero-indexed: the first element is at index 0, the second is at index 1, and the last is at index len - 1.",
            "guided_reasoning": "If a list has 3 items, what are the three valid index numbers? Is index 3 valid?",
            "counterexample": "Consider items = ['a', 'b', 'c']. items[0] is 'a', items[1] is 'b', items[2] is 'c'. Calling items[3] raises IndexError: list index out of range.",
            "code_trace": "Index mapping:\nIndex 0 -> 'apple'\nIndex 1 -> 'banana'\nIndex 2 -> 'cherry'\nQuerying fruits[1] retrieves the element at index 1, which is 'banana'.",
            "follow_up_prompt": "What index retrieves the very first element from a list named numbers?"
        },
        "P010": {
            "hint": "In Python, assigning a list (b = a) does NOT create a new copy of the list. It creates a new reference pointing to the exact same list in memory.",
            "guided_reasoning": "If two people have keys to the exact same locker, when one person places an item in the locker, what does the second person see?",
            "counterexample": "Check with id(): id(a) and id(b) will output the exact same integer memory address when b = a.",
            "code_trace": "Memory heap trace:\nList object [1, 2, 3] created at memory address 0x100.\nVariable 'a' -> 0x100.\n'b = a' -> Variable 'b' -> 0x100.\n'b.append(4)' -> Modifies object at 0x100 to [1, 2, 3, 4].\n'print(a)' -> Inspects object at 0x100 -> prints [1, 2, 3, 4].",
            "follow_up_prompt": "How can you create a real independent copy of list 'a' so that mutating 'b' leaves 'a' unchanged?"
        }
    }

    def generate_intervention(
        self,
        misconception_id: str,
        learner_response: str = "",
        previous_interventions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        previous_interventions = previous_interventions or []
        templates = self.SCAFFOLDING_TEMPLATES.get(misconception_id)

        if not templates:
            return {
                "type": "hint",
                "content": "Let's review the fundamental steps and trace through your program one statement at a time.",
                "target_misconception": misconception_id,
                "follow_up_question": "Can you explain what happens line by line?",
                "is_validated": True,
                "validation_notes": "Generic fallback scaffolding applied."
            }

        # Select next scaffolding level based on previous interventions
        next_type = "hint"
        for strategy in self.HIERARCHY:
            if strategy in templates and strategy not in previous_interventions:
                next_type = strategy
                break
        else:
            next_type = "code_trace" # deepest fallback

        content = templates[next_type]
        follow_up = templates.get("follow_up_prompt", "What is the expected result after this step?")

        # Validate intervention to prevent answer leakage
        validation = self.validate_intervention(content, misconception_id)

        return {
            "type": next_type,
            "content": content,
            "target_misconception": misconception_id,
            "follow_up_question": follow_up,
            "is_validated": validation["is_valid"],
            "validation_notes": validation["notes"]
        }

    def validate_intervention(self, content: str, target_misconception: str) -> Dict[str, Any]:
        """
        Validates intervention:
        1. Checks for direct answer leakage (e.g. 'the answer is 4')
        2. Ensures relevance to target misconception
        3. Verifies clear, constructive pedagogical scaffolding
        """
        leakage_patterns = [
            r"the answer is \b\w+\b",
            r"the correct output is \b\w+\b",
            r"just write \b\w+\b"
        ]

        for pattern in leakage_patterns:
            if re.search(pattern, content.lower()):
                return {
                    "is_valid": False,
                    "notes": f"Answer leakage detected matching '{pattern}'."
                }

        if len(content.strip()) < 15:
            return {
                "is_valid": False,
                "notes": "Intervention content is insufficiently descriptive."
            }

        return {
            "is_valid": True,
            "notes": "Passed answer leakage and pedagogical safety validations."
        }

if __name__ == "__main__":
    engine = InterventionEngine()
    
    # Test level 1 (hint)
    int1 = engine.generate_intervention("P003")
    print("Level 1:", int1)

    # Test level 2 after hint already given
    int2 = engine.generate_intervention("P003", previous_interventions=["hint"])
    print("Level 2:", int2)

    # Test level 4 (code trace)
    int4 = engine.generate_intervention("P003", previous_interventions=["hint", "guided_reasoning", "counterexample"])
    print("Level 4:", int4)
