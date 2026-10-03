import os
import sys
import json
import numpy as np
sys.path.insert(0, os.path.abspath("."))

from typing import Dict, Any, List
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
from ml.models.baseline_tfidf import BaselineTfidfModel
from ml.models.baseline_mlp import BaselineMlpModel
from ml.models.baseline_transformer import BaselineTransformerHeadModel
from ml.models.hybrid_diagnoser import HybridMisconceptionDiagnoser

def run_evaluation():
    print("=" * 70)
    print("         RE:LEARN COMPREHENSIVE BENCHMARK & EVALUATION")
    print("=" * 70)

    # Load splits
    test_path = "ml/data/test/dataset.json"
    unseen_path = "ml/data/unseen_questions/dataset.json"

    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    with open(unseen_path, "r", encoding="utf-8") as f:
        unseen_data = json.load(f)

    # Initialize models
    tfidf_model = BaselineTfidfModel()
    tfidf_model.load()

    mlp_model = BaselineMlpModel()
    mlp_model.load()

    gbm_model = BaselineTransformerHeadModel()
    gbm_model.load()

    hybrid = HybridMisconceptionDiagnoser()
    hybrid.train_or_ensure()

    models = {
        "Baseline A (TF-IDF + LogReg)": lambda item: tfidf_model.predict(item)["primary"],
        "Baseline B (Dense Embedding + MLP)": lambda item: mlp_model.predict(item)["primary"],
        "Baseline C (GBM Classifier Head)": lambda item: gbm_model.predict(item)["primary"],
        "Re:Learn Flagship (Hybrid Engine)": lambda item: hybrid.diagnose(
            question_id=item["question"]["id"],
            question_text=item["question"]["text"],
            student_answer=item["learner_response"].get("answer", ""),
            reasoning=item["learner_response"].get("reasoning", ""),
            code=item["learner_response"].get("code", ""),
            expected_answer=item.get("expected_answer", "")
        )["primary"]["id"]
    }

    results = {}

    # 1. Standard Test Set Evaluation
    print("\n[+] 1. Evaluating on Standard Test Set (185 samples):")
    y_true = [item["misconception"]["primary"] for item in test_data]

    for name, predictor in models.items():
        y_pred = []
        for item in test_data:
            y_pred.append(predictor(item))

        acc = accuracy_score(y_true, y_pred)
        macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
        weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

        results[name] = {
            "test_accuracy": round(float(acc), 4),
            "test_macro_f1": round(float(macro_f1), 4),
            "test_weighted_f1": round(float(weighted_f1), 4)
        }
        print(f"    {name:36s} | Acc: {acc*100:5.1f}% | Macro F1: {macro_f1:.4f} | Weighted F1: {weighted_f1:.4f}")

    # 2. Unseen Questions / Generalization Benchmark
    print("\n[+] 2. Evaluating on Unseen Questions & Transfer Templates (140 samples):")
    y_true_unseen = [item["misconception"]["primary"] for item in unseen_data]

    for name, predictor in models.items():
        y_pred_unseen = []
        for item in unseen_data:
            y_pred_unseen.append(predictor(item))

        acc = accuracy_score(y_true_unseen, y_pred_unseen)
        macro_f1 = f1_score(y_true_unseen, y_pred_unseen, average="macro", zero_division=0)
        results[name]["unseen_accuracy"] = round(float(acc), 4)
        results[name]["unseen_macro_f1"] = round(float(macro_f1), 4)
        print(f"    {name:36s} | Unseen Acc: {acc*100:5.1f}% | Unseen F1: {macro_f1:.4f}")

    # 3. Difficult Contrast Differentiation
    # Same Answer -> Different Misconceptions
    contrast_items = [i for i in test_data + unseen_data if i.get("sample_category") == "difficult_contrast_same_answer"]
    print(f"\n[+] 3. Difficult Contrast: Same Surface Answer -> Different Misconceptions ({len(contrast_items)} samples):")
    if contrast_items:
        y_true_contrast = [item["misconception"]["primary"] for item in contrast_items]
        for name, predictor in models.items():
            y_pred_c = [predictor(item) for item in contrast_items]
            acc_c = accuracy_score(y_true_contrast, y_pred_c)
            results[name]["contrast_differentiation_accuracy"] = round(float(acc_c), 4)
            print(f"    {name:36s} | Contrast Differentiation Acc: {acc_c*100:5.1f}%")

    # Save summary
    os.makedirs("docs", exist_ok=True)
    with open("docs/evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("\n[OK] Evaluation metrics written to docs/evaluation_results.json")

    return results

if __name__ == "__main__":
    # Ensure baseline models are trained first
    BaselineTfidfModel().train("ml/data/train/dataset.json", "ml/data/validation/dataset.json")
    BaselineMlpModel().train("ml/data/train/dataset.json", "ml/data/validation/dataset.json")
    BaselineTransformerHeadModel().train("ml/data/train/dataset.json", "ml/data/validation/dataset.json")
    run_evaluation()
