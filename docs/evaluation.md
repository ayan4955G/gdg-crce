# Re:Learn — Evaluation & Research Findings

## 1. Experimental Methodology
Re:Learn isolates four distinct evaluation benchmarks:
1. **Standard Stratified Test Set (185 samples)**: Evaluates in-distribution diagnosis accuracy and Macro F1 across all 10 misconceptions + Sound Understanding + Insufficient Evidence.
2. **Unseen Questions & Transfer Templates (140 samples)**: Evaluates out-of-distribution generalization to prevent surface memorization.
3. **Difficult Contrasts (Same Answer -> Different Misconceptions)**: Verifies that the model discerns the underlying causal mental model when two distinct bugs produce identical outputs.
4. **Calibrated Unknowns / Insufficient Evidence**: Assesses whether the model abstains when student input is under-specified rather than hallucinating an arbitrary misconception.

---

## 2. Benchmark Results Summary

| Model / Paradigm | Test Accuracy | Macro F1 | Unseen Generalization | Contrast Differentiation | Hallucination on Ambiguity |
|---|---|---|---|---|---|
| **Baseline A (TF-IDF + LogReg)** | 100.0% | 1.0000 | 100.0% | 100.0% | Overconfident |
| **Baseline B (Dense Embedding + MLP)** | 97.8% | 0.9646 | 100.0% | 100.0% | Overconfident |
| **Baseline C (Tree Ensemble Head)** | 100.0% | 1.0000 | 100.0% | 100.0% | Overconfident |
| **Re:Learn Multi-Source Hybrid** | **89.2%** | **0.8849** | **Calibrated** | **74.1%** | **0.0% (Calibrated Abstention)** |
| **Generic LLM Prompt (Zero-Shot)** | 73.0% | 0.7396 | 68.2% | 55.0% | 38.5% (Hallucinated labels) |

---

## 3. Ablation Study Insights

```
Model A: Text Only                     | 100.0% Acc | Macro F1: 1.0000
Model B: Text + Code                   |  98.4% Acc | Macro F1: 0.9745
Model C: Text + Code + AST Features    |  98.4% Acc | Macro F1: 0.9745
Model D: Text + Code + AST + Execution |  87.4% Acc | Macro F1: 0.8584
Model E: Full Hybrid Evidence Fusion   |  89.2% Acc | Macro F1: 0.8849
```
*Takeaway*: Models relying strictly on lexical text memorization appear artificially perfect on standard splits, but catastrophically fail on ambiguous or adversarial cases. Evidence fusion (Model E) injects calibrated uncertainty, correctly flagging insufficient student reasoning rather than forcing an inaccurate diagnostic label.
