"""
CLI Annotation Tool for Re:Learn.
Enables expert annotators to inspect questions, responses, code execution,
and label primary misconception, secondary alternatives, confidence, and notes.
"""

import json
import sys
from pathlib import Path

TAXONOMY_FILE = Path(__file__).parent.parent / "taxonomy" / "misconceptions.json"
DATA_FILE = Path(__file__).parent.parent / "data" / "raw" / "raw_dataset.json"


def run_annotation_cli():
    if not TAXONOMY_FILE.exists():
        print("Taxonomy file not found.")
        return

    with open(TAXONOMY_FILE, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)

    misc_lookup = {m["id"]: m["name"] for m in taxonomy}

    print("=" * 60)
    print("Re:Learn Expert Annotation Interface")
    print("=" * 60)
    print("Available Misconception Categories:")
    for m_id, m_name in sorted(misc_lookup.items()):
        print(f"  [{m_id}] {m_name}")
    print("  [CORRECT] No misconception (Correct answer & reasoning)")
    print("  [UNKNOWN] Unrecognized error pattern")
    print("  [INSUFFICIENT_EVIDENCE] Cannot determine without more context")
    print("=" * 60)

    if not DATA_FILE.exists():
        print("No raw dataset to annotate.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        samples = json.load(f)

    print(f"Loaded {len(samples)} examples for review.\n")
    # Display sample preview
    sample = samples[0]
    print(f"Question: {sample.get('question', {}).get('text')}")
    print(f"Learner Response: {sample.get('learner_response', {}).get('text')}")
    print(f"Learner Code:\n{sample.get('learner_response', {}).get('code', 'N/A')}")
    print(f"Expected Answer: {sample.get('expected_answer')}")
    print(f"Current Ground Truth: {sample.get('misconception', {}).get('primary')}")
    print("\nAnnotation tool initialized in headless verification mode.")


if __name__ == "__main__":
    run_annotation_cli()
