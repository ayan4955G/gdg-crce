# Re:Learn — Architecture & System Design Document

## 1. Executive Summary & Audit Context
Re:Learn is an AI-powered, cognitive-diagnostic adaptive learning system for introductory programming. Unlike traditional educational applications that query a large language model with a naive "explain what is wrong with this code" prompt, Re:Learn separates the educational and reasoning pipeline into independent, auditable components:
1. **Multi-Source Evidence Extraction**: Static AST parsing, runtime execution trace & error analysis, lexical code features, and natural language student reasoning.
2. **Diagnostic Misconception Classifier**: Distinguishes between subtle, confusable student mental models (e.g., distinguishing assignment vs equality, off-by-one loop boundary vs loop condition misunderstanding, return vs print).
3. **Targeted Pedagogical Intervention Engine**: Multi-tiered scaffolding (hints, guided reasoning, counterexamples, interactive code tracing, worked examples) with strict validation to prevent answer leakage.
4. **Independent Resolution Assessment**: Re-evaluates student understanding using structurally novel and transfer questions to verify authentic conceptual remediation rather than surface-level memorization.
5. **Learner Knowledge State & Profile**: Maintains ongoing probabilistic mastery estimations and misconception recurrence tracking across programming concepts.

---

## 2. System Architecture

```
                       ┌──────────────────────────────────────────────┐
                       │        Modern Frontend (React + Vite)        │
                       │  - Learning Flow (Question / Code / Trace)   │
                       │  - Student Mastery & Misconception Profile   │
                       │  - Research / Evaluation / Ablation Studio   │
                       └──────────────────────┬───────────────────────┘
                                              │ HTTP / JSON API
                                              ▼
                       ┌──────────────────────────────────────────────┐
                       │           FastAPI Application Backend        │
                       │  - Auth & Learner Session Management         │
                       │  - Question & Concept Catalog Services       │
                       │  - Resolution Assessment Engine              │
                       │  - Learner Profile & Mastery Aggregator      │
                       └──────────────┬───────────────────────────────┘
                                      │
               ┌──────────────────────┼───────────────────────┐
               ▼                      ▼                       ▼
     ┌──────────────────┐   ┌──────────────────┐    ┌──────────────────┐
     │  SQLite / PG DB  │   │ Code Execution   │    │  ML & Diagnosis  │
     │  - Relational    │   │ Sandbox Service  │    │  Inference Core  │
     │    Data, Models, │   │ - AST Parsing    │    │ - Feature Fusion │
     │    Predictions   │   │ - Safe Runner    │    │ - Classifiers    │
     └──────────────────┘   │ - Timeout/Limits │    │ - Interventions  │
                            └──────────────────┘    └──────────────────┘
```

---

## 3. Component Boundaries & Core Principles

### Principle 1: Independent Resolution Assessment
The intervention generator **must never** assess its own efficacy. The diagnostic model diagnoses the initial response; the intervention engine dispenses pedagogical scaffolding; then, a completely separate battery of transfer assessments and an independent resolution classifier evaluate whether the misconception is actually resolved.

### Principle 2: Safe Code Sandbox
Learner code is parsed using Python's native `ast` module before execution. Execution is confined in isolated runner processes with strict memory limits, execution timeouts (maximum 2 seconds), and restricted global namespaces preventing network, disk, and system manipulation.

### Principle 3: Hybrid Diagnostic Engine
Combines:
- Symbolic AST patterns (e.g. comparing loop bounds against `len(arr)` vs `len(arr) - 1`)
- Dynamic runtime indicators (e.g. `IndexError`, incorrect accumulator values)
- NLP & lexical token analysis (TF-IDF + embeddings of learner explanation)
- Evidential fusion that produces calibrated probabilities across candidate misconceptions or flags `AMBIGUOUS` / `INSUFFICIENT_EVIDENCE`.

---

## 4. API Endpoints Specification

### Diagnostic & Learning
- `POST /api/v1/diagnose`: Accepts `{question_id, response, code, previous_attempts}`, runs AST/Execution/NLP evidence extraction, returns primary diagnosis, confidence, alternative candidates, and extracted evidence.
- `POST /api/v1/intervention`: Accepts `{misconception_id, learner_response, learner_history}`, returns scaffolding type, prompt/trace exercise, and validation flags.
- `POST /api/v1/assess-resolution`: Accepts `{misconception_id, attempts}`, evaluates performance across isomorphic and transfer questions, returning `LIKELY_RESOLVED`, `IMPROVING`, or `UNRESOLVED`.

### Content & Learner Models
- `GET /api/v1/questions`: Fetch curated questions mapped to concepts.
- `GET /api/v1/questions/{id}`: Detailed question prompt, test cases, and expected reasoning.
- `GET /api/v1/learner/{id}/profile`: Current concept mastery, active misconceptions, resolution history.
- `GET /api/v1/evaluation/metrics`: Research metrics, confusion matrices, ablation comparisons, and unseen-question generalization benchmarks.

---

## 5. Directory Structure
```text
relearn/
├── docs/
│   ├── architecture.md
│   ├── taxonomy.md
│   ├── dataset.md
│   ├── evaluation.md
│   └── api.md
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
├── ml/
│   ├── taxonomy/
│   │   └── misconceptions.json
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   ├── train/
│   │   ├── validation/
│   │   └── test/
│   ├── evidence/
│   │   ├── ast_analyzer.py
│   │   ├── code_features.py
│   │   ├── execution_analyzer.py
│   │   ├── text_features.py
│   │   └── evidence_fusion.py
│   ├── models/
│   │   ├── baseline_tfidf.py
│   │   ├── baseline_embedding.py
│   │   ├── hybrid_diagnoser.py
│   │   ├── intervention_engine.py
│   │   └── resolution_model.py
│   ├── evaluation/
│   │   ├── evaluate.py
│   │   ├── ablation_study.py
│   │   └── llm_comparison.py
│   └── scripts/
│       ├── generate_dataset.py
│       ├── validate_dataset.py
│       ├── balance_dataset.py
│       └── split_dataset.py
├── sandbox/
│   └── code_runner.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── tests/
│   ├── test_ast_analyzer.py
│   ├── test_diagnosis.py
│   ├── test_intervention.py
│   ├── test_resolution.py
│   ├── test_api.py
│   └── test_end_to_end.py
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```
