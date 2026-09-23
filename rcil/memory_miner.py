#!/usr/bin/env python3
"""
Universal Question Intelligence Layer — Memory Miner (Layer 1)
==============================================================
Pulls project-specific context from:
  1. Obsaidy AST Knowledge Graph (via obsaidy.py query)
  2. Workspace rules (GEMINI.md, AGENTS.md, .agents/rules/)
  3. Git status / recent commit messages
  4. Project configuration manifests (package.json, pyproject.toml, docker-compose.yml)

The Non-Negotiable Memory Rule:
  NEVER ask the human director a question whose answer is already
  documented in the workspace.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

OBSAIDY_CLI = Path(r"C:\Users\HP\.gemini\tools\obsaidy.py")


def search_obsidian_system(workspace: Path, task_command: str) -> List[str]:
    """
    Priority 1: Searches the Obsidian System (Obsaidy AST Graph, Obsidian Vault notes, and Agent Wiki).
    Returns list of formatted memory fragments if found, or empty list if nothing matches.
    """
    obsidian_fragments = []

    # 1A. Query Obsaidy AST Graph (deterministic structural knowledge)
    if OBSAIDY_CLI.exists():
        try:
            res = subprocess.run(
                ["python", str(OBSAIDY_CLI), "query", task_command[:120]],
                cwd=str(workspace),
                capture_output=True, text=True, timeout=12
            )
            if res.returncode == 0 and res.stdout.strip():
                output = res.stdout.strip()
                if "nodes found" in output or "NODE " in output or "EDGE " in output:
                    obsidian_fragments.append(f"[Obsidian System - Obsaidy AST Graph]\n{output[:1800]}")
        except Exception:
            pass

    # 1B. Search Obsidian Vault Notes (.md files in graphify-out/obsidian and graphify-out/wiki)
    vault_dirs = [
        workspace / "graphify-out" / "obsidian",
        workspace / "graphify-out" / "wiki",
    ]

    stop_words = {
        "this", "that", "with", "from", "have", "make", "need", "should", "will", "what", "where",
        "when", "your", "more", "into", "some", "then", "them", "these", "those", "about", "using",
        "system", "built", "build", "there", "their", "here", "just", "like", "also", "want"
    }
    raw_words = [w.lower().strip(".,!?:;\"'()[]{}") for w in task_command.split()]
    search_keywords = [w for w in raw_words if len(w) >= 4 and w not in stop_words]

    if search_keywords:
        matching_notes = []
        for v_dir in vault_dirs:
            if not v_dir.exists():
                continue
            for md_file in v_dir.glob("*.md"):
                name_lower = md_file.name.lower()
                hits = sum(1 for kw in search_keywords if kw in name_lower)
                if hits > 0:
                    matching_notes.append((hits, md_file))

        matching_notes.sort(key=lambda x: x[0], reverse=True)
        for _, note_path in matching_notes[:4]:
            try:
                content = note_path.read_text(encoding="utf-8", errors="ignore")
                sample = "\n".join(content.splitlines()[:35])
                obsidian_fragments.append(f"[Obsidian System - Vault Note: {note_path.name}]\n{sample}")
            except Exception:
                pass

    return obsidian_fragments


def search_regular_memory(workspace: Path) -> List[str]:
    """
    Priority 2 (Fallback): Searches standard workspace files (Rules, Guides, Manifests)
    only when Obsidian System memory yields nothing.
    """
    regular_fragments = []

    # 1. Workspace Markdown Rules & Guides
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
                content = cand.read_text(encoding="utf-8", errors="ignore")
                sample = "\n".join(content.splitlines()[:40])
                regular_fragments.append(f"[Regular Memory - {cand.name}]\n{sample}")
            except Exception:
                pass

    # 2. Project Manifests (Package / Dependencies)
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
                content = mf.read_text(encoding="utf-8", errors="ignore")
                sample = "\n".join(content.splitlines()[:30])
                regular_fragments.append(f"[Regular Memory - {mf.name}]\n{sample}")
            except Exception:
                pass

    return regular_fragments


def extract_workspace_memory(workspace_path: Path, task_command: str) -> str:
    """
    Extract relevant context from the workspace before formulating questions.

    Priority Rule:
      1. ALWAYS prioritize searching the Obsidian System (Obsaidy AST Graph,
         Obsidian Vault notes, and Agent Wiki).
      2. If and only if NOT found in the Obsidian System, fallback to regular
         memory-based searching (Workspace rules, guides, configuration manifests).
    """
    workspace = Path(workspace_path).resolve()

    # Priority 1: Search Obsidian System
    obsidian_fragments = search_obsidian_system(workspace, task_command)
    if obsidian_fragments:
        return "\n\n---\n\n".join(obsidian_fragments)

    # Priority 2 (Fallback): Search Regular Memory
    regular_fragments = search_regular_memory(workspace)
    if regular_fragments:
        return "\n\n---\n\n".join(regular_fragments)

    return ""


def filter_answered_questions(candidate_questions: List[Dict[str, Any]], memory_text: str) -> List[Dict[str, Any]]:
    """
    Drops candidate questions whose target parameter or critical concept
    is already clearly documented in the workspace memory.
    """
    if not memory_text:
        return candidate_questions

    memory_lower = memory_text.lower()
    filtered = []

    for q in candidate_questions:
        qid = q.get("id", "").lower().replace("_", " ")
        critical_words = [w for w in q.get("why_critical", "").lower().split() if len(w) > 5]
        
        # Check if parameter name or critical keywords appear frequently in memory
        match_count = sum(1 for w in critical_words if w in memory_lower)
        if qid in memory_lower or match_count >= 3:
            # Documented! Skip asking the user
            continue
        filtered.append(q)

    return filtered


if __name__ == "__main__":
    mem = extract_workspace_memory(Path("."), "Add authentication layer")
    print(f"Memory extracted ({len(mem)} characters)")
