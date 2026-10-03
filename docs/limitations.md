# Re:Learn — Known Limitations & Future Work

## Current Limitations

### Taxonomy Coverage
- Only 10 misconceptions (P001–P010) covering introductory programming concepts.
- Does not cover advanced topics (e.g., recursion, OOP, concurrency).
- Taxonomy is flat; no hierarchical prerequisite relationships between misconceptions.

### Dataset
- Synthetically generated — not from real student data.
- Distribution may not reflect real classroom misconception frequencies.
- Limited to 1,330 examples across 10 categories.

### Diagnostic Model
- Text classifier is language-dependent (English only).
- AST analyzer supports Python only; no multi-language support.
- Sandbox execution uses `subprocess` with timeout — not a true containerized sandbox.
- No GPU acceleration; inference is CPU-only.

### Intervention Engine
- Template-based; does not generate novel explanations.
- No A/B testing of intervention effectiveness.
- Scaffolding hierarchy is fixed, not adaptive to learner style.

### Resolution Assessment
- Transfer questions are pre-curated, not dynamically generated.
- Binary pass/fail per attempt; no partial-credit scoring.
- Cannot detect "gaming" (e.g., memorizing answers without understanding).

### Learner Model
- In-memory only; profiles are lost on server restart.
- Bayesian update uses fixed learning rates, not calibrated to individual learners.
- No forgetting curve modeling.

### Infrastructure
- Single-process deployment; no horizontal scaling.
- No authentication or multi-tenancy.
- SQLite/in-memory only; no production database integration.

## Future Work

1. **Real Student Data**: Partner with CS education programs to collect and annotate authentic student misconception data.
2. **Expanded Taxonomy**: Add 50+ misconceptions covering recursion, OOP, data structures.
3. **Multi-Language Support**: Extend AST analysis to JavaScript, Java, C++.
4. **LLM-Augmented Diagnosis**: Use LLMs as an additional evidence source (not replacement) in the fusion layer.
5. **Adaptive Intervention**: Personalize scaffolding style based on learner model feedback.
6. **Spaced Repetition**: Integrate forgetting curves for long-term retention tracking.
7. **Instructor Dashboard**: Add analytics for classroom-level misconception prevalence.
8. **Containerized Sandbox**: Use Docker/gVisor for true isolation of student code execution.
