import os
import json
import random
from collections import defaultdict
from typing import Dict, List, Any

def split_dataset_stratified(
    raw_path: str = "ml/data/raw/dataset.json",
    output_dir: str = "ml/data"
):
    print(f"[*] Splitting dataset from {raw_path} (Stratified + Unseen benchmark)...")
    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Separate unseen_questions benchmark (e.g. transfer, partial understanding, and difficult contrast items)
    unseen_items = []
    standard_pool = []

    for item in data:
        cat = item.get("sample_category", "")
        # Reserve a distinct subset of contrast & partial items for unseen transfer evaluation
        if cat in ["partial_understanding"] or (cat == "difficult_contrast_same_answer" and int(item["id"].replace("EX", "")) % 2 == 0):
            unseen_items.append(item)
        else:
            standard_pool.append(item)

    # 2. Group standard_pool by class to stratify train/val/test
    by_class = defaultdict(list)
    for item in standard_pool:
        label = item["misconception"]["primary"]
        by_class[label].append(item)

    train_data = []
    val_data = []
    test_data = []

    random.seed(42)
    for label, items in by_class.items():
        random.shuffle(items)
        n = len(items)
        n_train = max(1, int(0.70 * n))
        n_val = max(1, int(0.15 * n))
        
        train_data.extend(items[:n_train])
        val_data.extend(items[n_train:n_train + n_val])
        test_data.extend(items[n_train + n_val:])

    # Shuffle splits
    random.shuffle(train_data)
    random.shuffle(val_data)
    random.shuffle(test_data)
    random.shuffle(unseen_items)

    splits = {
        "train": train_data,
        "validation": val_data,
        "test": test_data,
        "unseen_questions": unseen_items
    }

    for split_name, items in splits.items():
        split_dir = os.path.join(output_dir, split_name)
        os.makedirs(split_dir, exist_ok=True)
        out_file = os.path.join(split_dir, "dataset.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)
        print(f"    [OK] {split_name:18s}: {len(items):4d} samples -> {out_file}")

    processed_dir = os.path.join(output_dir, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    with open(os.path.join(processed_dir, "all_cleaned.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"    [OK] Processed all_cleaned.json: {len(data)} samples")

if __name__ == "__main__":
    split_dataset_stratified()
