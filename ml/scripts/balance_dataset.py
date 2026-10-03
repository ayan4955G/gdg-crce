"""
Dataset Balancer script for Re:Learn.
Analyzes class distribution across misconceptions and produces balanced resampled subsets if needed.
"""

import json
import os
import random
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
RAW_FILE = DATA_DIR / "raw" / "raw_dataset.json"
BALANCED_FILE = DATA_DIR / "processed" / "balanced_dataset.json"


def balance_dataset(target_samples_per_class: int = None):
    if not RAW_FILE.exists():
        print(f"Error: {RAW_FILE} does not exist. Run generate_dataset.py first.")
        return

    with open(RAW_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Group by primary misconception
    by_misconception = {}
    for item in data:
        misc = item["misconception"]["primary"] or "CORRECT"
        by_misconception.setdefault(misc, []).append(item)

    print("Initial class distribution:")
    for misc, items in sorted(by_misconception.items()):
        print(f"  {misc}: {len(items)} examples")

    if target_samples_per_class is None:
        # Balance to median class size
        counts = [len(items) for items in by_misconception.values()]
        target_samples_per_class = sorted(counts)[len(counts) // 2]

    print(f"\nTargeting {target_samples_per_class} samples per class...")

    balanced = []
    random.seed(42)
    for misc, items in by_misconception.items():
        if len(items) >= target_samples_per_class:
            balanced.extend(random.sample(items, target_samples_per_class))
        else:
            # Upsample with replacement if undersampled
            oversampled = items.copy()
            while len(oversampled) < target_samples_per_class:
                oversampled.append(random.choice(items))
            balanced.extend(oversampled)

    random.shuffle(balanced)

    BALANCED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BALANCED_FILE, "w", encoding="utf-8") as f:
        json.dump(balanced, f, indent=2)

    print(f"Balanced dataset written to {BALANCED_FILE} ({len(balanced)} total items)")


if __name__ == "__main__":
    balance_dataset()
