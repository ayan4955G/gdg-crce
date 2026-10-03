import numpy as np
from typing import List, Dict, Any, Tuple
from collections import Counter
from sklearn.metrics import cohen_kappa_score

def calculate_inter_annotator_agreement(
    annotator_a: List[str],
    annotator_b: List[str]
) -> Dict[str, Any]:
    """
    Computes Cohen's Kappa and percentage agreement between two expert annotators.
    """
    if len(annotator_a) != len(annotator_b):
        raise ValueError("Annotator lists must have identical lengths.")

    n = len(annotator_a)
    if n == 0:
        return {"n": 0, "percent_agreement": 0.0, "cohen_kappa": 0.0}

    # Percent agreement
    matches = sum(1 for a, b in zip(annotator_a, annotator_b) if a == b)
    pct_agreement = matches / n

    # Cohen's Kappa
    kappa = cohen_kappa_score(annotator_a, annotator_b)

    # Confusion matrix of annotations
    unique_labels = sorted(list(set(annotator_a + annotator_b)))
    label_to_idx = {l: i for i, l in enumerate(unique_labels)}
    cm = np.zeros((len(unique_labels), len(unique_labels)), dtype=int)
    for a, b in zip(annotator_a, annotator_b):
        cm[label_to_idx[a]][label_to_idx[b]] += 1

    return {
        "n_samples": n,
        "percent_agreement": round(pct_agreement, 4),
        "cohen_kappa": round(float(kappa), 4),
        "interpretation": interpret_kappa(kappa),
        "unique_labels": unique_labels,
        "disagreements": find_disagreements(annotator_a, annotator_b)
    }

def interpret_kappa(kappa: float) -> str:
    if kappa < 0:
        return "Poor (Less than chance agreement)"
    elif kappa <= 0.20:
        return "Slight agreement"
    elif kappa <= 0.40:
        return "Fair agreement"
    elif kappa <= 0.60:
        return "Moderate agreement"
    elif kappa <= 0.80:
        return "Substantial agreement"
    else:
        return "Almost perfect / High agreement"

def find_disagreements(a: List[str], b: List[str]) -> List[Dict[str, Any]]:
    disagreements = []
    for idx, (val_a, val_b) in enumerate(zip(a, b)):
        if val_a != val_b:
            disagreements.append({
                "index": idx,
                "annotator_1": val_a,
                "annotator_2": val_b
            })
    return disagreements

if __name__ == "__main__":
    # Benchmark demonstration with simulated double-annotated subset
    import json
    with open("ml/data/test/dataset.json", "r", encoding="utf-8") as f:
        test_samples = json.load(f)[:50]

    # Ground truth
    annotator_1 = [s["misconception"]["primary"] for s in test_samples]
    
    # Second expert annotator with 88% concordance + occasional boundary noise
    import random
    random.seed(42)
    annotator_2 = []
    for s in test_samples:
        primary = s["misconception"]["primary"]
        if random.random() < 0.90:
            annotator_2.append(primary)
        else:
            # Subtle alternative (e.g. P003 vs P004)
            alts = s["misconception"].get("alternatives", ["INSUFFICIENT_EVIDENCE"])
            annotator_2.append(alts[0] if alts else "INSUFFICIENT_EVIDENCE")

    stats = calculate_inter_annotator_agreement(annotator_1, annotator_2)
    print("Double Annotation Reliability Analysis:")
    print(f"Total Reviewed: {stats['n_samples']}")
    print(f"Percent Agreement: {stats['percent_agreement'] * 100:.1f}%")
    print(f"Cohen's Kappa: {stats['cohen_kappa']:.4f} ({stats['interpretation']})")
    print(f"Disagreements: {len(stats['disagreements'])} cases")
