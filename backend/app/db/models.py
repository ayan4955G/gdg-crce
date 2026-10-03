from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True)
    username = Column(String(128), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), default="learner", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    responses = relationship("LearnerResponse", back_populates="user", cascade="all, delete-orphan")
    learner_concepts = relationship("LearnerConcept", back_populates="user", cascade="all, delete-orphan")
    learner_misconceptions = relationship("LearnerMisconception", back_populates="user", cascade="all, delete-orphan")


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    slug = Column(String(128), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    misconceptions = relationship("Misconception", back_populates="concept", cascade="all, delete-orphan")
    question_links = relationship("QuestionConcept", back_populates="concept", cascade="all, delete-orphan")


class Misconception(Base):
    __tablename__ = "misconceptions"

    id = Column(String(32), primary_key=True) # P001..P010
    name = Column(String(255), nullable=False)
    concept_id = Column(String(64), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=False)
    observable_symptoms = Column(Text, nullable=True)
    common_errors = Column(Text, nullable=True)
    diagnostic_patterns = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    concept = relationship("Concept", back_populates="misconceptions")
    diagnoses = relationship("Diagnosis", back_populates="misconception")


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    starter_code = Column(Text, nullable=True)
    expected_output = Column(Text, nullable=True)
    expected_answer = Column(Text, nullable=True)
    solution_code = Column(Text, nullable=True)
    question_type = Column(String(32), default="code", nullable=False)
    difficulty = Column(String(32), default="beginner", nullable=False)
    is_transfer_question = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    concepts = relationship("QuestionConcept", back_populates="question", cascade="all, delete-orphan")
    responses = relationship("LearnerResponse", back_populates="question", cascade="all, delete-orphan")


class QuestionConcept(Base):
    __tablename__ = "question_concepts"

    id = Column(String(64), primary_key=True)
    question_id = Column(String(64), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(String(64), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False, index=True)
    is_primary = Column(Boolean, default=True, nullable=False)
    weight = Column(Float, default=1.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    question = relationship("Question", back_populates="concepts")
    concept = relationship("Concept", back_populates="question_links")

    __table_args__ = (UniqueConstraint("question_id", "concept_id", name="uq_question_concept"),)


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(String(64), primary_key=True)
    model_name = Column(String(128), nullable=False)
    version_tag = Column(String(64), nullable=False)
    model_type = Column(String(64), nullable=False) # diagnosis, resolution, baseline
    parameters_json = Column(Text, nullable=True)
    metrics_summary_json = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LearnerResponse(Base):
    __tablename__ = "learner_responses"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(64), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_number = Column(Integer, default=1, nullable=False)
    response_text = Column(Text, nullable=True)
    submitted_code = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False, nullable=False)
    execution_stdout = Column(Text, nullable=True)
    execution_stderr = Column(Text, nullable=True)
    execution_exit_code = Column(Integer, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="responses")
    question = relationship("Question", back_populates="responses")
    evidence_items = relationship("ResponseEvidence", back_populates="response", cascade="all, delete-orphan")
    diagnosis = relationship("Diagnosis", back_populates="response", uselist=False, cascade="all, delete-orphan")


class ResponseEvidence(Base):
    __tablename__ = "response_evidence"

    id = Column(String(64), primary_key=True)
    response_id = Column(String(64), ForeignKey("learner_responses.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(String(64), nullable=False)
    feature_name = Column(String(128), nullable=False)
    feature_value = Column(Text, nullable=False)
    confidence_weight = Column(Float, default=1.0, nullable=False)
    source_component = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    response = relationship("LearnerResponse", back_populates="evidence_items")


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(String(64), primary_key=True)
    response_id = Column(String(64), ForeignKey("learner_responses.id", ondelete="CASCADE"), nullable=False, index=True)
    primary_misconception_id = Column(String(32), ForeignKey("misconceptions.id", ondelete="SET NULL"), nullable=True, index=True)
    model_version_id = Column(String(64), ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(32), nullable=False) # CORRECT, DIAGNOSED, AMBIGUOUS, UNKNOWN, INSUFFICIENT_EVIDENCE
    confidence = Column(Float, nullable=False)
    expert_reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    response = relationship("LearnerResponse", back_populates="diagnosis")
    misconception = relationship("Misconception", back_populates="diagnoses")
    candidates = relationship("DiagnosisCandidate", back_populates="diagnosis", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="diagnosis", cascade="all, delete-orphan")


class DiagnosisCandidate(Base):
    __tablename__ = "diagnosis_candidates"

    id = Column(String(64), primary_key=True)
    diagnosis_id = Column(String(64), ForeignKey("diagnoses.id", ondelete="CASCADE"), nullable=False, index=True)
    misconception_id = Column(String(32), ForeignKey("misconceptions.id", ondelete="CASCADE"), nullable=False)
    rank_order = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    diagnosis = relationship("Diagnosis", back_populates="candidates")


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(String(64), primary_key=True)
    diagnosis_id = Column(String(64), ForeignKey("diagnoses.id", ondelete="CASCADE"), nullable=False, index=True)
    misconception_id = Column(String(32), ForeignKey("misconceptions.id", ondelete="CASCADE"), nullable=False)
    strategy_type = Column(String(64), nullable=False)
    scaffolding_content = Column(Text, nullable=False)
    follow_up_question_id = Column(String(64), ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    is_validated = Column(Boolean, default=True, nullable=False)
    validation_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    diagnosis = relationship("Diagnosis", back_populates="interventions")
    attempts = relationship("InterventionAttempt", back_populates="intervention", cascade="all, delete-orphan")


class InterventionAttempt(Base):
    __tablename__ = "intervention_attempts"

    id = Column(String(64), primary_key=True)
    intervention_id = Column(String(64), ForeignKey("interventions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    learner_response_text = Column(Text, nullable=True)
    is_satisfactory = Column(Boolean, default=False, nullable=False)
    time_spent_seconds = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    intervention = relationship("Intervention", back_populates="attempts")


class ResolutionAssessment(Base):
    __tablename__ = "resolution_assessments"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    misconception_id = Column(String(32), ForeignKey("misconceptions.id", ondelete="CASCADE"), nullable=False, index=True)
    intervention_id = Column(String(64), ForeignKey("interventions.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(32), nullable=False) # UNRESOLVED, IMPROVING, LIKELY_RESOLVED, INSUFFICIENT_EVIDENCE
    confidence = Column(Float, nullable=False)
    isomorphic_passed = Column(Boolean, default=False, nullable=False)
    transfer_passed = Column(Boolean, default=False, nullable=False)
    evidence_summary = Column(Text, nullable=True)
    model_version_id = Column(String(64), ForeignKey("model_versions.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LearnerConcept(Base):
    __tablename__ = "learner_concepts"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    concept_id = Column(String(64), ForeignKey("concepts.id", ondelete="CASCADE"), nullable=False)
    mastery_score = Column(Float, default=0.0, nullable=False)
    confidence = Column(Float, default=0.5, nullable=False)
    attempts_count = Column(Integer, default=0, nullable=False)
    successes_count = Column(Integer, default=0, nullable=False)
    last_practiced_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="learner_concepts")
    concept = relationship("Concept")

    __table_args__ = (UniqueConstraint("user_id", "concept_id", name="uq_user_concept"),)


class LearnerMisconception(Base):
    __tablename__ = "learner_misconceptions"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    misconception_id = Column(String(32), ForeignKey("misconceptions.id", ondelete="CASCADE"), nullable=False)
    occurrences_count = Column(Integer, default=1, nullable=False)
    is_currently_resolved = Column(Boolean, default=False, nullable=False)
    last_diagnosed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_resolved_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="learner_misconceptions")
    misconception = relationship("Misconception")

    __table_args__ = (UniqueConstraint("user_id", "misconception_id", name="uq_user_misconception"),)


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(String(64), primary_key=True)
    model_version_id = Column(String(64), ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    input_sample_id = Column(String(64), nullable=True)
    predicted_label = Column(String(64), nullable=False)
    true_label = Column(String(64), nullable=True)
    confidence = Column(Float, nullable=False)
    probabilities_json = Column(Text, nullable=True)
    inference_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(64), primary_key=True)
    model_version_id = Column(String(64), ForeignKey("model_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    dataset_split = Column(String(64), nullable=False) # train, validation, test, unseen_questions
    accuracy = Column(Float, nullable=False)
    macro_f1 = Column(Float, nullable=False)
    weighted_f1 = Column(Float, nullable=False)
    metrics_json = Column(Text, nullable=False)
    confusion_matrix_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
