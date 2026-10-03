# Re:Learn — Model Architecture & Training

## Hybrid Diagnostic Engine Architecture

```
              +-- Text Reasoning Classifier (TF-IDF + LogReg)
              |
Response -----+-- AST Pattern Matcher (Symbolic Rules)
              |
              +-- Sandbox Execution Analyzer (Runtime Errors)
              |
              +-- Lexical Cue Detector (Misconception Markers)
                       |
                 Evidence Fusion Layer
                       |
                 Confidence Calibration
                       |
                 Ambiguity / Insufficient Evidence Detection
                       |
                Final Diagnosis (or Abstention)
```

## Evidence Fusion Weights
- Statistical text classifier: 45% weight
- Deterministic AST/Runtime rule signals: 55% weight (when triggered)
- Ambiguity threshold: Top-2 candidates within 0.08 confidence AND top < 0.70

## Training Pipeline
1. Generate 1,330 labelled examples via `ml/scripts/generate_dataset.py`
2. Validate schema via `ml/scripts/validate_dataset.py`
3. Stratified split with unseen-question holdout via `ml/scripts/split_dataset.py`
4. Train baselines A/B/C independently
5. Hybrid engine loads trained TF-IDF sub-model and combines with rule engine at inference

## Baseline Models

| Model | Architecture | Features |
|---|---|---|
| Baseline A | TF-IDF (1,2)-grams + L2 Logistic Regression | Question + Code + Answer + Reasoning |
| Baseline B | TF-IDF + SVD(64) + MLP(64) | Same concatenated text |
| Baseline C | TF-IDF (1,2)-grams + Random Forest(60 trees) | Same concatenated text |
| **Hybrid** | Baseline A + AST Rules + Execution Sandbox + Text Cues | Multi-source fusion |

## Intervention Engine
Template-based scaffolding with 6-tier hierarchy per misconception. Each intervention is validated for answer leakage before delivery. The engine never decides whether its own intervention succeeded.

## Resolution Model
Independently re-diagnoses post-intervention attempts using the same Hybrid Diagnostic Engine. Compares results across isomorphic, different-surface, and transfer questions.

## Learner Cognitive Model
Bayesian mastery updates: correct answers increase mastery by `0.12 * (1 - current)`, incorrect decrease by `0.15 * current`. Confidence grows logarithmically with attempt count.
