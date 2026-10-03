import json
import os
import joblib
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix

class BaselineTfidfModel:
    """
    Baseline A: TF-IDF representation of question + code + student reasoning
    coupled with L2-regularized Multiclass Logistic Regression.
    """

    def __init__(self, model_dir: str = "ml/saved_models/tfidf"):
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=3000, sublinear_tf=True)),
            ("clf", LogisticRegression(max_iter=1000, C=1.0, class_weight="balanced", random_state=42))
        ])
        self.classes_ = []

    def _prepare_text(self, item: Dict[str, Any]) -> str:
        q_text = item.get("question", {}).get("text", "")
        code = item.get("learner_response", {}).get("code", "")
        reasoning = item.get("learner_response", {}).get("reasoning", "")
        answer = str(item.get("learner_response", {}).get("answer", ""))
        return f"{q_text}\nCODE:\n{code}\nANSWER:\n{answer}\nREASONING:\n{reasoning}"

    def train(self, train_path: str, val_path: str) -> Dict[str, Any]:
        with open(train_path, "r", encoding="utf-8") as f:
            train_data = json.load(f)
        with open(val_path, "r", encoding="utf-8") as f:
            val_data = json.load(f)

        X_train = [self._prepare_text(item) for item in train_data]
        y_train = [item["misconception"]["primary"] for item in train_data]

        X_val = [self._prepare_text(item) for item in val_data]
        y_val = [item["misconception"]["primary"] for item in val_data]

        print(f"[*] Training Baseline A (TF-IDF + Logistic Regression) on {len(X_train)} samples...")
        self.pipeline.fit(X_train, y_train)
        self.classes_ = list(self.pipeline.named_steps["clf"].classes_)

        y_pred = self.pipeline.predict(X_val)
        acc = accuracy_score(y_val, y_pred)
        macro_f1 = f1_score(y_val, y_pred, average="macro", zero_division=0)
        weighted_f1 = f1_score(y_val, y_pred, average="weighted", zero_division=0)
        report = classification_report(y_val, y_pred, output_dict=True, zero_division=0)
        cm = confusion_matrix(y_val, y_pred, labels=self.classes_).tolist()

        # Save model artifact
        save_path = os.path.join(self.model_dir, "model.joblib")
        joblib.dump(self.pipeline, save_path)
        print(f"[OK] Saved TF-IDF baseline to {save_path}")

        metrics = {
            "model": "Baseline A (TF-IDF + Logistic Regression)",
            "accuracy": round(float(acc), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_f1": round(float(weighted_f1), 4),
            "classes": self.classes_,
            "confusion_matrix": cm,
            "classification_report": report
        }
        return metrics

    def predict(self, item: Dict[str, Any]) -> Dict[str, Any]:
        text = self._prepare_text(item)
        probs = self.pipeline.predict_proba([text])[0]
        top_idx = int(np.argmax(probs))
        label = self.classes_[top_idx]
        conf = float(probs[top_idx])

        # Alternatives
        ranked_indices = np.argsort(probs)[::-1]
        alternatives = [
            {"id": self.classes_[idx], "confidence": round(float(probs[idx]), 4)}
            for idx in ranked_indices[1:4]
        ]

        return {
            "primary": label,
            "confidence": round(conf, 4),
            "alternatives": alternatives,
            "probabilities": {cls: round(float(p), 4) for cls, p in zip(self.classes_, probs)}
        }

    def load(self):
        save_path = os.path.join(self.model_dir, "model.joblib")
        if os.path.exists(save_path):
            self.pipeline = joblib.load(save_path)
            self.classes_ = list(self.pipeline.named_steps["clf"].classes_)
            return True
        return False

if __name__ == "__main__":
    model = BaselineTfidfModel()
    metrics = model.train("ml/data/train/dataset.json", "ml/data/validation/dataset.json")
    print("Baseline A Validation Results:")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(f"Macro F1: {metrics['macro_f1']:.4f}")
