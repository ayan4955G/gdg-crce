import json
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

class LearnerCognitiveModel:
    """
    Maintains the persistent cognitive profile for a learner:
    - Concept Mastery scores (probabilistic tracking via smoothed Bayesian updates)
    - Active and remediated misconception trajectories
    - Recurrence detection and intervention efficacy histories
    """

    CONCEPTS = [
        "variables",
        "loops",
        "conditionals",
        "conditionals_and_booleans",
        "functions_and_scope",
        "lists_and_indexing",
        "data_structures_and_state"
    ]

    def __init__(self, learner_id: str):
        self.learner_id = learner_id
        self.concepts: Dict[str, Dict[str, Any]] = {
            c: {
                "mastery": 0.50, # Initial prior
                "confidence": 0.40,
                "attempts": 0,
                "successes": 0,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            for c in self.CONCEPTS
        }
        self.misconceptions: Dict[str, Dict[str, Any]] = {}
        self.interaction_history: List[Dict[str, Any]] = []

    def record_interaction(
        self,
        question_id: str,
        concept: str,
        is_correct: bool,
        diagnosis_result: Dict[str, Any],
        evidence_summary: Optional[List[str]] = None
    ):
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # 1. Update Concept Mastery (Bayesian Knowledge update)
        if concept in self.concepts:
            c_data = self.concepts[concept]
            c_data["attempts"] += 1
            if is_correct:
                c_data["successes"] += 1
                # Increase mastery with learning step
                c_data["mastery"] = min(0.98, c_data["mastery"] + 0.12 * (1.0 - c_data["mastery"]))
            else:
                # Decrease mastery proportionally
                c_data["mastery"] = max(0.05, c_data["mastery"] - 0.15 * c_data["mastery"])

            # Increase certainty with number of attempts
            c_data["confidence"] = min(0.95, 0.40 + 0.08 * math.log(c_data["attempts"] + 1))
            c_data["last_updated"] = timestamp

        # 2. Update Misconception Tracking
        status = diagnosis_result.get("status")
        primary_misc = diagnosis_result.get("primary", {}).get("id")

        if status in ["DIAGNOSED", "AMBIGUOUS"] and primary_misc and primary_misc.startswith("P"):
            if primary_misc not in self.misconceptions:
                self.misconceptions[primary_misc] = {
                    "id": primary_misc,
                    "occurrences": 1,
                    "resolved": False,
                    "confidence": diagnosis_result["primary"].get("confidence", 0.8),
                    "first_diagnosed_at": timestamp,
                    "last_diagnosed_at": timestamp,
                    "reassessments": 0,
                    "interventions_received": 0
                }
            else:
                m_data = self.misconceptions[primary_misc]
                m_data["occurrences"] += 1
                m_data["resolved"] = False # Re-opened recurrence
                m_data["last_diagnosed_at"] = timestamp
                m_data["confidence"] = diagnosis_result["primary"].get("confidence", 0.8)

        # 3. Append to interaction history
        self.interaction_history.append({
            "timestamp": timestamp,
            "question_id": question_id,
            "concept": concept,
            "is_correct": is_correct,
            "status": status,
            "diagnosed_misconception": primary_misc,
            "evidence": evidence_summary or []
        })

    def record_resolution(
        self,
        misconception_id: str,
        resolution_result: Dict[str, Any]
    ):
        timestamp = datetime.utcnow().isoformat()
        status = resolution_result.get("status")
        is_resolved = (status == "LIKELY_RESOLVED")

        if misconception_id in self.misconceptions:
            m_data = self.misconceptions[misconception_id]
            m_data["reassessments"] += 1
            if is_resolved:
                m_data["resolved"] = True
                m_data["resolved_at"] = timestamp
                m_data["resolution_confidence"] = resolution_result.get("confidence", 0.90)

    def get_profile(self) -> Dict[str, Any]:
        """
        Returns clean, calibrated student profile without misleading false precision.
        """
        formatted_concepts = {}
        for c, v in self.concepts.items():
            formatted_concepts[c] = {
                "estimated_mastery": round(v["mastery"], 2),
                "mastery_percentage": int(round(v["mastery"] * 100)),
                "confidence_level": "High" if v["confidence"] > 0.8 else ("Medium" if v["confidence"] > 0.6 else "Low"),
                "attempts": v["attempts"],
                "successes": v["successes"]
            }

        return {
            "learner_id": self.learner_id,
            "concepts": formatted_concepts,
            "misconceptions": self.misconceptions,
            "total_interactions": len(self.interaction_history),
            "active_misconceptions_count": sum(1 for m in self.misconceptions.values() if not m.get("resolved", False)),
            "resolved_misconceptions_count": sum(1 for m in self.misconceptions.values() if m.get("resolved", False))
        }

if __name__ == "__main__":
    learner = LearnerCognitiveModel("L001")
    
    # 1. Learner struggles on loops (P003)
    learner.record_interaction(
        question_id="Q001",
        concept="loops",
        is_correct=False,
        diagnosis_result={"status": "DIAGNOSED", "primary": {"id": "P003", "confidence": 0.88}}
    )
    print("Profile after initial error:")
    print(json.dumps(learner.get_profile(), indent=2))

    # 2. Learner successfully completes transfer resolution
    learner.record_resolution(
        misconception_id="P003",
        resolution_result={"status": "LIKELY_RESOLVED", "confidence": 0.92}
    )
    print("Profile after resolution:")
    print(json.dumps(learner.get_profile(), indent=2))
