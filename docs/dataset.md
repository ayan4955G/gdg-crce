# Re:Learn — Dataset Specification & Protocol

## 1. Schema Definition
Each labelled learner interaction record follows this JSON specification:

```json
{
  "id": "EX001",
  "question": {
    "id": "Q001",
    "text": "What is the output of this code?\n\nfor i in range(1, 5):\n    print(i, end=' ')",
    "concept": "loops",
    "code_snippet": "for i in range(1, 5):\n    print(i, end=' ')"
  },
  "learner_response": {
    "type": "code_and_reasoning",
    "answer": "1 2 3 4 5",
    "reasoning": "range(1, 5) starts at 1 and goes up to and includes 5, so it prints numbers 1 through 5.",
    "code": "for i in range(1, 5):\n    print(i, end=' ')"
  },
  "expected_answer": "1 2 3 4",
  "correct": false,
  "misconception": {
    "primary": "P003",
    "alternatives": ["P004"],
    "is_ambiguous": false
  },
  "evidence": [
    "Learner expects 5 iterations including endpoint 5",
    "Verbalized rule: 'goes up to and includes 5'",
    "AST indicates range(1, 5) without -1 or adjustment",
    "Mismatch between exclusive stop parameter and inclusive mental model"
  ],
  "expert_reasoning": "Learner exhibits classic loop boundary off-by-one confusion (P003). They assume Python range(start, stop) behaves like an inclusive interval [1, 5] rather than half-open [1, 5).",
  "difficulty": "beginner",
  "sample_category": "incorrect_known_misconception", 
  "split_metadata": {
    "question_family": "range_boundary",
    "syntax_form": "for_loop"
  }
}
```

## 2. Dataset Distribution & Balancing Strategy
To ensure the ML diagnostic core does not learn superficial shortcuts or trivial correlations, the dataset explicitly balances six essential cognitive categories:
1. **Correct**: Correct answer with sound reasoning (Class `CORRECT`).
2. **Incorrect Known Misconception**: Erroneous answer directly expressing one of `P001` - `P010`.
3. **Difficult Contrast A (Same Answer, Different Misconceptions)**: Identical surface output produced by two distinct underlying mental models.
4. **Difficult Contrast B (Same Misconception, Different Answers)**: Single underlying bug manifesting in different observed answers depending on variable names or initial states.
5. **Partial Understanding (Correct Answer, Faulty Reasoning)**: Right answer achieved through compensatory misconceptions or accidental cancellation of errors.
6. **Ambiguous / Insufficient Evidence**: Underspecified response where multiple misconceptions are equally probable or evidence is missing.

## 3. Train / Validation / Test Splitting Policy
Random row splitting leads to severe data leakage because models memorize question text. Re:Learn uses **Concept & Family Stratification**:
- Questions are grouped into semantic families.
- **Unseen Question Evaluation Set**: Holds out entire question templates (e.g. while-loop equivalents of for-loop problems) exclusively for test evaluation to measure genuine transfer learning.
