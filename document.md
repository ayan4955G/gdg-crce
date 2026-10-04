# Re:Learn Machine Learning & Cognitive Diagnostic Engine

This document provides a comprehensive technical guide to how the Machine Learning and Cognitive Diagnostic pipeline works in **Re:Learn** (`BNB_castors`), including component architectures, data flow, mathematical updates, and a step-by-step concrete example.

---

## 1. System Overview & Objective

Traditional programming tutors only check whether code passes unit tests or matches an expected string output. They fail to identify **why** a student made a mistake.

**Re:Learn** treats learning as a **cognitive diagnostic process**:
1. It analyzes student answers, verbal reasoning, code, and sandbox execution.
2. It pinpoints the exact **underlying conceptual misconception** (from a curated taxonomy `P001`–`P010`).
3. It generates **hierarchical pedagogical scaffolding** (hints, counterexamples, memory traces) without giving away the direct answer.
4. It independently tests understanding on **isomorphic and transfer problems** to verify true resolution before updating the student's Bayesian cognitive profile.

---

## 2. Core ML & Cognitive Architecture

```
                                  +---------------------------------------+
                                  |            Student Submission         |
                                  | (Code + Natural Language + Selection) |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                   +---------------------------------------------------------------------+
                   |                      Evidence Fusion Engine                         |
                   |                                                                     |
                   |   +-------------------+   +-----------------+   +---------------+   |
                   |   | Code AST Analyzer |   | Sandbox Runner  |   | Text Cues &   |   |
                   |   | (Static Structure)|   | (Exec & Output) |   | Verbalization |   |
                   |   +---------+---------+   +--------+--------+   +-------+-------+   |
                   +-------------|----------------------|--------------------|-----------+
                                 |                      |                    |
                                 +----------------------+--------------------+
                                                        |
                                                        v
                                  +---------------------------------------+
                                  |      Hybrid Misconception Diagnoser   |
                                  |    (NVIDIA Nemotron NIM / Classifier) |
                                  +---------------------+-----------------+
                                                        |
                                                        v
                                  +---------------------------------------+
                                  |           Diagnosis Result            |
                                  |   (Misconception ID, Confidence, Ev.) |
                                  +---------------------+-----------------+
                                                        |
                                                        v
                                  +---------------------------------------+
                                  |         Intervention Engine           |
                                  |     (6-tier Pedagogical Scaffolding)  |
                                  +---------------------+-----------------+
                                                        |
                                                        v
                                  +---------------------------------------+
                                  |   Independent Resolution Assessor     |
                                  | (Isomorphic + Transfer Re-evaluation) |
                                  +---------------------+-----------------+
                                                        |
                                                        v
                                  +---------------------------------------+
                                  |       Learner Cognitive Model         |
                                  |      (Bayesian Mastery Tracking)      |
                                  +---------------------------------------+
```

---

## 3. Component Deep Dive

### 3.1 Deterministic Evidence Engine (`ml/evidence/`)
- **[CodeASTAnalyzer](file:///e:/BNB_castors/ml/evidence/ast_analyzer.py)**: Parses the Python Abstract Syntax Tree to identify symbolic patterns (e.g., `range(a, b)` calls, assignment statements, chained comparisons).
- **[ExecutionAnalyzer](file:///e:/BNB_castors/ml/evidence/execution_analyzer.py) & [SandboxedCodeRunner](file:///e:/BNB_castors/sandbox/code_runner.py)**: Safely executes student code inside an isolated subprocess with strict timeouts to capture actual stdout, runtime exceptions (e.g. `IndexError`), and return states.
- **[TextFeatureExtractor](file:///e:/BNB_castors/ml/evidence/text_features.py)**: Extracts verbal cues, linguistic keywords, and misconception markers from the student's written reasoning.
- **[EvidenceFusionEngine](file:///e:/BNB_castors/ml/evidence/evidence_fusion.py)**: Combines AST facts, runtime output, text cues, and answer correctness into a unified evidence payload.

---

### 3.2 Hybrid Misconception Diagnoser (`ml/models/hybrid_diagnoser.py`)
- Coordinates diagnosis by passing fused deterministic evidence alongside the problem prompt and student answers to **[NvidiaNemotron](file:///e:/BNB_castors/ml/models/nvidia_nemotron.py)** (`nvidia/nemotron-3.5-lightning-30b-a3b`).
- Enforces strict structured JSON schema output (`status`, `primary_id`, `confidence`, `summary`, `evidence`).
- Categorizes submissions into `CORRECT`, `DIAGNOSED` (identifying misconception `P001` through `P010`), `INSUFFICIENT_EVIDENCE`, or `UNKNOWN`.

#### Misconception Taxonomy Sample:
- **`P001`**: Assignment Direction Misunderstanding (`a = b` vs `b = a`)
- **`P002`**: Local Variable / Scope Leaks
- **`P003`**: Loop Upper Boundary Off-by-One (`range(start, stop)` inclusive vs exclusive)
- **`P004`**: While-Loop Condition Continuous Checking Illusion
- **`P005`**: Fallthrough Misconception in Independent `if` statements
- **`P006`**: Boolean Expression Misparsing (`x == 1 or 2`)
- **`P007`**: Print vs Return Equivalence
- **`P009`**: 1-based Indexing Assumption in Sequences
- **`P010`**: Object Aliasing vs Value Copying

---

### 3.3 Pedagogical Intervention Engine (`ml/models/intervention_engine.py`)
Generates calibrated interventions using a 6-tier scaffolding hierarchy:
1. **`hint`**: Nudges attention to key concepts without spoiling.
2. **`guided_reasoning`**: Socratic questions prompting reflection.
3. **`counterexample`**: Real-world analogies or code examples demonstrating the flaw.
4. **`code_trace`**: Step-by-step state and memory breakdown.
5. **`concept_explanation`**: Formal conceptual principle.
6. **`worked_example`**: Parallel solved problem.

The engine includes validation filters to prevent leaking exact answer strings to the student.

---

### 3.4 Independent Resolution Assessor (`ml/models/resolution_model.py`)
- Decoupled from intervention generation to eliminate bias.
- Evaluates student follow-up responses across 3 tiers:
  - **Isomorphic Problems**: Identical structure, different surface numbers.
  - **Different Surface Problems**: Alternate scenario testing the same principle.
  - **Transfer Problems**: Structurally novel problem requiring generalized understanding (e.g. testing loop bounds on a `while` loop instead of a `for range`).
- Outputs resolution state: `LIKELY_RESOLVED` (confidence ~0.92), `IMPROVING` (confidence ~0.76), or `UNRESOLVED` (confidence ~0.88).

---

### 3.5 Bayesian Learner Cognitive Model (`ml/models/learner_model.py`)
Maintains a dynamic probabilistic state for each student across fundamental topics:
- **Bayesian Update Formula**:
  - **On Success**:
    $$\text{Mastery}_{t+1} = \min(0.98, \text{Mastery}_t + 0.12 \times (1.0 - \text{Mastery}_t))$$
  - **On Failure**:
    $$\text{Mastery}_{t+1} = \max(0.05, \text{Mastery}_t - 0.15 \times \text{Mastery}_t)$$
- **Confidence Growth**:
  $$\text{Confidence} = \min(0.95, 0.40 + 0.08 \times \ln(\text{Attempts} + 1))$$

---

## 4. End-to-End Walkthrough with a Concrete Example

Let us trace a student attempting a Python loop question.

### Step 1: Student Submission
- **Question**: "What does the following code print? `for i in range(1, 5): print(i, end=' ')`"
- **Expected Answer**: `"1 2 3 4"`
- **Student Answer**: `"1 2 3 4 5"`
- **Student Verbal Reasoning**: *"range(1, 5) starts at 1 and stops at 5 inclusive, so it prints 1 through 5."*
- **Student Code**:
  ```python
  for i in range(1, 5):
      print(i, end=' ')
  ```

---

### Step 2: Evidence Extraction & Fusion
The **EvidenceFusionEngine** runs three parallel extractions:

1. **AST Extraction**:
   - Matches pattern `ast_range_call`.
   - Identifies 2-argument `range(1, 5)`.
2. **Sandbox Execution**:
   - Executes snippet safely.
   - Stdout captured: `"1 2 3 4 "`
   - Mismatch detected between student answer (`"1 2 3 4 5"`) and actual execution output (`"1 2 3 4"`).
3. **Text Feature Extraction**:
   - Scans student reasoning for lexical cues.
   - Matches cue: `['stops at 5 inclusive', 'inclusive']` tagged to `P003`.

**Fused Evidence Payload**:
```json
{
  "evidence_list": [
    "AST Pattern (ast_range_call): Detected range(1, 5) invocation",
    "Runtime Symptom (mismatch): Code printed '1 2 3 4 ' but student predicted '1 2 3 4 5'",
    "Reasoning Cue for P003: Found expressions ['inclusive', 'stops at 5']"
  ],
  "is_answer_correct": false
}
```

---

### Step 3: Hybrid Diagnosis
The fused payload is passed to the diagnostic engine.

**Diagnosis Output (`/api/diagnose`)**:
```json
{
  "status": "DIAGNOSED",
  "primary": {
    "id": "P003",
    "name": "Loop Upper Boundary Off-by-One",
    "confidence": 0.94
  },
  "alternatives": [],
  "evidence": [
    "AST Pattern (ast_range_call): Detected range(1, 5) invocation",
    "Runtime Symptom: Output mismatch between prediction and sandbox runtime",
    "Reasoning Cue: Learner stated range is inclusive of stop argument"
  ],
  "expert_reasoning": "Student believes range(1, 5) includes upper bound 5."
}
```

---

### Step 4: Pedagogical Intervention
The system calls the **InterventionEngine** requesting the first tier (`hint`):

**Intervention Response (`/api/intervene`)**:
```json
{
  "type": "hint",
  "content": "In Python, range(start, stop) generates integers starting at 'start' and stopping strictly BEFORE 'stop' (half-open interval [start, stop)).",
  "target_misconception": "P003",
  "follow_up_question": "If you want a loop to execute with values 1, 2, 3, 4, 5, what stop value must you pass to range(1, ?)?",
  "is_validated": true
}
```

If the student still struggles, the engine escalates to higher tiers:
- **`guided_reasoning`**: *"How many values are between 1 and 5 if 5 is excluded? Write out the numbers one by one starting from 1."*
- **`code_trace`**: *"Step 4: i = 4, prints 4. Next value would be 5, but range stop is 5 (exclusive) -> loop ends."*

---

### Step 5: Transfer Assessment & Resolution
The student is given two follow-up validation problems:

1. **Isomorphic Problem**:
   - Question: *"What does `range(2, 6)` print?"*
   - Student Answer: `"2 3 4 5"` (Correct)
2. **Transfer Problem**:
   - Question: *"How many times does this loop body execute? `i = 0; while i < 5: i += 1`"*
   - Student Answer: `"5"` (Correct, demonstrating understanding of boundary termination in loops)

**Independent Resolution Assessment Output (`/api/resolve`)**:
```json
{
  "status": "LIKELY_RESOLVED",
  "confidence": 0.92,
  "evidence": {
    "similar_problem": true,
    "different_problem": false,
    "transfer_problem": true,
    "misconception_still_detected": false,
    "attempts_evaluated": 2
  },
  "summary": "Student solved transfer and isomorphic problems. Conceptual misconception P003 is successfully remediated."
}
```

---

### Step 6: Cognitive Profile Update
The **LearnerCognitiveModel** updates the student's mastery profile:

- **Before resolution**:
  - `loops.mastery`: `0.35`
  - `misconceptions.P003.resolved`: `false`
- **After successful resolution**:
  - `loops.mastery` increases: `0.35 + 0.12 * (1.0 - 0.35) = 0.428`
  - `loops.confidence` increases with attempt count
  - `misconceptions.P003.resolved`: `true`
  - `misconceptions.P003.resolution_confidence`: `0.92`

---

## 5. Summary of Key Files

| File | Purpose |
|---|---|
| [ml/models/hybrid_diagnoser.py](file:///e:/BNB_castors/ml/models/hybrid_diagnoser.py) | Main diagnostic coordinator combining Nemotron + deterministic fusion |
| [ml/models/nvidia_nemotron.py](file:///e:/BNB_castors/ml/models/nvidia_nemotron.py) | NVIDIA NIM LLM client with structured response parsing |
| [ml/evidence/evidence_fusion.py](file:///e:/BNB_castors/ml/evidence/evidence_fusion.py) | Multimodal evidence extractor (AST + Sandbox + Text) |
| [ml/models/intervention_engine.py](file:///e:/BNB_castors/ml/models/intervention_engine.py) | 6-tier scaffolding engine with answer leakage guardrails |
| [ml/models/resolution_model.py](file:///e:/BNB_castors/ml/models/resolution_model.py) | Independent assessor testing isomorphic & transfer generalization |
| [ml/models/learner_model.py](file:///e:/BNB_castors/ml/models/learner_model.py) | Bayesian Knowledge Tracing and cognitive profile tracker |
| [backend/app/main.py](file:///e:/BNB_castors/backend/app/main.py) | FastAPI endpoints exposing diagnosis, intervention, and resolution |
