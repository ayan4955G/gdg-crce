"""NVIDIA NIM Nemotron client used as the primary diagnosis model."""
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class NvidiaNemotron:
    def __init__(self) -> None:
        self.api_key = os.getenv("NVIDIA_API_KEY", "").strip()
        self.model = os.getenv("NVIDIA_NEMOTRON_MODEL", "nvidia/nemotron-3.5-lightning-30b-a3b")
        self.endpoint = os.getenv(
            "NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1/chat/completions"
        )
        taxonomy_path = Path(__file__).resolve().parents[1] / "taxonomy" / "misconceptions.json"
        with taxonomy_path.open(encoding="utf-8") as taxonomy_file:
            taxonomy = json.load(taxonomy_file)
        self.misconceptions = taxonomy.get("misconceptions", [])
        self.valid_ids = {item["id"] for item in self.misconceptions}

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def diagnose(self, *, question: str, answer: str, reasoning: str, code: str,
                 expected_answer: str, deterministic_evidence: list[str]) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            print("[NVIDIA Nemotron] NVIDIA_API_KEY is not set or empty in environment. Skipping Nemotron diagnosis.", flush=True)
            return None

        taxonomy_compact = [
            {"id": item["id"], "name": item["name"]}
            for item in self.misconceptions
        ]

        user_data = {
            "question": question,
            "expected_answer": expected_answer,
            "learner_answer": answer,
            "learner_reasoning": reasoning,
            "learner_code": code,
            "deterministic_evidence": deterministic_evidence,
            "taxonomy": taxonomy_compact,
        }
        user_content = json.dumps(user_data, ensure_ascii=False)

        # Attempt 1: Allow reasoning with generous token budget
        result = self._call_api(
            system=(
                "You are the primary diagnostic engine for an introductory programming tutor. "
                "Diagnose the student response based strictly on the provided evidence and taxonomy.\n\n"
                "At the end of your response, output a single JSON object with this schema:\n"
                '{"status": "CORRECT"|"DIAGNOSED"|"INSUFFICIENT_EVIDENCE"|"UNKNOWN", '
                '"primary_id": "<taxonomy_id>"|"CORRECT"|"INSUFFICIENT_EVIDENCE"|"UNKNOWN", '
                '"confidence": 0.0-1.0, "summary": "short explanation", '
                '"evidence": ["observation1", "observation2"]}'
            ),
            user=user_content,
            max_tokens=4096,
        )

        if result is not None:
            parsed = self._extract_diagnosis(result)
            if parsed is not None:
                return parsed

        # Attempt 2: Minimal prompt that suppresses reasoning
        print("[NVIDIA Nemotron] Retrying with compact no-reasoning prompt...", flush=True)
        result = self._call_api(
            system=(
                "Output ONLY a JSON object. No thinking, no preamble. Start with '{'. "
                "Schema: {\"status\":\"DIAGNOSED\",\"primary_id\":\"P003\",\"confidence\":0.9,"
                "\"summary\":\"explanation\",\"evidence\":[\"obs1\"]}"
            ),
            user=user_content,
            max_tokens=600,
        )

        if result is not None:
            return self._extract_diagnosis(result)

        return None

    def _call_api(self, *, system: str, user: str, max_tokens: int) -> Optional[str]:
        """Make a single API call and return the content string, or None on failure."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.0,
            "max_tokens": max_tokens,
            # The classifier must return a parseable diagnosis, not a chain of
            # thought that consumes the response budget before the JSON answer.
            "chat_template_kwargs": {"enable_thinking": False},
        }
        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=90) as response:
                result = json.loads(response.read().decode("utf-8"))
            choice = result["choices"][0]
            finish = choice.get("finish_reason", "")
            content = choice["message"]["content"]
            if finish == "length":
                print(f"[NVIDIA Nemotron] Response truncated (finish_reason=length, {max_tokens} tokens)", flush=True)
            return content
        except HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore") if hasattr(e, "read") else ""
            print(f"[NVIDIA Nemotron HTTPError {e.code}] {e.reason}: {error_body}", flush=True)
        except URLError as e:
            print(f"[NVIDIA Nemotron URLError] Connection failed: {e.reason}", flush=True)
        except TimeoutError:
            print(f"[NVIDIA Nemotron Timeout] Request exceeded 90s timeout", flush=True)
        except Exception as e:
            print(f"[NVIDIA Nemotron Error] {type(e).__name__}: {e}", flush=True)
        return None

    def _extract_diagnosis(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract and validate a diagnosis JSON from model output text."""
        # Strip thinking tags and markdown fences
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        content = re.sub(r"```(?:json)?\s*|\s*```", "", content, flags=re.IGNORECASE)

        # Try to find valid diagnosis JSON objects, working backwards
        json_matches = list(re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content))
        for match in reversed(json_matches):
            try:
                parsed = json.loads(match.group(0))
                if "status" in parsed and "primary_id" in parsed:
                    return self._validate_diagnosis(parsed)
            except (json.JSONDecodeError, ValueError):
                continue

        # Fallback: greedy match for the last { ... } block
        greedy = re.search(r"\{[\s\S]*\}", content)
        if greedy:
            try:
                parsed = json.loads(greedy.group(0))
                if "status" in parsed and "primary_id" in parsed:
                    return self._validate_diagnosis(parsed)
            except (json.JSONDecodeError, ValueError):
                pass

        print(f"[NVIDIA Nemotron Error] No valid diagnosis JSON in output: {content[:300]}", flush=True)
        return None

    def _validate_diagnosis(self, parsed: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate and normalize a parsed diagnosis dict."""
        primary_id = str(parsed.get("primary_id", "")).strip().upper()
        status = str(parsed.get("status", "")).strip().upper()
        confidence = min(1.0, max(0.0, float(parsed.get("confidence", 0.0))))
        summary = str(parsed.get("summary", "")).strip()
        evidence = parsed.get("evidence", [])
        valid_statuses = {"CORRECT", "DIAGNOSED", "INSUFFICIENT_EVIDENCE", "UNKNOWN"}

        if (status not in valid_statuses or not summary or not isinstance(evidence, list)
                or (primary_id not in self.valid_ids and primary_id not in {"CORRECT", "INSUFFICIENT_EVIDENCE", "UNKNOWN"})
                or (status == "DIAGNOSED" and primary_id not in self.valid_ids)
                or (status != "DIAGNOSED" and primary_id != status)):
            print(f"[NVIDIA Nemotron Validation Failed] {parsed}", flush=True)
            return None

        label = next((item["name"] for item in self.misconceptions if item["id"] == primary_id), None)
        return {
            "status": status,
            "primary_id": primary_id,
            "primary_name": label,
            "confidence": confidence,
            "summary": summary,
            "evidence": [str(item).strip() for item in evidence if str(item).strip()][:4],
        }
