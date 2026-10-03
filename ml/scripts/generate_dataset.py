import os
import json
import random
from typing import List, Dict, Any

# Ensure reproducibility
random.seed(42)

MISCONCEPTION_TEMPLATES = {
    "P001": {
        "concept": "variables",
        "name": "Variable Assignment Confusion",
        "scenarios": [
            {
                "question": "What is printed by this code?\n\na = 10\nb = 20\na = b\nb = 30\nprint(a)",
                "code": "a = 10\nb = 20\na = b\nb = 30\nprint(a)",
                "expected": "20",
                "wrong_answers": [
                    ("30", "Since a was assigned b (a = b), a is permanently tied to b, so changing b to 30 also changes a to 30."),
                    ("10", "a = b sets b to a, so a stays 10 and b becomes 10."),
                    ("30", "Variable assignment is an algebraic equality relation; whenever b changes, a changes automatically.")
                ],
                "correct_reasoning": "a = b copies the current value of b (20) into a. Subsequent changes to b do not affect a, so print(a) outputs 20."
            },
            {
                "question": "How do you swap the values of two variables x and y without tuple unpacking?\nConsider:\nx = y\ny = x\nprint(x, y) with x=5, y=9",
                "code": "x = 5\ny = 9\nx = y\ny = x\nprint(x, y)",
                "expected": "9 9",
                "wrong_answers": [
                    ("9 5", "x = y and y = x swaps them simultaneously because both are assigned to each other."),
                    ("5 9", "Assignment sets them equal to each other at the same time.")
                ],
                "correct_reasoning": "x = y overwrites x with 9. Then y = x assigns the new value of x (9) to y, resulting in 9 9 instead of swapping."
            },
            {
                "question": "What is the result of attempting:\nx + 1 = 5",
                "code": "x + 1 = 5",
                "expected": "SyntaxError",
                "wrong_answers": [
                    ("4", "Solves for x algebraically so x is assigned 4."),
                    ("5", "Sets x + 1 to equal 5.")
                ],
                "correct_reasoning": "Python assignment requires a single assignable target identifier on the left-hand side, not an algebraic expression."
            }
        ]
    },
    "P002": {
        "concept": "functions_and_scope",
        "name": "Variable Scope Confusion",
        "scenarios": [
            {
                "question": "What is the output of the following program?\n\ndef set_val():\n    total = 50\n\nset_val()\nprint(total)",
                "code": "def set_val():\n    total = 50\n\nset_val()\nprint(total)",
                "expected": "NameError",
                "wrong_answers": [
                    ("50", "The function set_val() defined total as 50, so total is now 50 globally."),
                    ("None", "The function ran so total is set to None.")
                ],
                "correct_reasoning": "'total' is a local variable inside set_val and ceases to exist once the function finishes executing."
            },
            {
                "question": "What is printed?\n\nscore = 10\ndef add_bonus(score):\n    score = score + 5\n\nadd_bonus(score)\nprint(score)",
                "code": "score = 10\ndef add_bonus(score):\n    score = score + 5\n\nadd_bonus(score)\nprint(score)",
                "expected": "10",
                "wrong_answers": [
                    ("15", "The function modified the score parameter, so the original score variable in main program updated to 15."),
                    ("None", "The function has no return so score becomes None.")
                ],
                "correct_reasoning": "Numbers are immutable in Python and passed by value/object-reference; re-binding the local parameter 'score' does not modify the global 'score'."
            }
        ]
    },
    "P003": {
        "concept": "loops",
        "name": "Loop Boundary / Off-by-One",
        "scenarios": [
            {
                "question": "What does this code print?\n\nfor i in range(1, 5):\n    print(i, end=' ')",
                "code": "for i in range(1, 5):\n    print(i, end=' ')",
                "expected": "1 2 3 4",
                "wrong_answers": [
                    ("1 2 3 4 5", "range(1, 5) starts at 1 and stops at 5 inclusive, so it prints 1 through 5."),
                    ("0 1 2 3 4", "range always starts at 0 regardless of first argument."),
                    ("1 2 3 4 5", "Loop executes 5 times starting from 1.")
                ],
                "correct_reasoning": "range(start, stop) in Python includes 'start' and stops before 'stop' (half-open [1, 5)), generating 1, 2, 3, 4."
            },
            {
                "question": "What is the output?\n\nnums = [10, 20, 30]\nfor i in range(len(nums) + 1):\n    print(nums[i])",
                "code": "nums = [10, 20, 30]\nfor i in range(len(nums) + 1):\n    print(nums[i])",
                "expected": "IndexError",
                "wrong_answers": [
                    ("10 20 30", "Loop iterates through all elements properly because len(nums)+1 covers all indices."),
                    ("10 20 30 None", "The last element is empty/None.")
                ],
                "correct_reasoning": "Valid indices for nums (length 3) are 0, 1, 2. range(4) generates index 3, which triggers IndexError: list index out of range."
            },
            {
                "question": "How many times does this loop execute?\n\ni = 0\nwhile i <= 5:\n    i += 1",
                "code": "i = 0\nwhile i <= 5:\n    i += 1",
                "expected": "6",
                "wrong_answers": [
                    ("5", "The loop stops when i is 5, so it runs 5 times."),
                    ("4", "Zero index means 5 minus 1 times.")
                ],
                "correct_reasoning": "i takes values 0, 1, 2, 3, 4, 5 — exactly 6 iterations."
            }
        ]
    },
    "P004": {
        "concept": "loops",
        "name": "Loop Condition Misunderstanding",
        "scenarios": [
            {
                "question": "What is the output?\n\nx = 3\nwhile x > 0:\n    x -= 1\n    print(x, end=' ')",
                "code": "x = 3\nwhile x > 0:\n    x -= 1\n    print(x, end=' ')",
                "expected": "2 1 0",
                "wrong_answers": [
                    ("2 1", "The condition says x > 0, so as soon as x becomes 0 the loop immediately terminates before print."),
                    ("3 2 1", "x starts at 3 so 3 is printed first."),
                    ("2 1", "Loop checks the condition continually inside the body and aborts mid-iteration.")
                ],
                "correct_reasoning": "The loop condition is only evaluated at the top of each iteration. Inside the body, x becomes 0 and print(0) executes before the next header check."
            },
            {
                "question": "What happens when this runs?\n\ncount = 0\nwhile count == 5:\n    print(count)\n    count += 1",
                "code": "count = 0\nwhile count == 5:\n    print(count)\n    count += 1",
                "expected": "Nothing printed",
                "wrong_answers": [
                    ("0 1 2 3 4 5", "The loop repeats until count reaches 5."),
                    ("5", "It loops until count is 5 then prints 5.")
                ],
                "correct_reasoning": "While-loop condition is a continuation condition ('while true, keep going'), not an exit condition ('stop when'). Since count == 5 is immediately False, the body never runs."
            }
        ]
    },
    "P005": {
        "concept": "conditionals",
        "name": "Conditional Logic Misunderstanding",
        "scenarios": [
            {
                "question": "What is printed by this code?\n\nx = 15\nif x > 10:\n    print('A')\nif x > 5:\n    print('B')",
                "code": "x = 15\nif x > 10:\n    print('A')\nif x > 5:\n    print('B')",
                "expected": "A\nB",
                "wrong_answers": [
                    ("A", "Only the first matching if-statement executes in a program."),
                    ("B", "The second if overwrites the first one because 15 > 5 is also true.")
                ],
                "correct_reasoning": "These are two independent 'if' statements, not an if-elif ladder. Both conditions are checked and both evaluate to True, printing both A and B."
            },
            {
                "question": "What is printed?\n\nval = 8\nif val > 10:\n    val += 2\nelif val > 5:\n    val += 5\nelif val > 2:\n    val += 10\nprint(val)",
                "code": "val = 8\nif val > 10:\n    val += 2\nelif val > 5:\n    val += 5\nelif val > 2:\n    val += 10\nprint(val)",
                "expected": "13",
                "wrong_answers": [
                    ("23", "Both val > 5 and val > 2 are true for 8, so both elif branches add (8 + 5 + 10 = 23)."),
                    ("8", "No branch matches.")
                ],
                "correct_reasoning": "In an if-elif-else chain, as soon as one branch matches (val > 5), its body runs and the entire rest of the chain is skipped."
            }
        ]
    },
    "P006": {
        "concept": "conditionals_and_booleans",
        "name": "Boolean Operator Misunderstanding",
        "scenarios": [
            {
                "question": "What does this code print?\n\nx = 3\nif x == 1 or 2:\n    print('Match')\nelse:\n    print('No Match')",
                "code": "x = 3\nif x == 1 or 2:\n    print('Match')\nelse:\n    print('No Match')",
                "expected": "Match",
                "wrong_answers": [
                    ("No Match", "x is 3, which is neither 1 nor 2, so the condition x == 1 or 2 is false."),
                    ("No Match", "3 does not equal 1 or 2.")
                ],
                "correct_reasoning": "In Python, 'x == 1 or 2' is parsed as '(x == 1) or (2)'. Since 2 is a truthy non-zero integer, the expression evaluates to True regardless of x, printing 'Match'."
            },
            {
                "question": "What does this print?\n\nval = 15\nif val < 5 and val > 10:\n    print('Valid')\nelse:\n    print('Invalid')",
                "code": "val = 15\nif val < 5 and val > 10:\n    print('Valid')\nelse:\n    print('Invalid')",
                "expected": "Invalid",
                "wrong_answers": [
                    ("Valid", "val is 15 which is greater than 10, so the 'and' condition passes."),
                    ("Valid", "'and' means either condition being valid is acceptable.")
                ],
                "correct_reasoning": "'and' requires BOTH conditions to simultaneously evaluate to True. A single number cannot be both strictly less than 5 and greater than 10."
            }
        ]
    },
    "P007": {
        "concept": "functions_and_scope",
        "name": "Return vs Print Confusion",
        "scenarios": [
            {
                "question": "What does this code print?\n\ndef compute(a, b):\n    print(a + b)\n\nres = compute(3, 4)\nprint(res)",
                "code": "def compute(a, b):\n    print(a + b)\n\nres = compute(3, 4)\nprint(res)",
                "expected": "7\nNone",
                "wrong_answers": [
                    ("7\n7", "The function printed 7, which returns 7 into res, so print(res) prints 7."),
                    ("7", "res holds 7 and prints it."),
                    ("None\nNone", "print does nothing.")
                ],
                "correct_reasoning": "print() sends text to stdout but does not return a value. In Python, functions without a return statement implicitly return None, so res is None."
            },
            {
                "question": "What does this print?\n\ndef square(n):\n    return n * n\n    print('Done squaring')\n\nval = square(4)\nprint(val)",
                "code": "def square(n):\n    return n * n\n    print('Done squaring')\n\nval = square(4)\nprint(val)",
                "expected": "16",
                "wrong_answers": [
                    ("Done squaring\n16", "The function prints 'Done squaring' before handing back 16."),
                    ("16\nDone squaring", "All statements in the function body execute before returning.")
                ],
                "correct_reasoning": "return immediately terminates function execution and hands control back to the caller; code following return is unreachable."
            }
        ]
    },
    "P008": {
        "concept": "functions_and_scope",
        "name": "Parameter vs Argument Confusion",
        "scenarios": [
            {
                "question": "What is the output?\n\ndef greet(name):\n    print('Hello ' + name)\n\nuser = 'Alice'\ngreet(user)",
                "code": "def greet(name):\n    print('Hello ' + name)\n\nuser = 'Alice'\ngreet(user)",
                "expected": "Hello Alice",
                "wrong_answers": [
                    ("NameError", "Argument variable 'user' must match parameter name 'name'."),
                    ("Hello name", "Parameter literal 'name' is printed instead of 'Alice'.")
                ],
                "correct_reasoning": "Parameters are local placeholders. At call time, the argument 'user' evaluates to 'Alice' and binds to parameter 'name'."
            },
            {
                "question": "What is printed?\n\nx = 100\ndef double(val):\n    return x * 2\n\nprint(double(5))",
                "code": "x = 100\ndef double(val):\n    return x * 2\n\nprint(double(5))",
                "expected": "200",
                "wrong_answers": [
                    ("10", "double(5) multiplies the parameter 5 by 2 to get 10."),
                    ("5", "Returns 5.")
                ],
                "correct_reasoning": "The function ignores the passed parameter 'val' and instead refers to the global variable 'x' (100 * 2 = 200), demonstrating parameter omission."
            }
        ]
    },
    "P009": {
        "concept": "lists_and_indexing",
        "name": "List/Array Indexing Misunderstanding",
        "scenarios": [
            {
                "question": "What is printed?\n\nfruits = ['apple', 'banana', 'cherry']\nprint(fruits[1])",
                "code": "fruits = ['apple', 'banana', 'cherry']\nprint(fruits[1])",
                "expected": "banana",
                "wrong_answers": [
                    ("apple", "fruits[1] gets the first element in the list."),
                    ("IndexError", "Index 1 is out of range.")
                ],
                "correct_reasoning": "Python lists are zero-indexed. Index 0 is 'apple', index 1 is 'banana'."
            },
            {
                "question": "What is printed?\n\nletters = ['a', 'b', 'c', 'd', 'e']\nprint(letters[1:3])",
                "code": "letters = ['a', 'b', 'c', 'd', 'e']\nprint(letters[1:3])",
                "expected": "['b', 'c']",
                "wrong_answers": [
                    ("['b', 'c', 'd']", "Slices include indices 1, 2, and 3 (3 elements)."),
                    ("['a', 'b', 'c']", "Slices start at 1st element 'a'.")
                ],
                "correct_reasoning": "Slice [start:stop] starts at index 1 ('b') and stops before index 3 ('d'), extracting items at indices 1 and 2 ('b', 'c')."
            }
        ]
    },
    "P010": {
        "concept": "data_structures_and_state",
        "name": "Mutable State / Reference Confusion",
        "scenarios": [
            {
                "question": "What does this code print?\n\na = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)",
                "code": "a = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)",
                "expected": "[1, 2, 3, 4]",
                "wrong_answers": [
                    ("[1, 2, 3]", "b = a made an independent copy of list a, so mutating b has no effect on a."),
                    ("None", "b.append() returns None.")
                ],
                "correct_reasoning": "Assignment `b = a` creates an alias reference pointing to the same list object in memory. Appending to `b` alters `a` directly."
            },
            {
                "question": "What does this print?\n\nrow = [0, 0]\ngrid = [row] * 2\ngrid[0][0] = 9\nprint(grid)",
                "code": "row = [0, 0]\ngrid = [row] * 2\ngrid[0][0] = 9\nprint(grid)",
                "expected": "[[9, 0], [9, 0]]",
                "wrong_answers": [
                    ("[[9, 0], [0, 0]]", "Only the first row was modified because grid[0] targets index 0."),
                    ("[[0, 0], [9, 0]]", "Index modified the second row.")
                ],
                "correct_reasoning": "[row] * 2 duplicates the reference to the single 'row' object. Both elements of grid point to the same sublist."
            }
        ]
    }
}

CORRECT_SAMPLES = [
    {
        "concept": "variables",
        "question": "What is printed?\nx = 5\ny = x\nx = 10\nprint(y)",
        "code": "x = 5\ny = x\nx = 10\nprint(y)",
        "expected": "5",
        "reasoning": "y gets the value 5 from x. Modifying x afterwards does not change y because ints are immutable."
    },
    {
        "concept": "loops",
        "question": "What does this print?\ntotal = 0\nfor i in range(4):\n    total += i\nprint(total)",
        "code": "total = 0\nfor i in range(4):\n    total += i\nprint(total)",
        "expected": "6",
        "reasoning": "range(4) produces 0, 1, 2, 3. Sum is 0 + 1 + 2 + 3 = 6."
    },
    {
        "concept": "functions_and_scope",
        "question": "What does this print?\ndef add(a, b):\n    return a + b\nprint(add(2, 3))",
        "code": "def add(a, b):\n    return a + b\nprint(add(2, 3))",
        "expected": "5",
        "reasoning": "add returns 2 + 3 = 5, which print outputs."
    },
    {
        "concept": "conditionals",
        "question": "What does this print?\na = 4\nif a % 2 == 0:\n    print('even')\nelse:\n    print('odd')",
        "code": "a = 4\nif a % 2 == 0:\n    print('even')\nelse:\n    print('odd')",
        "expected": "even",
        "reasoning": "4 % 2 is 0, so the if condition evaluates to True and prints 'even'."
    },
    {
        "concept": "lists_and_indexing",
        "question": "What does this print?\nitems = [10, 20, 30]\nprint(items[0] + items[-1])",
        "code": "items = [10, 20, 30]\nprint(items[0] + items[-1])",
        "expected": "40",
        "reasoning": "items[0] is 10 and items[-1] is 30. 10 + 30 = 40."
    },
    {
        "concept": "data_structures_and_state",
        "question": "What does this print?\norig = [1, 2]\nclone = orig.copy()\nclone.append(3)\nprint(len(orig))",
        "code": "orig = [1, 2]\nclone = orig.copy()\nclone.append(3)\nprint(len(orig))",
        "expected": "2",
        "reasoning": "clone is a distinct shallow copy of orig, so appending to clone does not alter orig."
    }
]

DIFFICULT_CONTRAST_CASES = [
    # Same answer (e.g. 5) but different misconceptions: P003 vs P004
    {
        "question": "What is the final value of x?\nx = 0\nwhile x < 5:\n    x += 1",
        "code": "x = 0\nwhile x < 5:\n    x += 1",
        "expected": "5",
        "variations": [
            ("P003", "4", "Loop stops one early because loop boundary exclusive bound means it only reaches 4.", "Loop boundary off-by-one"),
            ("P004", "4", "As soon as x reaches 4 + 1 inside body it halts immediately before doing increment check.", "Mid-body exit misconception")
        ]
    },
    # Same answer (NameError) but P002 (scope) vs P008 (parameter mismatch)
    {
        "question": "Why does calling calculate() fail?\ndef calculate():\n    return factor * 2\ncalculate()",
        "code": "def calculate():\n    return factor * 2\ncalculate()",
        "expected": "NameError",
        "variations": [
            ("P002", "NameError", "factor was assumed to be global or inherited from somewhere in the call stack.", "Scope confusion"),
            ("P008", "NameError", "factor was supposed to be passed as an argument but was forgotten in function definition parameters.", "Parameter confusion")
        ]
    }
]

def generate_dataset(total_target: int = 1200) -> List[Dict[str, Any]]:
    dataset = []
    sample_id = 1

    # 1. Generate Incorrect Known Misconceptions (Balanced across P001-P010)
    samples_per_p = total_target // 15
    for p_id, p_info in MISCONCEPTION_TEMPLATES.items():
        scenarios = p_info["scenarios"]
        for i in range(samples_per_p):
            scenario = random.choice(scenarios)
            wrong_ans, reasoning = random.choice(scenario["wrong_answers"])
            
            # Subtle variation in reasoning noise
            noise_prefixes = [
                "",
                "I believe that ",
                "In my understanding, ",
                "Clearly, ",
                "According to rules, "
            ]
            custom_reasoning = random.choice(noise_prefixes) + reasoning

            record = {
                "id": f"EX{sample_id:04d}",
                "question": {
                    "id": f"Q_{p_id}_{i%len(scenarios)+1}",
                    "text": scenario["question"],
                    "concept": p_info["concept"],
                    "code_snippet": scenario["code"]
                },
                "learner_response": {
                    "type": "code_and_reasoning",
                    "answer": wrong_ans,
                    "reasoning": custom_reasoning,
                    "code": scenario["code"]
                },
                "expected_answer": scenario["expected"],
                "correct": False,
                "misconception": {
                    "primary": p_id,
                    "alternatives": [alt for alt in ["P001", "P003", "P004", "P005", "P010"] if alt != p_id][:2],
                    "is_ambiguous": False
                },
                "evidence": [
                    f"Learner predicted '{wrong_ans}' instead of '{scenario['expected']}'",
                    f"Reasoning indicates {p_info['name']}",
                    f"Diagnostic pattern matched for {p_id}"
                ],
                "expert_reasoning": f"Learner demonstrates {p_info['name']} ({p_id}). {scenario['correct_reasoning']}",
                "difficulty": random.choice(["beginner", "beginner", "intermediate"]),
                "sample_category": "incorrect_known_misconception",
                "split_metadata": {
                    "concept": p_info["concept"],
                    "template_group": f"template_{p_id}_{i%len(scenarios)}"
                }
            }
            dataset.append(record)
            sample_id += 1

    # 2. Difficult Contrast Cases (Same answer, different misconception)
    for contrast in DIFFICULT_CONTRAST_CASES:
        for p_id, ans, reasoning, title in contrast["variations"]:
            for rep in range(25):
                record = {
                    "id": f"EX{sample_id:04d}",
                    "question": {
                        "id": f"Q_CONTRAST_{p_id}_{rep%3}",
                        "text": contrast["question"],
                        "concept": MISCONCEPTION_TEMPLATES[p_id]["concept"],
                        "code_snippet": contrast["code"]
                    },
                    "learner_response": {
                        "type": "code_and_reasoning",
                        "answer": ans,
                        "reasoning": f"{reasoning} (Attempt variation {rep+1})",
                        "code": contrast["code"]
                    },
                    "expected_answer": contrast["expected"],
                    "correct": False,
                    "misconception": {
                        "primary": p_id,
                        "alternatives": [p for p in ["P003", "P004", "P002", "P008"] if p != p_id],
                        "is_ambiguous": False
                    },
                    "evidence": [
                        f"Contrast problem testing same surface answer '{ans}'",
                        f"Reasoning distinguishes {p_id} from competitor"
                    ],
                    "expert_reasoning": f"Contrast benchmark sample: Learner produces answer '{ans}' driven specifically by {title}.",
                    "difficulty": "intermediate",
                    "sample_category": "difficult_contrast_same_answer",
                    "split_metadata": {
                        "concept": MISCONCEPTION_TEMPLATES[p_id]["concept"],
                        "template_group": f"contrast_{p_id}"
                    }
                }
                dataset.append(record)
                sample_id += 1

    # 3. Partial Understanding (Correct Answer, Faulty Reasoning)
    for p_id in ["P003", "P005", "P006"]:
        for rep in range(30):
            p_info = MISCONCEPTION_TEMPLATES[p_id]
            scenario = p_info["scenarios"][0]
            record = {
                "id": f"EX{sample_id:04d}",
                "question": {
                    "id": f"Q_PARTIAL_{p_id}_{rep}",
                    "text": scenario["question"],
                    "concept": p_info["concept"],
                    "code_snippet": scenario["code"]
                },
                "learner_response": {
                    "type": "code_and_reasoning",
                    "answer": scenario["expected"], # Correct answer!
                    "reasoning": f"I guessed {scenario['expected']} by lucky coincidence, but I actually thought {p_info['name']} applied here.",
                    "code": scenario["code"]
                },
                "expected_answer": scenario["expected"],
                "correct": True,
                "misconception": {
                    "primary": p_id,
                    "alternatives": [],
                    "is_ambiguous": False
                },
                "evidence": [
                    f"Answer was correct ('{scenario['expected']}') but reasoning exhibits misconception {p_id}",
                    "Partial understanding with compensatory guessing or lucky error cancellation"
                ],
                "expert_reasoning": f"Learner obtained the correct surface output through flawed mental model ({p_id}).",
                "difficulty": "intermediate",
                "sample_category": "partial_understanding",
                "split_metadata": {
                    "concept": p_info["concept"],
                    "template_group": f"partial_{p_id}"
                }
            }
            dataset.append(record)
            sample_id += 1

    # 4. Ambiguous / Insufficient Evidence Cases
    for rep in range(60):
        target_p = random.choice(list(MISCONCEPTION_TEMPLATES.keys()))
        p_info = MISCONCEPTION_TEMPLATES[target_p]
        scenario = random.choice(p_info["scenarios"])
        record = {
            "id": f"EX{sample_id:04d}",
            "question": {
                "id": f"Q_AMBIG_{rep}",
                "text": scenario["question"],
                "concept": p_info["concept"],
                "code_snippet": scenario["code"]
            },
            "learner_response": {
                "type": "code_and_reasoning",
                "answer": "idk maybe wrong",
                "reasoning": "not sure why but it broke",
                "code": scenario["code"]
            },
            "expected_answer": scenario["expected"],
            "correct": False,
            "misconception": {
                "primary": "INSUFFICIENT_EVIDENCE",
                "alternatives": [target_p],
                "is_ambiguous": True
            },
            "evidence": [
                "No substantive technical reasoning provided",
                "Ambiguous response string"
            ],
            "expert_reasoning": "System should identify insufficient evidence rather than hallucinating a specific misconception.",
            "difficulty": "beginner",
            "sample_category": "ambiguous_insufficient_evidence",
            "split_metadata": {
                "concept": p_info["concept"],
                "template_group": "ambiguous"
            }
        }
        dataset.append(record)
        sample_id += 1

    # 5. Correct Answers (Class: CORRECT)
    for i in range(250):
        sample = random.choice(CORRECT_SAMPLES)
        record = {
            "id": f"EX{sample_id:04d}",
            "question": {
                "id": f"Q_CORRECT_{i%len(CORRECT_SAMPLES)}",
                "text": sample["question"],
                "concept": sample["concept"],
                "code_snippet": sample["code"]
            },
            "learner_response": {
                "type": "code_and_reasoning",
                "answer": sample["expected"],
                "reasoning": sample["reasoning"],
                "code": sample["code"]
            },
            "expected_answer": sample["expected"],
            "correct": True,
            "misconception": {
                "primary": "CORRECT",
                "alternatives": [],
                "is_ambiguous": False
            },
            "evidence": [
                "Answer matches expected output",
                "Sound causal code reasoning demonstrated"
            ],
            "expert_reasoning": "Student demonstrates solid mastery of the concept without misconceptions.",
            "difficulty": "beginner",
            "sample_category": "correct",
            "split_metadata": {
                "concept": sample["concept"],
                "template_group": f"correct_{i%len(CORRECT_SAMPLES)}"
            }
        }
        dataset.append(record)
        sample_id += 1

    random.shuffle(dataset)
    return dataset

if __name__ == "__main__":
    os.makedirs("ml/data/raw", exist_ok=True)
    os.makedirs("ml/data/processed", exist_ok=True)

    data = generate_dataset(total_target=1250)
    raw_path = "ml/data/raw/dataset.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {len(data)} dataset examples into {raw_path}")
