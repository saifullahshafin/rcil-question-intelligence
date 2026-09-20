#!/usr/bin/env python3
"""
System One Client Bridge
========================
Connects to TypeSafe Jev (direct API or OpenRouter fallback) for deterministic,
sub-100ms calibrated evaluations (Choice, Score, Noul).
"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, Optional, Union

TYPESAFE_DIRECT_URL = "https://api.typesafe.ai/v1/systemone"
OPENROUTER_DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"


def get_credentials() -> Dict[str, str]:
    """Retrieve API keys from environment or local .env file."""
    typesafe_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "").strip()

    # Fallback to local .env in current directory or user home
    candidate_paths = [
        Path(".env"),
        Path(__file__).parent / ".env",
        Path.home() / ".env",
        Path.home() / ".gemini" / "tools" / ".env",
    ]
    for env_path in candidate_paths:
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("TYPESAFE_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val and not typesafe_key:
                                typesafe_key = val
                        elif line.startswith("OPENROUTER_API_KEY="):
                            val = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if val and not openrouter_key:
                                openrouter_key = val
            except Exception:
                pass
        if typesafe_key and openrouter_key:
            break

    return {
        "typesafe_key": typesafe_key,
        "openrouter_key": openrouter_key,
    }


class ChoiceQuestion:
    """Classifies input into one option from an enumerated taxonomy."""
    def __init__(self, instructions: str, criteria: Dict[str, str]):
        self.instructions = instructions
        self.criteria = criteria

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "choice",
            "instructions": self.instructions,
            "criteria": self.criteria,
        }


class ScoreQuestion:
    """Evaluates continuous intensity across ordered levels."""
    def __init__(self, instructions: str, criteria: list):
        self.instructions = instructions
        self.criteria = criteria

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "score",
            "instructions": self.instructions,
            "criteria": self.criteria,
        }


class NoulQuestion:
    """Normalized binary probability judgment (0.0 to 1.0)."""
    def __init__(self, instructions: str):
        self.instructions = instructions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "noul",
            "instructions": self.instructions,
        }


def evaluate_state(
    state: Union[str, Dict[str, Any], list],
    questions: Dict[str, Any],
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a structured System One decision call against TypeSafe Jev.
    Fallback chain: Direct TypeSafe API -> OpenRouter Fallback.
    """
    creds = get_credentials()
    ts_key = creds["typesafe_key"]
    or_key = creds["openrouter_key"]

    if not ts_key and not or_key:
        raise ValueError(
            "System One Error: Neither TYPESAFE_API_KEY nor OPENROUTER_API_KEY is configured. "
            "Set TYPESAFE_API_KEY in environment or .env file."
        )

    # Format questions payload
    payload_questions = {}
    for q_id, q_obj in questions.items():
        if hasattr(q_obj, "to_dict"):
            payload_questions[q_id] = q_obj.to_dict()
        elif isinstance(q_obj, dict):
            payload_questions[q_id] = q_obj
        else:
            raise TypeError(f"Invalid question object for '{q_id}': {type(q_obj)}")

    # Attempt 1: TypeSafe Direct
    if ts_key:
        req_data = {
            "model": model or "jev-latest",
            "state": state,
            "questions": payload_questions,
        }
        json_bytes = json.dumps(req_data).encode("utf-8")
        req = urllib.request.Request(
            TYPESAFE_DIRECT_URL,
            data=json_bytes,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ts_key}",
                "User-Agent": "RCIL-SystemOne-Client/1.1",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if not or_key:
                raise RuntimeError(f"TypeSafe Direct call failed: {e}")

    # Attempt 2: OpenRouter Fallback
    if or_key:
        req_data = {
            "model": model or "typesafe/jev-1.13",
            "state": state,
            "questions": payload_questions,
        }
        json_bytes = json.dumps(req_data).encode("utf-8")
        req = urllib.request.Request(
            OPENROUTER_DECISIONS_URL,
            data=json_bytes,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {or_key}",
                "User-Agent": "RCIL-SystemOne-Client/1.1",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
            raise RuntimeError(f"OpenRouter Fallback HTTP status {resp.status}")

    raise RuntimeError("System One evaluation failed across all providers.")
