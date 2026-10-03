from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Diagnostic Schemas
class DiagnosisRequest(BaseModel):
    question_id: str
    question: str
    response: Optional[str] = ""
    code: Optional[str] = ""
    reasoning: Optional[str] = ""
    expected_answer: Optional[str] = ""
    previous_attempts: Optional[List[Dict[str, Any]]] = []

class CandidateMisconception(BaseModel):
    id: str
    confidence: float
    name: Optional[str] = None
    rationale: Optional[str] = None

class DiagnosisResponse(BaseModel):
    status: str # CORRECT, DIAGNOSED, UNKNOWN, INSUFFICIENT_EVIDENCE, MODEL_UNAVAILABLE
    primary: CandidateMisconception
    alternatives: List[CandidateMisconception] = []
    evidence: List[str] = []
    model_version: str
    expert_reasoning: Optional[str] = None

# Intervention Schemas
class InterventionRequest(BaseModel):
    misconception_id: str
    learner_response: Optional[str] = ""
    learner_history: Optional[Dict[str, Any]] = {}
    previous_interventions: Optional[List[str]] = []

class InterventionResponse(BaseModel):
    type: str # hint, guided_reasoning, counterexample, code_trace, worked_example
    content: str
    target_misconception: str
    follow_up_question: str
    is_validated: bool
    validation_notes: Optional[str] = None

# Resolution Schemas
class AttemptItem(BaseModel):
    question_type: str = "isomorphic" # isomorphic, different_surface, transfer
    question_text: str
    student_answer: str
    expected_answer: str
    reasoning: Optional[str] = ""
    code: Optional[str] = ""

class ResolutionRequest(BaseModel):
    misconception_id: str
    attempts: List[AttemptItem]

class ResolutionResponse(BaseModel):
    status: str # UNRESOLVED, IMPROVING, LIKELY_RESOLVED, INSUFFICIENT_EVIDENCE
    confidence: float
    evidence: Dict[str, Any]
    summary: str
    attempt_evaluations: List[Dict[str, Any]] = []

# Question Schemas
class QuestionSchema(BaseModel):
    id: str
    title: str
    prompt: str
    starter_code: Optional[str] = ""
    expected_answer: str
    concept: str
    difficulty: str = "beginner"
    is_transfer_question: bool = False
    options: Optional[List[str]] = None

# Learner Schemas
class LearnerMasteryUpdate(BaseModel):
    concept: str
    mastery_score: float

class LearnerProfileResponse(BaseModel):
    learner_id: str
    concepts: Dict[str, Any]
    misconceptions: Dict[str, Any]
    total_interactions: int
    active_misconceptions_count: int
    resolved_misconceptions_count: int
