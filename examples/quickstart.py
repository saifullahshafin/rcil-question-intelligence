#!/usr/bin/env python3
"""
RCIL Quickstart Example
=======================
Demonstrates the 2-step loop:
  Step 1: Ingress triage + question generation
  Step 2: Natural language answer encoding + enriched execution
"""

import os
from rcil import run_universal_rcil

def main():
    task = "Design a high-throughput real-time payment gateway using distributed queues"

    print("--- STEP 1: INITIAL TASK INGRESS ---")
    step1 = run_universal_rcil(task, verbose=True)

    if step1["status"] == "QUESTIONS_PENDING":
        print("\n[Human Interaction Required]")
        for i, q in enumerate(step1["questions_for_human"]):
            print(f"  Q{i+1}: {q['question']}")

        print("\n--- STEP 2: HUMAN PROVIDES NATURAL LANGUAGE ANSWERS ---")
        mock_human_answers = {
            "persistence_model": "We must use PostgreSQL with strict ACID transactions because this is financial data.",
            "api_and_communication": "Event-driven architecture with Kafka or Redis Streams for decoupling.",
            "deliverable_tier": "Production-grade service with automated integration tests and zero data loss."
        }

        step2 = run_universal_rcil(task, user_answers=mock_human_answers, verbose=True)
        print("\n--- FINAL ENRICHED EXECUTION STATE ---")
        for k, v in step2["execution_state"].items():
            print(f"  {k}: {v}")

    elif step1["status"] == "AUTONOMOUS":
        print("Task cleared for autonomous execution with zero human interruptions.")

if __name__ == "__main__":
    main()
