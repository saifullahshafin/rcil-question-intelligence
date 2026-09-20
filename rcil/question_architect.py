#!/usr/bin/env python3
"""
Universal Question Intelligence Layer — Question Architect (Layer 2 & 2.5)
==========================================================================
Selects, engineers, and quality-gates questions for software engineering,
architecture, DevOps, and multi-agent tasks.

Two Quality Gates:
  - Gate 2.5A: Structural Quality Gate (System One: MECE, Anchors, Memory)
  - Gate 2.5B: Holistic Third-Person Meta-Observer Gate (System One: XY-problem,
               missing dependencies, wrong tier, root unlock question)
"""

from typing import Dict, List, Any
from .system1_bridge import evaluate_state, ChoiceQuestion, ScoreQuestion, NoulQuestion


# ─────────────────────────────────────────────────────────────────────────────
# UNIVERSAL DOMAIN QUESTION BANKS
# ─────────────────────────────────────────────────────────────────────────────

ARCHITECTURE_QUESTIONS = [
    {
        "id": "persistence_model",
        "question": "What is the primary data persistence model for this feature? (Relational PostgreSQL/SQLite, Document NoSQL, In-Memory/Redis, or Ephemeral File-Based)?",
        "why_critical": "Determines transaction boundaries, schema design, and migration strategy.",
        "maps_to_decision": "database_selection_and_schema_design",
    },
    {
        "id": "api_and_communication",
        "question": "What communication contract is required? (REST/JSON HTTP endpoints, tRPC/GraphQL typed schema, gRPC Protobuf, or Event-Driven Pub/Sub)?",
        "why_critical": "Wrong API paradigm forces expensive transport rewrites across client and server.",
        "maps_to_decision": "transport_layer_and_serialization",
    },
    {
        "id": "state_and_concurrency",
        "question": "How should state and concurrency be handled? (Stateless horizontal scaling, centralized Redis lock, or optimistic database concurrency)?",
        "why_critical": "Prevents race conditions, distributed deadlocks, and stale state bugs.",
        "maps_to_decision": "concurrency_and_caching_strategy",
    },
    {
        "id": "auth_and_security",
        "question": "What authentication/authorization mechanism governs this? (Stateless JWT, HTTP-only session cookies, API Key header, or OAuth2)?",
        "why_critical": "Security boundary must be locked prior to writing routes or middleware.",
        "maps_to_decision": "security_and_middleware_architecture",
    },
]

REFERENCE_QUESTIONS = [
    {
        "id": "borrowed_dimension",
        "question": "When referencing this system/example, which specific dimension must be replicated? (Data schema, API ergonomics, visual UI design, CLI ergonomics, or performance)?",
        "why_critical": "References are ambiguous shortcuts; replicating the wrong attribute wastes hours.",
        "maps_to_decision": "paradigm_and_interface_selection",
    },
    {
        "id": "divergence_criteria",
        "question": "What should we explicitly NOT replicate from that reference? (e.g., 'same API style but NOT their heavy dependencies', 'same UI layout but light mode only')?",
        "why_critical": "Via Negativa: knowing what to subtract eliminates generative defaults and AI slop.",
        "maps_to_decision": "anti_pattern_boundary_rules",
    },
    {
        "id": "anchor_reference_url",
        "question": "Can you provide the exact repository link, documentation URL, or file path that best demonstrates the desired pattern?",
        "why_critical": "Concrete anchor prevents guessing and enables deterministic inspection.",
        "maps_to_decision": "reference_code_inspection",
    },
]

SCOPE_QUESTIONS = [
    {
        "id": "deliverable_tier",
        "question": "What is the expected deliverable tier? (Quick proof-of-concept prototype, robust internal tool, or mission-critical production service)?",
        "why_critical": "Dictates error handling rigor, test coverage, telemetry, and security constraints.",
        "maps_to_decision": "engineering_rigor_and_testing_tier",
    },
    {
        "id": "runtime_environment",
        "question": "What is the target execution environment? (Local Windows host, Docker container, remote Linux ARM instance, or browser runtime)?",
        "why_critical": "Determines path separators, shell commands, and binary compatibility.",
        "maps_to_decision": "deployment_and_os_toolchain",
    },
    {
        "id": "backward_compatibility",
        "question": "Must existing public APIs, CLI flags, or schema definitions remain strictly backward-compatible, or is a breaking upgrade permitted?",
        "why_critical": "Prevents breaking downstream callers and dependent services.",
        "maps_to_decision": "breaking_change_and_deprecation_policy",
    },
]

HIGH_RISK_QUESTIONS = [
    {
        "id": "data_loss_verification",
        "question": "This task involves destructive modifications (schema alterations, file deletions, or credential rotations). Has an active backup or snapshot been created?",
        "why_critical": "Irreversible data loss cannot be remediated after execution.",
        "maps_to_decision": "destructive_action_gating",
    },
    {
        "id": "rollback_procedure",
        "question": "Is there an explicit rollback plan or Git commit to revert to if the migration or deployment fails?",
        "why_critical": "Protects system availability during high-risk infrastructure operations.",
        "maps_to_decision": "rollback_safety_gate",
    },
    {
        "id": "explicit_human_token",
        "question": "Please confirm explicit authorization to proceed with this high-risk action (Type 'CONFIRM_DESTRUCTIVE_EXECUTION').",
        "why_critical": "System One gating invariant: autonomous execution is strictly prohibited for destructive changes.",
        "maps_to_decision": "human_escalation_authorization",
    },
]


def quality_gate_questions(proposed_questions: List[Dict[str, Any]], task_context: str) -> dict:
    questions_summary = "\n".join([
        f"Q{i+1}: [{q['id']}] {q['question']} | Target: {q.get('maps_to_decision', 'N/A')}"
        for i, q in enumerate(proposed_questions)
    ])

    state = {
        "task_context": task_context[:500],
        "proposed_questions": questions_summary,
        "question_count": len(proposed_questions),
    }

    gate_rubric = {
        "overall_quality": ScoreQuestion(
            instructions="Rate the diagnostic precision and necessity of these proposed questions for the engineering task.",
            criteria=[
                "Level 0: Questions are vague, obvious, or could be answered by standard best practices. Waste of human time.",
                "Level 1: Moderately useful, but some questions overlap or could be inferred from codebase files.",
                "Level 2: Surgically precise. Each question directly decides an unguessable architectural parameter.",
            ]
        ),
        "mece_violation": NoulQuestion(
            instructions="Do any of these questions overlap in meaning or address redundant decisions? True = violation detected."
        ),
        "answerable_without_human": NoulQuestion(
            instructions="Can any of these questions be answered by inspecting the codebase files, package.json, or rules? True = unnecessary question."
        ),
        "max_questions_respected": NoulQuestion(
            instructions="Are there 3 or fewer questions? True = within human focus constraints (<= 3)."
        ),
    }

    result = evaluate_state(state, gate_rubric)
    return result.get("answers", {})


def holistic_blind_spot_gate(
    task_command: str,
    route: str,
    proposed_questions: List[Dict[str, Any]],
    proposed_approach: str
) -> dict:
    questions_text = " | ".join([q["question"][:60] for q in proposed_questions])

    state = {
        "task_command": task_command,
        "route_chosen": route,
        "questions_being_asked": questions_text,
        "proposed_approach": proposed_approach[:400],
    }

    meta_rubric = {
        "holistic_blind_spot": ChoiceQuestion(
            instructions=(
                "Step COMPLETELY OUTSIDE the current loop. Looking at the full task, route, "
                "and questions from a third-person systems perspective, what hidden blind spot exists?"
            ),
            criteria={
                "missing_prerequisite_dependency": (
                    "A critical prerequisite does not exist (missing API keys, missing database connection, "
                    "missing source repository, uninstalled runtime). Questions about implementation are premature."
                ),
                "xy_problem_trap": (
                    "The user is asking how to implement a flawed or convoluted workaround (Y) "
                    "instead of addressing the actual underlying engineering problem (X)."
                ),
                "wrong_architectural_tier": (
                    "The agent is designing an over-engineered distributed architecture for a simple script, "
                    "or building an ephemeral script when production reliability is required."
                ),
                "destructive_scope_blindness": (
                    "The approach risks silently breaking existing consumers, deleting data, or introducing security holes."
                ),
                "no_blind_spot": (
                    "The approach is sound. The questions address the genuine root decisions."
                ),
            }
        ),
        "approach_fundamentally_sound": NoulQuestion(
            instructions="Is the agent solving the real problem rather than efficiently building the wrong solution?"
        ),
        "one_question_that_unlocks_everything": ChoiceQuestion(
            instructions=(
                "If ONLY ONE question could be presented to the human director to prevent "
                "the most rework and eliminate the most ambiguity, what is it?"
            ),
            criteria={
                "confirm_prerequisite_environment": (
                    "Are the prerequisite database, API credentials, and runtime environment already configured and accessible?"
                ),
                "confirm_core_business_outcome": (
                    "What is the single core business or technical outcome this implementation must guarantee?"
                ),
                "confirm_target_deliverable_format": (
                    "Is this a standalone script, a reusable library module, or a full-stack integrated service?"
                ),
                "confirm_destructive_authorization": (
                    "Do you authorize executing this destructive modification, and is there a verified backup?"
                ),
            }
        ),
    }

    result = evaluate_state(state, meta_rubric)
    answers = result.get("answers", {})

    blind_spot = answers.get("holistic_blind_spot", {}).get("choice", "no_blind_spot")
    sound = answers.get("approach_fundamentally_sound", {}).get("noul", 1.0) >= 0.5
    unlock_q = answers.get("one_question_that_unlocks_everything", {}).get("choice", "confirm_core_business_outcome")

    return {
        "holistic_blind_spot": blind_spot,
        "approach_fundamentally_sound": sound,
        "one_question_that_unlocks_everything": unlock_q,
        "requires_restructure": (blind_spot != "no_blind_spot") and (not sound),
        "raw": answers,
    }


def architect_universal_questions(
    triage_result: dict,
    project_memory: str = "",
    task_command: str = ""
) -> dict:
    route = triage_result.get("task_route", "proceed_autonomously")
    if triage_result.get("proceed_directly", False) and route == "proceed_autonomously":
        return {
            "questions_for_human": [],
            "quality_score": 2.0,
            "gate_passed": True,
            "skipped": True,
            "reason": "Task triage cleared for autonomous execution. Zero questions needed.",
        }

    bank_map = {
        "extract_architecture_and_design": ARCHITECTURE_QUESTIONS,
        "extract_reference_and_paradigms": REFERENCE_QUESTIONS,
        "extract_scope_and_tier":          SCOPE_QUESTIONS,
        "escalate_high_risk_destructive":  HIGH_RISK_QUESTIONS,
    }
    candidate_bank = bank_map.get(route, SCOPE_QUESTIONS)

    memory_lower = project_memory.lower()
    filtered = []
    for q in candidate_bank:
        qid = q["id"].lower().replace("_", " ")
        if qid not in memory_lower:
            filtered.append(q)

    selected_questions = filtered[:3]

    if not selected_questions:
        return {
            "questions_for_human": [],
            "quality_score": 2.0,
            "gate_passed": True,
            "skipped": True,
            "reason": "All relevant questions are already documented in project memory.",
        }

    context = f"Task: {task_command}\nRoute: {route}\nMemory: {project_memory[:250]}"
    structural_gate = quality_gate_questions(selected_questions, context)

    quality_score = structural_gate.get("overall_quality", {}).get("score", 1.5)
    mece_violation = structural_gate.get("mece_violation", {}).get("noul", 0.0) >= 0.5

    holistic_gate = holistic_blind_spot_gate(
        task_command=task_command,
        route=route,
        proposed_questions=selected_questions,
        proposed_approach=f"Execute {route} by asking {len(selected_questions)} questions."
    )

    if holistic_gate["requires_restructure"]:
        unlock_id = holistic_gate["one_question_that_unlocks_everything"]
        unlock_text = f"[Root Precondition] {unlock_id.replace('_', ' ').capitalize()}?"
        selected_questions = [{
            "id": unlock_id,
            "question": unlock_text,
            "why_critical": f"Holistic Meta-Observer detected blind spot: {holistic_gate['holistic_blind_spot']}.",
            "maps_to_decision": "root_prerequisite_resolution",
        }]

    return {
        "questions_for_human": selected_questions,
        "quality_score": quality_score,
        "gate_passed": (quality_score >= 1.0) and (not mece_violation),
        "mece_violation": mece_violation,
        "holistic_gate": holistic_gate,
        "skipped": False,
    }
