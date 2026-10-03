-- Re:Learn Database Schema DDL
-- Compatible with PostgreSQL and SQLite

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    username VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(32) DEFAULT 'learner' NOT NULL, -- learner, instructor, researcher, admin
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS concepts (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    slug VARCHAR(128) UNIQUE NOT NULL,
    description TEXT,
    order_index INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS misconceptions (
    id VARCHAR(32) PRIMARY KEY, -- e.g. P001, P002 ...
    name VARCHAR(255) NOT NULL,
    concept_id VARCHAR(64) NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    observable_symptoms TEXT, -- structured or serialized list
    common_errors TEXT,
    diagnostic_patterns TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_misconceptions_concept ON misconceptions(concept_id);

CREATE TABLE IF NOT EXISTS questions (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    prompt TEXT NOT NULL,
    starter_code TEXT,
    expected_output TEXT,
    expected_answer TEXT,
    solution_code TEXT,
    question_type VARCHAR(32) DEFAULT 'code' NOT NULL, -- code, code_trace, explanation, multiple_choice
    difficulty VARCHAR(32) DEFAULT 'beginner' NOT NULL, -- beginner, intermediate, advanced
    is_transfer_question BOOLEAN DEFAULT FALSE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(question_type);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);

CREATE TABLE IF NOT EXISTS question_concepts (
    id VARCHAR(64) PRIMARY KEY,
    question_id VARCHAR(64) NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    concept_id VARCHAR(64) NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT TRUE NOT NULL,
    weight FLOAT DEFAULT 1.0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(question_id, concept_id)
);
CREATE INDEX IF NOT EXISTS idx_qc_question ON question_concepts(question_id);
CREATE INDEX IF NOT EXISTS idx_qc_concept ON question_concepts(concept_id);

CREATE TABLE IF NOT EXISTS model_versions (
    id VARCHAR(64) PRIMARY KEY,
    model_name VARCHAR(128) NOT NULL,
    version_tag VARCHAR(64) NOT NULL,
    model_type VARCHAR(64) NOT NULL, -- diagnosis, resolution, baseline
    parameters_json TEXT,
    metrics_summary_json TEXT,
    is_active BOOLEAN DEFAULT FALSE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS learner_responses (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id VARCHAR(64) NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    attempt_number INTEGER DEFAULT 1 NOT NULL,
    response_text TEXT,
    submitted_code TEXT,
    is_correct BOOLEAN DEFAULT FALSE NOT NULL,
    execution_stdout TEXT,
    execution_stderr TEXT,
    execution_exit_code INTEGER,
    execution_time_ms FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_lr_user ON learner_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_lr_question ON learner_responses(question_id);

CREATE TABLE IF NOT EXISTS response_evidence (
    id VARCHAR(64) PRIMARY KEY,
    response_id VARCHAR(64) NOT NULL REFERENCES learner_responses(id) ON DELETE CASCADE,
    evidence_type VARCHAR(64) NOT NULL, -- ast_pattern, runtime_error, text_lexical, execution_output
    feature_name VARCHAR(128) NOT NULL,
    feature_value TEXT NOT NULL,
    confidence_weight FLOAT DEFAULT 1.0 NOT NULL,
    source_component VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_re_response ON response_evidence(response_id);

CREATE TABLE IF NOT EXISTS diagnoses (
    id VARCHAR(64) PRIMARY KEY,
    response_id VARCHAR(64) NOT NULL REFERENCES learner_responses(id) ON DELETE CASCADE,
    primary_misconception_id VARCHAR(32) REFERENCES misconceptions(id) ON DELETE SET NULL,
    model_version_id VARCHAR(64) REFERENCES model_versions(id) ON DELETE SET NULL,
    status VARCHAR(32) NOT NULL, -- CORRECT, DIAGNOSED, AMBIGUOUS, UNKNOWN, INSUFFICIENT_EVIDENCE
    confidence FLOAT NOT NULL,
    expert_reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_diagnoses_response ON diagnoses(response_id);
CREATE INDEX IF NOT EXISTS idx_diagnoses_misconception ON diagnoses(primary_misconception_id);

CREATE TABLE IF NOT EXISTS diagnosis_candidates (
    id VARCHAR(64) PRIMARY KEY,
    diagnosis_id VARCHAR(64) NOT NULL REFERENCES diagnoses(id) ON DELETE CASCADE,
    misconception_id VARCHAR(32) NOT NULL REFERENCES misconceptions(id) ON DELETE CASCADE,
    rank_order INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    rationale TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_dc_diagnosis ON diagnosis_candidates(diagnosis_id);

CREATE TABLE IF NOT EXISTS interventions (
    id VARCHAR(64) PRIMARY KEY,
    diagnosis_id VARCHAR(64) NOT NULL REFERENCES diagnoses(id) ON DELETE CASCADE,
    misconception_id VARCHAR(32) NOT NULL REFERENCES misconceptions(id) ON DELETE CASCADE,
    strategy_type VARCHAR(64) NOT NULL, -- hint, guided_reasoning, counterexample, code_trace, worked_example
    scaffolding_content TEXT NOT NULL,
    follow_up_question_id VARCHAR(64) REFERENCES questions(id) ON DELETE SET NULL,
    is_validated BOOLEAN DEFAULT TRUE NOT NULL,
    validation_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_interventions_diagnosis ON interventions(diagnosis_id);

CREATE TABLE IF NOT EXISTS intervention_attempts (
    id VARCHAR(64) PRIMARY KEY,
    intervention_id VARCHAR(64) NOT NULL REFERENCES interventions(id) ON DELETE CASCADE,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    learner_response_text TEXT,
    is_satisfactory BOOLEAN DEFAULT FALSE NOT NULL,
    time_spent_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ia_intervention ON intervention_attempts(intervention_id);

CREATE TABLE IF NOT EXISTS resolution_assessments (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    misconception_id VARCHAR(32) NOT NULL REFERENCES misconceptions(id) ON DELETE CASCADE,
    intervention_id VARCHAR(64) REFERENCES interventions(id) ON DELETE SET NULL,
    status VARCHAR(32) NOT NULL, -- UNRESOLVED, IMPROVING, LIKELY_RESOLVED, INSUFFICIENT_EVIDENCE
    confidence FLOAT NOT NULL,
    isomorphic_passed BOOLEAN DEFAULT FALSE NOT NULL,
    transfer_passed BOOLEAN DEFAULT FALSE NOT NULL,
    evidence_summary TEXT,
    model_version_id VARCHAR(64) REFERENCES model_versions(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ra_user ON resolution_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_ra_misconception ON resolution_assessments(misconception_id);

CREATE TABLE IF NOT EXISTS learner_concepts (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    concept_id VARCHAR(64) NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    mastery_score FLOAT DEFAULT 0.0 NOT NULL, -- 0.0 to 1.0 calibrated
    confidence FLOAT DEFAULT 0.5 NOT NULL,
    attempts_count INTEGER DEFAULT 0 NOT NULL,
    successes_count INTEGER DEFAULT 0 NOT NULL,
    last_practiced_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(user_id, concept_id)
);
CREATE INDEX IF NOT EXISTS idx_lc_user ON learner_concepts(user_id);

CREATE TABLE IF NOT EXISTS learner_misconceptions (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    misconception_id VARCHAR(32) NOT NULL REFERENCES misconceptions(id) ON DELETE CASCADE,
    occurrences_count INTEGER DEFAULT 1 NOT NULL,
    is_currently_resolved BOOLEAN DEFAULT FALSE NOT NULL,
    last_diagnosed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_resolved_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(user_id, misconception_id)
);
CREATE INDEX IF NOT EXISTS idx_lm_user ON learner_misconceptions(user_id);

CREATE TABLE IF NOT EXISTS model_predictions (
    id VARCHAR(64) PRIMARY KEY,
    model_version_id VARCHAR(64) NOT NULL REFERENCES model_versions(id) ON DELETE CASCADE,
    input_sample_id VARCHAR(64),
    predicted_label VARCHAR(64) NOT NULL,
    true_label VARCHAR(64),
    confidence FLOAT NOT NULL,
    probabilities_json TEXT,
    inference_time_ms FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mp_model ON model_predictions(model_version_id);

CREATE TABLE IF NOT EXISTS evaluation_runs (
    id VARCHAR(64) PRIMARY KEY,
    model_version_id VARCHAR(64) NOT NULL REFERENCES model_versions(id) ON DELETE CASCADE,
    dataset_split VARCHAR(64) NOT NULL, -- train, validation, test, unseen_questions
    accuracy FLOAT NOT NULL,
    macro_f1 FLOAT NOT NULL,
    weighted_f1 FLOAT NOT NULL,
    metrics_json TEXT NOT NULL,
    confusion_matrix_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_er_model ON evaluation_runs(model_version_id);
