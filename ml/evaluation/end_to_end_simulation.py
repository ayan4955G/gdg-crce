import os
import sys
import json
sys.path.insert(0, os.path.abspath("."))

from ml.models.hybrid_diagnoser import HybridMisconceptionDiagnoser
from ml.models.intervention_engine import InterventionEngine
from ml.models.resolution_model import IndependentResolutionAssessor
from ml.models.learner_model import LearnerCognitiveModel

def run_simulation():
    print("=" * 75)
    print("          RE:LEARN END-TO-END MULTI-LEARNER LIFECYCLE SIMULATION")
    print("=" * 75)

    diagnoser = HybridMisconceptionDiagnoser()
    intervention_engine = InterventionEngine()
    resolution_assessor = IndependentResolutionAssessor(diagnoser=diagnoser)

    learners_config = [
        {
            "id": "LEARNER_A",
            "name": "Alex (Loop Boundary / Off-by-One - P003)",
            "initial_question": {
                "id": "Q_LOOP_01",
                "text": "What does for i in range(1, 5) print?",
                "expected": "1 2 3 4",
                "code": "for i in range(1, 5):\n    print(i, end=' ')",
                "student_answer": "1 2 3 4 5",
                "reasoning": "range(1, 5) starts at 1 and stops at 5 inclusive, so it prints 1 2 3 4 5."
            },
            "concept": "loops",
            "target_misc": "P003",
            "transfer_attempts": [
                {
                    "question_type": "isomorphic",
                    "question_text": "What does for i in range(2, 6) print?",
                    "expected_answer": "2 3 4 5",
                    "student_answer": "2 3 4 5",
                    "reasoning": "range(2, 6) starts at 2 and stops strictly before 6, so 2, 3, 4, 5.",
                    "code": "for i in range(2, 6):\n    print(i, end=' ')"
                },
                {
                    "question_type": "transfer",
                    "question_text": "How many times does while i < 5 iterate starting from i = 0?",
                    "expected_answer": "5",
                    "student_answer": "5",
                    "reasoning": "i takes values 0, 1, 2, 3, 4. When i is 5, 5 < 5 is False and it halts (5 total).",
                    "code": "i = 0\nwhile i < 5:\n    i += 1"
                }
            ]
        },
        {
            "id": "LEARNER_B",
            "name": "Blake (Boolean Operator Misunderstanding - P006)",
            "initial_question": {
                "id": "Q_BOOL_01",
                "text": "What does this print?\nx = 3\nif x == 1 or 2: print('Match')",
                "expected": "Match",
                "code": "x = 3\nif x == 1 or 2:\n    print('Match')\nelse:\n    print('No Match')",
                "student_answer": "No Match",
                "reasoning": "x is 3 so it neither equals 1 nor 2, so the condition fails."
            },
            "concept": "conditionals_and_booleans",
            "target_misc": "P006",
            "transfer_attempts": [
                {
                    "question_type": "isomorphic",
                    "question_text": "What does 'x == 'a' or 'b'' evaluate to for x = 'c'?",
                    "expected_answer": "'b'",
                    "student_answer": "True",
                    "reasoning": "Because 'b' is a non-empty string and thus truthy, the or expression evaluates to True.",
                    "code": "x = 'c'\nres = bool(x == 'a' or 'b')"
                },
                {
                    "question_type": "transfer",
                    "question_text": "How do you check if score is between 10 and 20?",
                    "expected_answer": "score >= 10 and score <= 20",
                    "student_answer": "score >= 10 and score <= 20",
                    "reasoning": "Both relational tests must be joined by 'and' because a single number must satisfy both bounds.",
                    "code": "valid = score >= 10 and score <= 20"
                }
            ]
        },
        {
            "id": "LEARNER_C",
            "name": "Casey (Return vs Print Confusion - P007)",
            "initial_question": {
                "id": "Q_FUNC_01",
                "text": "What is the output of print(res)?\ndef add(a, b): print(a + b)\nres = add(2, 3)\nprint(res)",
                "expected": "5\nNone",
                "code": "def add(a, b):\n    print(a + b)\nres = add(2, 3)\nprint(res)",
                "student_answer": "5\n5",
                "reasoning": "The function printed 5, so res holds 5."
            },
            "concept": "functions_and_scope",
            "target_misc": "P007",
            "transfer_attempts": [
                {
                    "question_type": "isomorphic",
                    "question_text": "What is in 'val' if def multiply(x): print(x*2)? val = multiply(4)",
                    "expected_answer": "None",
                    "student_answer": "None",
                    "reasoning": "print only sends text to console; without return, Python assigns None to val.",
                    "code": "def multiply(x):\n    print(x*2)\nval = multiply(4)"
                },
                {
                    "question_type": "transfer",
                    "question_text": "How do you pass data from helper() to caller?",
                    "expected_answer": "return",
                    "student_answer": "return",
                    "reasoning": "A return statement transmits data back into caller variables for computation.",
                    "code": "def helper():\n    return 42"
                }
            ]
        }
    ]

    all_traces = []

    for l_cfg in learners_config:
        print(f"\n===========================================================================")
        print(f">> SIMULATING LEARNER: {l_cfg['name']}")
        print(f"===========================================================================")
        profile = LearnerCognitiveModel(l_cfg["id"])
        init_q = l_cfg["initial_question"]

        # Step 1: Initial Question Response & Diagnosis
        print(f"\n[Step 1] Student receives question: '{init_q['text'].splitlines()[0]}'")
        print(f"         Student submitted answer: '{init_q['student_answer']}'")
        print(f"         Student reasoning: '{init_q['reasoning']}'")

        diag = diagnoser.diagnose(
            question_id=init_q["id"],
            question_text=init_q["text"],
            student_answer=init_q["student_answer"],
            reasoning=init_q["reasoning"],
            code=init_q["code"],
            expected_answer=init_q["expected"]
        )
        print(f"\n[Step 2] Re:Learn Diagnostic Inference:")
        print(f"         Status: {diag['status']}")
        print(f"         Diagnosed: {diag['primary']['id']} (Confidence: {diag['primary']['confidence']})")
        print(f"         Evidence Extracted: {diag['evidence']}")

        # Record in learner model
        profile.record_interaction(
            question_id=init_q["id"],
            concept=l_cfg["concept"],
            is_correct=False,
            diagnosis_result=diag,
            evidence_summary=diag["evidence"]
        )
        print(f"         Initial Concept Mastery ({l_cfg['concept']}): {profile.get_profile()['concepts'][l_cfg['concept']]['estimated_mastery']}")

        # Step 3: Targeted Pedagogical Intervention
        intervention = intervention_engine.generate_intervention(
            misconception_id=diag["primary"]["id"],
            learner_response=init_q["student_answer"]
        )
        print(f"\n[Step 3] Targeted Scaffolding Generated (Type: {intervention['type']}):")
        print(f"         Scaffolding: {intervention['content'][:110]}...")
        print(f"         Pedagogical Follow-up: {intervention['follow_up_question']}")

        # Step 4 & 5: Transfer Reassessment & Independent Resolution
        print(f"\n[Step 4] Presenting Novel Transfer Battery ({len(l_cfg['transfer_attempts'])} problems)...")
        resolution = resolution_assessor.assess_resolution(
            misconception_id=diag["primary"]["id"],
            attempts=l_cfg["transfer_attempts"]
        )
        print(f"\n[Step 5] Independent Resolution Assessment:")
        print(f"         Resolution Status: {resolution['status']}")
        print(f"         Remediation Confidence: {resolution['confidence']}")
        print(f"         Evidence Breakdown: {resolution['evidence']}")
        print(f"         Summary: {resolution['summary']}")

        # Step 6: Final Cognitive State Update
        profile.record_resolution(diag["primary"]["id"], resolution)
        # Update concept mastery after successful transfer
        profile.record_interaction(
            question_id="TRANSFER_Q",
            concept=l_cfg["concept"],
            is_correct=True,
            diagnosis_result={"status": "CORRECT", "primary": {"id": "CORRECT"}}
        )
        final_profile = profile.get_profile()
        final_mastery = final_profile["concepts"][l_cfg["concept"]]["estimated_mastery"]
        print(f"\n[Step 6] Final Learner Cognitive State:")
        print(f"         Updated Mastery for {l_cfg['concept']}: {final_mastery} (Status: {final_profile['concepts'][l_cfg['concept']]['confidence_level']} confidence)")
        print(f"         Misconception {diag['primary']['id']} Resolved: {final_profile['misconceptions'][diag['primary']['id']]['resolved']}")

        all_traces.append({
            "learner_id": l_cfg["id"],
            "target_misconception": l_cfg["target_misc"],
            "diagnosis": diag,
            "intervention": intervention,
            "resolution": resolution,
            "final_profile": final_profile
        })

    os.makedirs("docs", exist_ok=True)
    with open("docs/end_to_end_simulation_traces.json", "w", encoding="utf-8") as f:
        json.dump(all_traces, f, indent=2)

    print("\n" + "=" * 75)
    print("[OK] Complete end-to-end simulation traces written to docs/end_to_end_simulation_traces.json")

if __name__ == "__main__":
    run_simulation()
