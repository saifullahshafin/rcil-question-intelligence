#!/usr/bin/env python3
"""
Universal RCIL Command-Line Interface
"""

import sys
import json
import argparse
from pathlib import Path

from . import rcil_bus
from .universal_rcil import run_universal_rcil
from .task_triage import triage_universal_task


def main():
    parser = argparse.ArgumentParser(prog="rcil", description="Universal Question Intelligence Layer & Bus CLI")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    subparsers.add_parser("status", help="Display RCIL bus status and registered agents")
    subparsers.add_parser("demo", help="Run interactive zero-config walkthrough demo")
    p_bm = subparsers.add_parser("benchmark", help="Run token economics and latency benchmark")
    p_bm.add_argument("--steps", type=int, default=15, help="Number of decision steps")
    p_bm.add_argument("--live", action="store_true", help="Run against live TypeSafe Jev API")

    p_check = subparsers.add_parser("check", help="Check for pending system updates")
    p_check.add_argument("agent", nargs="?", default=".", help="Agent ID or workspace directory path")

    p_ack = subparsers.add_parser("ack", help="Acknowledge pending system updates")
    p_ack.add_argument("agent", nargs="?", default=".", help="Agent ID or workspace directory path")

    p_triage = subparsers.add_parser("triage", help="Run Layer 0 Task Triage")
    p_triage.add_argument("task", help="The engineering command or prompt")

    p_run = subparsers.add_parser("run", help="Run the full 5-Layer Universal RCIL Loop")
    p_run.add_argument("task", help="The engineering command or prompt")
    p_run.add_argument("--answers", help="JSON dictionary of user answers", default=None)
    p_run.add_argument("--dir", default=".", help="Workspace path")

    p_bc = subparsers.add_parser("broadcast", help="Broadcast an update event to all agents")
    p_bc.add_argument("--origin", required=True, help="Origin agent ID")
    p_bc.add_argument("--type", default="CORE_SPEC_UPDATE", help="Event type")
    p_bc.add_argument("--title", required=True, help="Update title")
    p_bc.add_argument("--desc", required=True, help="Update description")
    p_bc.add_argument("--ver", default="1.1.0", help="Version")

    args = parser.parse_args()

    if args.command == "demo":
        from .demo import run_interactive_demo
        run_interactive_demo()
    elif args.command == "benchmark":
        import benchmark
        benchmark.run_benchmark(steps=args.steps, use_live=args.live)
    elif args.command == "status":
        print(json.dumps(rcil_bus.get_status_summary(), indent=2))
    elif args.command == "check":
        has_up, pending = rcil_bus.check_updates(args.agent)
        print(f"Target: {args.agent}")
        print(f"Pending updates available: {has_up} ({len(pending)} total)")
        for ev in pending:
            print(f"  [#{ev['event_id']}] {ev['event_type']} from {ev['origin_agent']}: {ev['title']}")
    elif args.command == "ack":
        synced_id = rcil_bus.ack_updates(args.agent)
        print(f"Synced target '{args.agent}' up to event #{synced_id}.")
    elif args.command == "triage":
        res = triage_universal_task(args.task)
        print(json.dumps(res, indent=2))
    elif args.command == "run":
        answers = json.loads(args.answers) if args.answers else None
        res = run_universal_rcil(args.task, workspace_path=args.dir, user_answers=answers, verbose=True)
        print(f"\nFinal RCIL Status: {res['status']}")
    elif args.command == "broadcast":
        ev = rcil_bus.broadcast_update(args.origin, args.type, args.title, args.desc, args.ver)
        print(f"Broadcasted event #{ev['event_id']}: {ev['title']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
