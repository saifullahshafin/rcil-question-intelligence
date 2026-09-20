#!/usr/bin/env python3
"""
Universal Question Intelligence Layer — Memory Miner (Layer 1)
==============================================================
Pulls project-specific context from:
  1. Knowledge graph / AST tools (Obsaidy, tree-sitter, or code indexers)
  2. Workspace rules (GEMINI.md, AGENTS.md, docs/ARCHITECTURE.md)
  3. Git status / recent commit messages
  4. Project configuration manifests (package.json, pyproject.toml, docker-compose.yml)

The Non-Negotiable Memory Rule:
  NEVER ask the human director a question whose answer is already
  documented in the workspace.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any


def extract_workspace_memory(workspace_path: Path, task_command: str) -> str:
    workspace = Path(workspace_path).resolve()
    memory_fragments = []

    # 1. Query AST / Obsaidy CLI if available
    obsaidy_bin = shutil.which("obsaidy") or shutil.which("obsaidy.cmd")
    if not obsaidy_bin:
        # Check standard user home tools
        cand = Path.home() / ".gemini" / "tools" / "obsaidy.py"
        if cand.exists():
            obsaidy_bin = str(cand)

    if obsaidy_bin:
        try:
            cmd = ["python", obsaidy_bin, "query", task_command[:120]] if obsaidy_bin.endswith(".py") else [obsaidy_bin, "query", task_command[:120]]
            res = subprocess.run(cmd, cwd=str(workspace), capture_output=True, text=True, timeout=10)
            if res.returncode == 0 and res.stdout.strip():
                memory_fragments.append(f"[AST Memory Graph]\n{res.stdout.strip()[:1000]}")
        except Exception:
            pass

    # 2. Workspace Markdown Rules & Guides
    rule_candidates = [
        workspace / "GEMINI.md",
        workspace / "AGENTS.md",
        workspace / ".agents" / "AGENTS.md",
        workspace / "README.md",
        workspace / "docs" / "ARCHITECTURE.md",
        workspace / "docs" / "CURRENT_STATE.md",
    ]
    for cand in rule_candidates:
        if cand.exists():
            try:
                content = cand.read_text(encoding="utf-8")
                sample = "\n".join(content.splitlines()[:40])
                memory_fragments.append(f"[{cand.name}]\n{sample}")
            except Exception:
                pass

    # 3. Project Manifests
    manifest_candidates = [
        workspace / "package.json",
        workspace / "pyproject.toml",
        workspace / "requirements.txt",
        workspace / "Cargo.toml",
        workspace / "go.mod",
        workspace / "docker-compose.yml",
    ]
    for mf in manifest_candidates:
        if mf.exists():
            try:
                content = mf.read_text(encoding="utf-8")
                sample = "\n".join(content.splitlines()[:30])
                memory_fragments.append(f"[{mf.name}]\n{sample}")
            except Exception:
                pass

    return "\n\n---\n\n".join(memory_fragments) if memory_fragments else ""


def filter_answered_questions(candidate_questions: List[Dict[str, Any]], memory_text: str) -> List[Dict[str, Any]]:
    if not memory_text:
        return candidate_questions

    memory_lower = memory_text.lower()
    filtered = []

    for q in candidate_questions:
        qid = q.get("id", "").lower().replace("_", " ")
        critical_words = [w for w in q.get("why_critical", "").lower().split() if len(w) > 5]
        
        match_count = sum(1 for w in critical_words if w in memory_lower)
        if qid in memory_lower or match_count >= 3:
            continue
        filtered.append(q)

    return filtered
