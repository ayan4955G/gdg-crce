import os
import json
import ast
import sys
from collections import Counter

VALID_MISCONCEPTIONS = {
    f"P{i:03d}" for i in range(1, 11)
} | {"CORRECT", "INSUFFICIENT_EVIDENCE", "UNKNOWN", "AMBIGUOUS"}

def validate_dataset(filepath: str) -> bool:
    print(f"[*] Validating dataset at: {filepath}")
    if not os.path.exists(filepath):
        print(f"[!] Error: File {filepath} does not exist.")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"[!] Invalid JSON format: {e}")
            return False

    if not isinstance(data, list):
        print("[!] Top-level structure must be a JSON array.")
        return False

    seen_ids = set()
    label_counts = Counter()
    errors = []

    for idx, item in enumerate(data):
        item_id = item.get("id")
        if not item_id:
            errors.append(f"Row {idx}: Missing 'id'.")
        elif item_id in seen_ids:
            errors.append(f"Row {idx}: Duplicate id '{item_id}'.")
        seen_ids.add(item_id)

        # Question check
        question = item.get("question")
        if not question or not isinstance(question, dict) or not question.get("text"):
            errors.append(f"Row {idx} ({item_id}): Missing question text.")

        # Code syntax check (if code provided)
        code = (item.get("learner_response") or {}).get("code")
        if code:
            try:
                ast.parse(code)
            except SyntaxError as e:
                # Some questions deliberately test SyntaxErrors (like x + 1 = 5)
                pass

        # Misconception label check
        misc = item.get("misconception")
        if not misc or not isinstance(misc, dict):
            errors.append(f"Row {idx} ({item_id}): Missing 'misconception' object.")
        else:
            primary = misc.get("primary")
            if not primary:
                errors.append(f"Row {idx} ({item_id}): Missing primary misconception.")
            elif primary not in VALID_MISCONCEPTIONS:
                errors.append(f"Row {idx} ({item_id}): Invalid misconception ID '{primary}'.")
            else:
                label_counts[primary] += 1

            for alt in misc.get("alternatives", []):
                if alt not in VALID_MISCONCEPTIONS:
                    errors.append(f"Row {idx} ({item_id}): Invalid alternative misconception ID '{alt}'.")

    if errors:
        print(f"[!] Validation failed with {len(errors)} issues:")
        for err in errors[:10]:
            print(f"    - {err}")
        if len(errors) > 10:
            print(f"    ... and {len(errors) - 10} more.")
        return False

    print(f"[OK] Dataset is valid! Total examples: {len(data)}")
    print("[*] Label distribution:")
    for label, count in label_counts.most_common():
        print(f"    {label:24s}: {count}")

    return True

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "ml/data/raw/dataset.json"
    success = validate_dataset(path)
    sys.exit(0 if success else 1)
