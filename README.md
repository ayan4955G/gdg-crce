# Re:Learn — AI-Powered Adaptive Misconception Remediation

> An intelligent cognitive-diagnostic learning system for introductory programming that identifies, scaffolds, and independently verifies resolution of student misconceptions.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (optional)

### 1. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Dataset & Train Models
```bash
python ml/scripts/generate_dataset.py
python ml/scripts/validate_dataset.py
python ml/scripts/split_dataset.py
python ml/scripts/dataset_statistics.py
```

### 3. Run Evaluations
```bash
python ml/evaluation/evaluate.py
python ml/evaluation/ablation_study.py
python ml/evaluation/llm_comparison.py
python ml/evaluation/end_to_end_simulation.py
```

### 4. Start Backend API
```bash
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start Frontend
```bash
cd frontend && npm install && npm run dev
```

### 6. Docker Deployment
```bash
docker-compose up --build
```

---

## Architecture

```
                    Frontend (React + Vite)
                           |
                    FastAPI Backend (/api/v1/*)
                     /        |        \
              Hybrid       Intervention   Resolution
              Diagnoser    Engine         Assessor
                |                            |
        Evidence Fusion              Independent Re-diagnosis
        /    |    |    \
    AST   Exec  Text   Code
    Parse  Sand  NLP    Features
              box
```

**Core Principle**: Diagnosis, Intervention, and Resolution Assessment are fully independent components. The resolution assessor never trusts the intervention engine's self-assessment.

## Key APIs

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/diagnose` | POST | Multi-source misconception diagnosis |
| `/api/v1/intervention` | POST | Targeted pedagogical scaffolding |
| `/api/v1/assess-resolution` | POST | Independent transfer-based resolution |
| `/api/v1/questions` | GET | Curated question catalog |
| `/api/v1/learner/{id}/profile` | GET | Cognitive mastery state |
| `/api/v1/evaluation/metrics` | GET | Research benchmark metrics |
| `/api/v1/evaluation/ablation` | GET | Ablation study results |

## Misconception Taxonomy (P001–P010)

| ID | Name | Concept |
|---|---|---|
| P001 | Variable Assignment Confusion | variables |
| P002 | Variable Scope Confusion | functions_and_scope |
| P003 | Loop Boundary / Off-by-One | loops |
| P004 | Loop Condition Misunderstanding | loops |
| P005 | Conditional Logic Misunderstanding | conditionals |
| P006 | Boolean Operator Misunderstanding | conditionals_and_booleans |
| P007 | Return vs Print Confusion | functions_and_scope |
| P008 | Parameter vs Argument Confusion | functions_and_scope |
| P009 | List/Array Indexing Misunderstanding | lists_and_indexing |
| P010 | Mutable State / Reference Confusion | data_structures_and_state |

## Testing
```bash
python -m unittest discover tests
```

## Documentation
See [docs/](docs/) for architecture, dataset, taxonomy, evaluation, and API documentation.
# NVIDIA Nemotron diagnosis

The diagnosis endpoint uses NVIDIA Nemotron through NVIDIA NIM to choose the
diagnosis status and misconception label from each learner's answer, reasoning,
code, and the misconception taxonomy. Local AST and sandbox execution analyses
are passed to Nemotron as supporting evidence. There is no fabricated local
diagnosis fallback: if Nemotron cannot be reached, diagnosis is marked unavailable.

Set `NVIDIA_API_KEY` in the environment used to start the backend. The default model
is `nvidia/nemotron-3.5-lightning-30b-a3b` and the default endpoint is NVIDIA's
hosted NIM chat completions API. You can override these with
`NVIDIA_NEMOTRON_MODEL` and `NVIDIA_NIM_BASE_URL`.

PowerShell example:

```powershell
$env:NVIDIA_API_KEY = "your NVIDIA API key"
```

Restart the backend after setting the key. The diagnosis response's `model_version`
identifies the Nemotron model that produced the result.
