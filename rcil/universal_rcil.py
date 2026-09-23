#!/usr/bin/env python3
"""
Universal Recursive Contextual Intelligence Loop (RCIL) Orchestrator
=====================================================================
The central ingress middleware for the Google Antigravity, OpenCode,
and Hermes agent frameworks.

Before any agent executes a deep or ambiguous engineering task:
  1. Checks the RCIL Universal Bus for system updates
  2. Runs Layer 0 Task Triage (System One)
  3. Runs Layer 1 Memory Mining (Obsaidy AST graph + docs)
  4. Runs Layer 2 & 2.5 Question Architecture + Quality Gates
  5. Runs Layer 3 Human Answer Encoding into typed execution parameters

Usage:
    from rcil.universal_rcil import run_universal_rcil
    result = run_universal_rcil("Refactor authentication to support OAuth2 GitHub login")
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

TOOLS_DIR = Path(r"C:\Users\HP\.gemini\tools")
RCIL_DIR = TOOLS_DIR / "rcil"
for p in (TOOLS_DIR, RCIL_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import rcil_bus
from task_triage import triage_universal_task
from memory_miner import extract_workspace_memory
from question_architect import architect_universal_questions, format_for_antigravity_dialog
from answer_encoder import encode_universal_answers


def run_universal_rcil(
    task_command: str,
    workspace_path: Optional[str] = None,
    user_answers: Optional[Dict[str, str]] = None,
    domain: str = "software_engineering",
    verbose: bool = True
) -> dict:
    """
    Execute the Universal RCIL Loop.
    """
    ws = Path(workspace_path).resolve() if workspace_path else Path(".").resolve()

    if verbose:
        print(f"\n{'='*64}")
        print(f"  UNIVERSAL RCIL — Recursive Contextual Intelligence Loop")
        print(f"{'='*64}")

    # ── STEP 0: CHECK UNIVERSAL BUS UPDATES ──────────────────────────────────
    has_updates, pending = rcil_bus.check_updates(str(ws))
    if has_updates and verbose:
        print(f"\n[RCIL Bus Notice] {len(pending)} ecosystem update(s) available:")
        for ev in pending:
            print(f"  - [#{ev['event_id']}] {ev['event_type']} from {ev['origin_agent']}: {ev['title']}")

    # ── LAYER 0: TASK TRIAGE ──────────────────────────────────────────────────
    if verbose:
        print(f"\n[Layer 0] Running Task Triage on System One...")
    triage = triage_universal_task(task_command, domain=domain)
    
    if verbose:
        print(f"  Route    : {triage['task_route']} (conf: {triage['route_confidence']:.2f})")
        print(f"  Depth    : {triage['task_depth']:.2f} / 2.0")
        print(f"  Decision : {'AUTONOMOUS (Proceed directly)' if triage['proceed_directly'] else 'HUMAN INSIGHT REQUIRED'}")

    if triage["proceed_directly"] and not user_answers:
        if verbose:
            print(f"  [OK] Autonomous clearance. Zero questions presented.")
        return {
            "status": "AUTONOMOUS",
            "task_route": triage["task_route"],
            "task_depth": triage["task_depth"],
            "questions_for_human": [],
            "execution_state": {},
            "triage": triage,
        }

    # ── LAYER 1: MEMORY MINING ────────────────────────────────────────────────
    if verbose:
        print(f"\n[Layer 1] Mining memory (Prioritizing Obsidian System with regular fallback)...")
    memory_text = extract_workspace_memory(ws, task_command)
    if verbose:
        print(f"  Memory extracted: {len(memory_text)} chars")

    # ── LAYER 2 & 2.5: QUESTION ARCHITECTURE & DUAL QUALITY GATES ─────────────
    if user_answers is None:
        if verbose:
            print(f"\n[Layer 2 & 2.5] Question Architect & Dual Quality Gates running...")
        arch_res = architect_universal_questions(
            triage_result=triage,
            project_memory=memory_text,
            task_command=task_command
        )

        questions = arch_res.get("questions_for_human", [])
        if arch_res.get("skipped", False) or not questions:
            if verbose:
                print(f"  ✓ All candidate questions resolved from memory. Proceeding autonomously.")
            return {
                "status": "AUTONOMOUS",
                "task_route": triage["task_route"],
                "task_depth": triage["task_depth"],
                "questions_for_human": [],
                "execution_state": {},
                "triage": triage,
            }

        if verbose:
            print(f"  Quality Gate Score : {arch_res.get('quality_score', 0):.2f} / 2.0")
            print(f"  MECE Violation     : {arch_res.get('mece_violation', False)}")
            holistic = arch_res.get("holistic_gate", {})
            print(f"  Holistic Blind Spot: {holistic.get('holistic_blind_spot', 'none')}")
            print(f"\n[Layer 2] Questions cleared for human director ({len(questions)}):")
            for i, q in enumerate(questions):
                print(f"  Q{i+1}: {q['question']}")

        return {
            "status": "QUESTIONS_PENDING",
            "task_route": triage["task_route"],
            "task_depth": triage["task_depth"],
            "questions_for_human": questions,
            "dialog_questions": format_for_antigravity_dialog(questions),
            "quality_score": arch_res.get("quality_score", 1.5),
            "execution_state": {},
            "triage": triage,
        }

    # ── LAYER 3: ANSWER ENCODING ──────────────────────────────────────────────
    else:
        if verbose:
            print(f"\n[Layer 3] Parsing human answers into typed execution parameters...")
        arch_res = architect_universal_questions(
            triage_result=triage,
            project_memory=memory_text,
            task_command=task_command
        )
        questions_asked = arch_res.get("questions_for_human", [])
        encoded = encode_universal_answers(questions_asked, user_answers)

        if verbose:
            print(f"  Encoded {len(encoded['execution_state'])} typed parameters:")
            for k, v in encoded["execution_state"].items():
                print(f"    - {k}: {v}")
            print(f"\n[RCIL COMPLETE] Enriched state dispatched to execution.")

        return {
            "status": "READY_TO_EXECUTE",
            "task_route": triage["task_route"],
            "task_depth": triage["task_depth"],
            "questions_for_human": [],
            "execution_state": encoded["execution_state"],
            "triage": triage,
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Universal RCIL CLI")
    parser.add_argument("task", help="The engineering command or prompt")
    parser.add_argument("--dir", default=".", help="Workspace path")
    args = parser.parse_args()

    res = run_universal_rcil(args.task, workspace_path=args.dir, verbose=True)
    print(f"\nStatus: {res['status']}")
