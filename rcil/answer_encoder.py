#!/usr/bin/env python3
"""
Universal Question Intelligence Layer — Answer Encoder (Layer 3)
================================================================
Parses the human director's natural language responses into typed,
calibrated machine parameters using System One.
"""

from typing import Dict, List, Any
from .system1_bridge import evaluate_state, ChoiceQuestion, ScoreQuestion, NoulQuestion


def encode_persistence_answer(answer_text: str) -> dict:
    state = {"human_answer_about_persistence": answer_text}
    questions = {
        "persistence_engine": ChoiceQuestion(
            instructions="Based on the answer, which database / persistence engine matches the intent?",
            criteria={
                "postgresql_relational": "PostgreSQL / relational SQL with ACID transactions",
                "sqlite_embedded":       "SQLite / local embedded relational file",
                "nosql_document":        "MongoDB / Document NoSQL flexible schema",
                "redis_in_memory":       "Redis / in-memory key-value cache or fast pub-sub",
                "filesystem_json":       "Simple JSON / YAML / text files on local disk",
            }
        ),
        "strict_consistency_required": NoulQuestion(
            instructions="Did the human indicate that strict ACID transaction consistency is mandatory?"
        ),
    }
    res = evaluate_state(state, questions)
    return res.get("answers", {})


def encode_api_contract_answer(answer_text: str) -> dict:
    state = {"human_answer_about_api": answer_text}
    questions = {
        "transport_protocol": ChoiceQuestion(
            instructions="Which API communication protocol applies?",
            criteria={
                "rest_json":          "Standard RESTful HTTP endpoints with JSON payloads",
                "trpc_or_graphql":    "End-to-end type-safe RPC (tRPC) or GraphQL schema",
                "grpc_protobuf":      "High-throughput binary gRPC / Protobuf",
                "event_driven_queue": "Asynchronous event queues (RabbitMQ, Kafka, Redis Streams)",
                "local_function_call":"Direct in-process function / library call (no network)",
            }
        )
    }
    res = evaluate_state(state, questions)
    return res.get("answers", {})


def encode_deliverable_tier_answer(answer_text: str) -> dict:
    state = {"human_answer_about_tier": answer_text}
    questions = {
        "engineering_tier": ChoiceQuestion(
            instructions="What engineering deliverable tier was specified?",
            criteria={
                "prototype_speed_first": "Quick prototype / POC. Speed is top priority; skip exhaustive tests and telemetry.",
                "robust_internal_tool":  "Internal tool / CLI. Needs clean error handling and usability, but not 99.99% high availability.",
                "production_service":    "Production grade. Requires defensive validation, unit/integration tests, logging, and security.",
            }
        ),
        "target_os_runtime": ChoiceQuestion(
            instructions="Which runtime environment was specified or implied?",
            criteria={
                "local_windows": "Windows PowerShell / local desktop environment",
                "docker_linux":  "Linux Docker container / Linux VM",
                "remote_arm_vps":"Remote ARM / Cloud VPS instance",
                "browser_web":   "Web browser / frontend runtime",
            }
        )
    }
    res = evaluate_state(state, questions)
    return res.get("answers", {})


def encode_risk_authorization_answer(answer_text: str) -> dict:
    state = {"human_answer_about_risk": answer_text}
    questions = {
        "explicitly_authorized": NoulQuestion(
            instructions="Did the human give explicit, unambiguous permission to execute the destructive action or schema change?"
        ),
        "backup_confirmed": NoulQuestion(
            instructions="Did the human confirm that a backup, snapshot, or safe revert commit exists?"
        ),
    }
    res = evaluate_state(state, questions)
    return res.get("answers", {})


ENCODER_ROUTING = {
    "persistence_model":       encode_persistence_answer,
    "api_and_communication":   encode_api_contract_answer,
    "deliverable_tier":        encode_deliverable_tier_answer,
    "data_loss_verification":  encode_risk_authorization_answer,
    "explicit_human_token":    encode_risk_authorization_answer,
}


def encode_universal_answers(questions_asked: List[Dict[str, Any]], user_answers: Dict[str, str]) -> dict:
    execution_state = {}
    raw_evaluations = {}

    for q in questions_asked:
        qid = q.get("id", "")
        answer = user_answers.get(qid, "")
        if not answer:
            continue

        encoder = ENCODER_ROUTING.get(qid)
        if encoder:
            try:
                eval_res = encoder(answer)
                raw_evaluations[qid] = eval_res
                for k, v in eval_res.items():
                    if isinstance(v, dict):
                        val = v.get("choice") if v.get("choice") is not None else (
                            v.get("score") if v.get("score") is not None else v.get("noul")
                        )
                        execution_state[f"{qid}__{k}"] = val
                    else:
                        execution_state[f"{qid}__{k}"] = v
            except Exception as e:
                execution_state[f"{qid}__error"] = str(e)
        else:
            execution_state[f"{qid}__raw_answer"] = answer

    return {
        "execution_state": execution_state,
        "raw_evaluations": raw_evaluations,
        "encoded_keys": list(execution_state.keys()),
    }
