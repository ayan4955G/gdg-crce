# Re:Learn — API Reference

## Base URL
```
http://localhost:8000/api/v1
```

---

## Diagnostic Engine

### POST `/diagnose`
Accepts question context, learner code, natural language reasoning, and optional history. Returns calibrated multi-source misconception diagnosis.

**Request Body:**
```json
{
  "question_id": "Q_P003_01",
  "question": "What does for i in range(1, 5) print?",
  "response": "1 2 3 4 5",
  "reasoning": "range(1, 5) includes 5",
  "code": "for i in range(1, 5):\n    print(i, end=' ')",
  "expected_answer": "1 2 3 4",
  "previous_attempts": []
}
```

**Response:**
```json
{
  "status": "DIAGNOSED",
  "primary": { "id": "P003", "confidence": 0.91 },
  "alternatives": [{ "id": "P004", "confidence": 0.06 }],
  "evidence": ["AST Pattern: range boundary", "Reasoning Cue: inclusive"],
  "model_version": "relearn-hybrid-v1.0",
  "expert_reasoning": "Multi-source evidence converges on P003."
}
```

**Possible `status` values:** `CORRECT`, `DIAGNOSED`, `AMBIGUOUS`, `UNKNOWN`, `INSUFFICIENT_EVIDENCE`

---

## Intervention Engine

### POST `/intervention`
Generates targeted pedagogical scaffolding with leakage validation.

**Request Body:**
```json
{
  "misconception_id": "P003",
  "learner_response": "1 2 3 4 5",
  "previous_interventions": []
}
```

**Response:**
```json
{
  "type": "hint",
  "content": "In Python, range(start, stop) stops strictly BEFORE stop...",
  "target_misconception": "P003",
  "follow_up_question": "What stop value gives 1, 2, 3, 4, 5?",
  "is_validated": true,
  "validation_notes": "Passed answer leakage and pedagogical safety validations."
}
```

**Scaffolding hierarchy:** `hint` -> `guided_reasoning` -> `counterexample` -> `code_trace` -> `concept_explanation` -> `worked_example`

---

## Resolution Assessment

### POST `/assess-resolution`
Independent evaluation using isomorphic and transfer questions.

**Request Body:**
```json
{
  "misconception_id": "P003",
  "attempts": [
    {
      "question_type": "isomorphic",
      "question_text": "What does range(2, 6) produce?",
      "student_answer": "2 3 4 5",
      "expected_answer": "2 3 4 5",
      "reasoning": "stops before 6",
      "code": "for i in range(2, 6): print(i)"
    },
    {
      "question_type": "transfer",
      "question_text": "How many iterations for while i < 5?",
      "student_answer": "5",
      "expected_answer": "5",
      "reasoning": "0,1,2,3,4 = 5 runs",
      "code": "i=0\nwhile i<5: i+=1"
    }
  ]
}
```

**Response:**
```json
{
  "status": "LIKELY_RESOLVED",
  "confidence": 0.92,
  "evidence": { "similar_problem": true, "transfer_problem": true },
  "summary": "Misconception P003 successfully remediated."
}
```

**Possible `status` values:** `UNRESOLVED`, `IMPROVING`, `LIKELY_RESOLVED`, `INSUFFICIENT_EVIDENCE`

---

## Questions

### GET `/questions`
Returns all curated programming questions. Optional `?concept=loops` filter.

### GET `/questions/{question_id}`
Returns a single question by ID.

---

## Learner Profile

### GET `/learner/{learner_id}/profile`
Returns calibrated concept mastery and misconception history.

### GET `/learner/{learner_id}/misconceptions`
Returns active and resolved misconception records.

### GET `/learner/{learner_id}/mastery`
Returns per-concept mastery scores.

### POST `/learner/{learner_id}/record-interaction`
Records a learning interaction. Query params: `question_id`, `concept`, `is_correct`, `misconception_id`.

---

## Research & Evaluation

### GET `/evaluation/metrics`
Returns baseline comparison benchmark results.

### GET `/evaluation/ablation`
Returns ablation study (Text Only -> Full Hybrid) results.

### GET `/evaluation/llm-comparison`
Returns Re:Learn vs generic LLM prompt comparison.

### GET `/evaluation/simulation-traces`
Returns end-to-end multi-learner lifecycle simulation traces.

### GET `/taxonomy`
Returns the full misconception taxonomy (P001-P010).
