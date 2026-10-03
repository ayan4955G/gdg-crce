import os
import json
from collections import Counter
import pandas as pd

def compute_statistics():
    base_dir = "ml/data"
    splits = ["raw", "train", "validation", "test", "unseen_questions"]

    print("=" * 60)
    print("             RE:LEARN DATASET AUDIT & STATISTICS")
    print("=" * 60)

    summary = []

    for s in splits:
        if s == "raw":
            p = os.path.join(base_dir, "raw", "dataset.json")
        else:
            p = os.path.join(base_dir, s, "dataset.json")

        if not os.path.exists(p):
            continue

        with open(p, "r", encoding="utf-8") as f:
            items = json.load(f)

        labels = Counter()
        concepts = Counter()
        categories = Counter()

        for it in items:
            labels[it["misconception"]["primary"]] += 1
            concepts[it["question"]["concept"]] += 1
            categories[it.get("sample_category", "unknown")] += 1

        summary.append({
            "Split": s,
            "Total Samples": len(items),
            "Unique Labels": len(labels),
            "Concepts": len(concepts),
            "Top Misconception": labels.most_common(1)[0][0] if labels else "N/A"
        })

        print(f"\n--- Split: {s.upper()} ({len(items)} samples) ---")
        print("Misconception Distribution:")
        for lbl, count in sorted(labels.items()):
            pct = (count / len(items)) * 100
            print(f"  {lbl:24s}: {count:4d} ({pct:5.1f}%)")

        print("Category Distribution:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat:32s}: {count:4d}")

    print("\n" + "=" * 60)
    print("SUMMARY TABLE:")
    print("=" * 60)
    for row in summary:
        print(f"{row['Split']:18s} | Count: {row['Total Samples']:4d} | Classes: {row['Unique Labels']:2d}")

if __name__ == "__main__":
    compute_statistics()
