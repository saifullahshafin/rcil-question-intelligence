#!/usr/bin/env python3
"""
Universal Question Intelligence Layer — Task Triage Gate (Layer 0)
===================================================================
Applies to any engineering, architecture, DevOps, or agentic task.
System One evaluates the task prompt and decides:
  - How deep / ambiguous is this task?
  - Should the agent proceed autonomously without interrupting the user?
  - Or is human insight required to avoid the Blind Execution Trap (AI Slop)?
"""

from typing import Dict, Any
from .system1_bridge import evaluate_state, ChoiceQuestion, ScoreQuestion, NoulQuestion


UNIVERSAL_TRIAGE_QUESTIONS = {
    "task_route": ChoiceQuestion(
        instructions=(
            "Given this software engineering, architecture, DevOps, or general agentic task, "
            "determine the correct execution route for the agent based on where ambiguity resides."
        ),
        criteria={
            "proceed_autonomously": (
                "Task is deterministic, self-contained, or has zero ambiguity: syntax fix, "
                "unit test addition, known stack trace fix, lint correction, or applying explicit instructions. "
                "Agent has all information needed and must NOT interrupt the user."
            ),
            "extract_architecture_and_design": (
                "Task requires fundamental system or software architecture decisions that cannot "
                "be inferred: monolith vs. microservices, SQL vs. NoSQL, state management pattern, "
                "sync vs. async messaging, or protocol choice (REST vs. GraphQL vs. gRPC)."
            ),
            "extract_reference_and_paradigms": (
                "Task references an external product, repository, or creator without full specificity "
                "(e.g., 'make it like Linear', 'use the Stripe payment pattern', 'build a dashboard like Grafana'). "
                "Agent must isolate which dimensions to replicate vs. which to diverge from."
            ),
            "extract_scope_and_tier": (
                "Task deliverable scope or quality tier is ambiguous: throwaway script vs. production-grade "
                "hardened library; ephemeral local storage vs. cloud persistent database; 5-minute prototype vs. long-term system."
            ),
            "escalate_high_risk_destructive": (
                "Task touches destructive actions, production database schema drop/migration, "
                "API billing/credentials, file deletions, or security authentication that requires explicit human authorization."
            ),
        }
    ),

    "task_depth": ScoreQuestion(
        instructions=(
            "Rate the technical, architectural, and strategic depth of this task — "
            "how much domain judgment and human mental model understanding is required?"
        ),
        criteria=[
            "Level 0: Surface-level mechanical task. Zero architectural judgment needed. "
                      "Agent executes autonomously with existing skills and code patterns.",
            "Level 1: Moderate engineering task. Needs project-specific context (stack, conventions) "
                      "which may already be documented in local project memory or AST graph.",
            "Level 2: Deep architectural or strategic task. Agent cannot guess without understanding "
                      "the human director's trade-offs, constraints, and long-term vision.",
        ]
    ),

    "has_previous_project_context": NoulQuestion(
        instructions=(
            "Does this task relate to an existing project, codebase, or repository with existing files, "
            "Obsaidy AST graphs, or documentation? If yes, memory mining must run before asking questions."
        )
    ),

    "is_iterative_refinement": NoulQuestion(
        instructions=(
            "Is this task a follow-up refinement, bug fix, or incremental tweak on something already "
            "built or reviewed, rather than building a new system from scratch?"
        )
    ),
}


def triage_universal_task(task_command: str, conversation_history: str = "", domain: str = "general_software") -> dict:
    state = {
        "task_command": task_command,
        "conversation_history_summary": conversation_history[:500],
        "domain": domain,
    }

    result = evaluate_state(state, UNIVERSAL_TRIAGE_QUESTIONS)
    answers = result.get("answers", {})

    route = answers.get("task_route", {}).get("choice", "proceed_autonomously")
    depth = answers.get("task_depth", {}).get("score", 0.0)
    has_context = answers.get("has_previous_project_context", {}).get("noul", 0.0) >= 0.5
    is_iterative = answers.get("is_iterative_refinement", {}).get("noul", 0.0) >= 0.5

    proceed_directly = (route == "proceed_autonomously") or (depth < 0.8) or is_iterative

    return {
        "task_route": route,
        "task_depth": depth,
        "has_previous_context": has_context,
        "is_iterative": is_iterative,
        "proceed_directly": proceed_directly,
        "route_confidence": answers.get("task_route", {}).get("confidence", 0.0),
        "raw": answers,
    }
