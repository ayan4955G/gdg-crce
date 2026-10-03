import os
import sys
import json
from typing import List, Dict, Any, Optional

# Ensure project root is in path
sys.path.insert(0, os.path.abspath("."))

from fastapi import FastAPI, HTTPException, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from backend.app.schemas.api_schemas import (
    DiagnosisRequest, DiagnosisResponse, CandidateMisconception,
    InterventionRequest, InterventionResponse,
    ResolutionRequest, ResolutionResponse,
    QuestionSchema, LearnerProfileResponse
)
from ml.models.hybrid_diagnoser import HybridMisconceptionDiagnoser
from ml.models.intervention_engine import InterventionEngine
from ml.models.resolution_model import IndependentResolutionAssessor
from ml.models.learner_model import LearnerCognitiveModel

app = FastAPI(
    title="Re:Learn Adaptive Learning Diagnostic API",
    description="Cognitive-diagnostic adaptive learning platform for introductory programming",
    version="1.0.0"
)

# Enable CORS for frontend Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML & Cognitive Engines
diagnoser = HybridMisconceptionDiagnoser()
intervention_engine = InterventionEngine()
resolution_assessor = IndependentResolutionAssessor(diagnoser=diagnoser)

# In-memory learner models store (backed by sqlite/profile models)
learner_profiles: Dict[str, LearnerCognitiveModel] = {}

def get_or_create_learner(learner_id: str) -> LearnerCognitiveModel:
    if learner_id not in learner_profiles:
        learner_profiles[learner_id] = LearnerCognitiveModel(learner_id)
    return learner_profiles[learner_id]

# Curated catalog of interactive programming questions
QUESTIONS_CATALOG = [
    {
        "id": "Q_P003_01",
        "title": "Loop Boundary Check: range(start, stop)",
        "prompt": "What does the following code print to standard output?\n\nfor i in range(1, 5):\n    print(i, end=' ')",
        "starter_code": "for i in range(1, 5):\n    print(i, end=' ')",
        "expected_answer": "1 2 3 4",
        "concept": "loops",
        "difficulty": "beginner",
        "is_transfer_question": False,
        "options": ["1 2 3 4 5", "1 2 3 4", "0 1 2 3 4", "0 1 2 3 4 5"]
    },
    { 
        "id": "Q_P003_TRANSFER",
        "title": "While Loop Boundary Counter (Transfer)",
        "prompt": "How many total times does this loop body execute?\n\ni = 0\nwhile i < 5:\n    i += 1",
        "starter_code": "i = 0\nwhile i < 5:\n    i += 1",
        "expected_answer": "5",
        "concept": "loops",
        "difficulty": "intermediate",
        "is_transfer_question": True,
        "options": ["4", "5", "6", "Infinite Loop"]
    },
    {
        "id": "Q_P006_01",
        "title": "Boolean Condition with 'or'",
        "prompt": "What is printed by this conditional statement?\n\nx = 3\nif x == 1 or 2:\n    print('Match')\nelse:\n    print('No Match')",
        "starter_code": "x = 3\nif x == 1 or 2:\n    print('Match')\nelse:\n    print('No Match')",
        "expected_answer": "Match",
        "concept": "conditionals_and_booleans",
        "difficulty": "beginner",
        "is_transfer_question": False,
        "options": ["Match", "No Match", "SyntaxError", "None"]
    },
    {
        "id": "Q_P006_TRANSFER",
        "title": "Compound Boundary Comparison (Transfer)",
        "prompt": "What does this compound condition evaluate to?\n\nval = 15\nres = val < 5 and val > 10\nprint(res)",
        "starter_code": "val = 15\nres = val < 5 and val > 10\nprint(res)",
        "expected_answer": "False",
        "concept": "conditionals_and_booleans",
        "difficulty": "intermediate",
        "is_transfer_question": True,
        "options": ["True", "False", "None", "Error"]
    },
    {
        "id": "Q_P007_01",
        "title": "Function Output vs Return",
        "prompt": "What does this script print to standard output?\n\ndef compute(a, b):\n    print(a + b)\n\nres = compute(3, 4)\nprint(res)",
        "starter_code": "def compute(a, b):\n    print(a + b)\n\nres = compute(3, 4)\nprint(res)",
        "expected_answer": "7\nNone",
        "concept": "functions_and_scope",
        "difficulty": "beginner",
        "is_transfer_question": False,
        "options": ["7\nNone", "7\n7", "7", "None\nNone"]
    },
    {
        "id": "Q_P001_01",
        "title": "Sequential Variable Reassignment",
        "prompt": "What is the final value of 'a' printed below?\n\na = 10\nb = 20\na = b\nb = 30\nprint(a)",
        "starter_code": "a = 10\nb = 20\na = b\nb = 30\nprint(a)",
        "expected_answer": "20",
        "concept": "variables",
        "difficulty": "beginner",
        "is_transfer_question": False,
        "options": ["10", "20", "30", "50"]
    },
    {
        "id": "Q_P010_01",
        "title": "Mutable List Reference Aliasing",
        "prompt": "What does this print?\n\na = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)",
        "starter_code": "a = [1, 2, 3]\nb = a\nb.append(4)\nprint(a)",
        "expected_answer": "[1, 2, 3, 4]",
        "concept": "data_structures_and_state",
        "difficulty": "intermediate",
        "is_transfer_question": False,
        "options": ["[1, 2, 3]", "[1, 2, 3, 4]", "None", "[4]"]
    }
]

# ----------------- DIAGNOSIS API -----------------
@app.post("/api/v1/diagnose", response_model=DiagnosisResponse)
def diagnose_learner_response(req: DiagnosisRequest):
    """
    POST /api/v1/diagnose
    Accepts question, learner code/response, and natural language reasoning.
    Runs multi-source evidence extraction and outputs calibrated misconception diagnosis.
    """
    answer_text = req.response or ""
    diag = diagnoser.diagnose(
        question_id=req.question_id,
        question_text=req.question,
        student_answer=answer_text,
        reasoning=req.reasoning or "",
        code=req.code or "",
        expected_answer=req.expected_answer or "",
        previous_attempts=req.previous_attempts
    )

    return DiagnosisResponse(
        status=diag["status"],
        primary=CandidateMisconception(
            id=diag["primary"]["id"],
            confidence=diag["primary"]["confidence"],
            name=diag["primary"].get("name")
        ),
        alternatives=[
            CandidateMisconception(id=alt["id"], confidence=alt["confidence"])
            for alt in diag.get("alternatives", [])
        ],
        evidence=diag.get("evidence", []),
        model_version=diag.get("model_version", "relearn-hybrid-v1.0"),
        expert_reasoning=diag.get("expert_reasoning")
    )

# ----------------- INTERVENTION API -----------------
@app.post("/api/v1/intervention", response_model=InterventionResponse)
@app.post("/api/v1/interventions", response_model=InterventionResponse)
def generate_intervention(req: InterventionRequest):
    """
    POST /api/v1/intervention
    Generates targeted pedagogical scaffolding (hints, guided trace, counterexamples)
    strictly validating to prevent answer leakage.
    """
    result = intervention_engine.generate_intervention(
        misconception_id=req.misconception_id,
        learner_response=req.learner_response or "",
        previous_interventions=req.previous_interventions or []
    )
    return InterventionResponse(**result)

# ----------------- RESOLUTION ASSESSMENT API -----------------
@app.post("/api/v1/assess-resolution", response_model=ResolutionResponse)
def assess_resolution(req: ResolutionRequest):
    """
    POST /api/v1/assess-resolution
    Independent resolution assessor evaluating transfer and isomorphic batteries.
    """
    attempts_dict = [att.model_dump() if hasattr(att, "model_dump") else att.dict() for att in req.attempts]
    result = resolution_assessor.assess_resolution(
        misconception_id=req.misconception_id,
        attempts=attempts_dict
    )
    return ResolutionResponse(**result)

# ----------------- QUESTIONS CATALOG -----------------
@app.get("/api/v1/questions", response_model=List[QuestionSchema])
def list_questions(concept: Optional[str] = None):
    if concept:
        return [q for q in QUESTIONS_CATALOG if q["concept"] == concept]
    return QUESTIONS_CATALOG

@app.get("/api/v1/questions/{question_id}", response_model=QuestionSchema)
def get_question(question_id: str):
    for q in QUESTIONS_CATALOG:
        if q["id"] == question_id:
            return q
    raise HTTPException(status_code=404, detail="Question not found")

# ----------------- LEARNER MODEL & PROFILE API -----------------
@app.get("/api/v1/learner/{learner_id}/profile", response_model=LearnerProfileResponse)
def get_learner_profile(learner_id: str):
    profile = get_or_create_learner(learner_id)
    return LearnerProfileResponse(**profile.get_profile())

@app.post("/api/v1/learner/{learner_id}/record-interaction")
def record_learner_interaction(
    learner_id: str,
    question_id: str = Query(...),
    concept: str = Query(...),
    is_correct: bool = Query(...),
    misconception_id: Optional[str] = Query(None)
):
    profile = get_or_create_learner(learner_id)
    diag_mock = {
        "status": "CORRECT" if is_correct else "DIAGNOSED",
        "primary": {"id": "CORRECT" if is_correct else (misconception_id or "P003"), "confidence": 0.88}
    }
    profile.record_interaction(question_id, concept, is_correct, diag_mock)
    return profile.get_profile()

@app.get("/api/v1/learner/{learner_id}/misconceptions")
def get_learner_misconceptions(learner_id: str):
    profile = get_or_create_learner(learner_id)
    return profile.misconceptions

@app.get("/api/v1/learner/{learner_id}/mastery")
def get_learner_mastery(learner_id: str):
    profile = get_or_create_learner(learner_id)
    return profile.get_profile()["concepts"]

# ----------------- EVALUATION & RESEARCH STUDIO API -----------------
@app.get("/api/v1/taxonomy")
def get_misconception_taxonomy():
    path = "ml/taxonomy/misconceptions.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"misconceptions": []}

@app.get("/api/v1/evaluation/metrics")
def get_evaluation_metrics():
    path = "docs/evaluation_results.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "Run ml/evaluation/evaluate.py to generate benchmarks."}

@app.get("/api/v1/evaluation/ablation")
def get_ablation_results():
    path = "docs/ablation_results.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "Run ml/evaluation/ablation_study.py to generate ablation metrics."}

@app.get("/api/v1/evaluation/llm-comparison")
def get_llm_comparison_results():
    path = "docs/llm_comparison_results.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"message": "Run ml/evaluation/llm_comparison.py to generate LLM comparison."}

@app.get("/api/v1/evaluation/simulation-traces")
def get_simulation_traces():
    path = "docs/end_to_end_simulation_traces.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
