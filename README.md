# Recursive Contextual Intelligence Loop (RCIL)
## Universal Question Intelligence Layer & Cross-Agent Decision Architecture

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Architecture: RCIL](https://img.shields.io/badge/Architecture-RCIL_5--Layer-purple.svg)](docs/QUESTION_INTELLIGENCE_LAYER_RCIL_MASTER_SPECIFICATION.md)
[![Decision Engine: System One](https://img.shields.io/badge/System_One-TypeSafe_Jev-emerald.svg)](https://typesafe.ai)

> **Originator & System Architect:** Saifullah Shafin  
> **Target Systems:** Autonomous AI Agents (Google Antigravity, OpenCode, Hermes, AutoGPT, LangGraph)  
> **Version:** 1.1.0 (Production-Verified)

---

## 1. Executive Summary

Autonomous AI agents in real-world production environments suffer from two symmetric, catastrophic failure modes:

1. **Failure Mode A: The Blind Execution Trap (The AI Slop Generator)**  
   The agent assumes it knows everything, fills in unstated architectural, security, or creative ambiguities with generic generative averages, and rushes into execution. The result is wasted compute, broken database schemas, and AI slop.
2. **Failure Mode B: The Conversational Fatigue Trap (The Interrogation Loop)**  
   The agent freezes and bombards the human with 8 to 10 vague, trivial questions (*"What are your preferences?", "What style do you want?"*), exhausting the user and destroying the value of automation.

### The System One Mathematical Ceiling
Integrating typed decision layers like **System One (TypeSafe Jev)** provides sub-100ms, deterministic evaluations (`choice`, `score`, `noul`). However, an immutable mathematical law governs every decision engine:

$$\text{Quality of Decision} \le \text{Quality of Question Frame}$$

System One does not speak conversational natural language. It evaluates mathematical relationships between an input state and an explicit rubric. **If a generative LLM generates vague, overlapping questions, System One returns mathematically calibrated garbage.**

### The Solution: RCIL
The **Recursive Contextual Intelligence Loop (RCIL)** bridges this gap. It acts as mandatory pre-execution middleware that triages task depth, mines project memory, architectures surgical diagnostic questions, quality-gates them through an **Outer-Loop Third-Person Meta-Observer**, and encodes human conversational answers into typed machine parameters.

---

## 2. Universal Architecture

```
                                  USER COMMAND / TASK
                                           │
                                           ▼
 ┌───────────────────────────────────────────────────────────────────────────────────┐
 │ LAYER 0: UNIVERSAL TASK TRIAGE GATE (System One)                                  │
 │ • Is this mechanical bug-fix/syntax (Level 0) or architectural/strategic (Level 2)?│
 │ • Routes: proceed_autonomously | extract_architecture | extract_reference_pattern │
 │           extract_scope_and_tier | escalate_high_risk_destructive                │
 └─────────────────────────────────────────┬─────────────────────────────────────────┘
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
             [Proceed Autonomously]                 [Human Insight Needed]
            (Depth < 0.8 or Iterative)                        │
                        │                                     ▼
                        │          ┌─────────────────────────────────────────────────┐
                        │          │ LAYER 1: UNIVERSAL MEMORY MINING                │
                        │          │ • Knowledge Graphs, ASTs, and Workspace Docs    │
                        │          │ • Filter out anything already documented        │
                        │          └──────────────────────────┬──────────────────────┘
                        │                                     │
                        │                                     ▼
                        │          ┌─────────────────────────────────────────────────┐
                        │          │ LAYER 2: UNIVERSAL QUESTION ARCHITECT           │
                        │          │ • Pre-Engineered Diagnostic Batteries per route │
                        │          │ • Three Laws: MECE, Observable Anchors, Nouls   │
                        │          │ • Anti-Fatigue Hard Cap: Maximum 3 questions    │
                        │          └──────────────────────────┬──────────────────────┘
                        │                                     │
                        │                                     ▼
                        │          ┌─────────────────────────────────────────────────┐
                        │          │ LAYER 2.5A: SYSTEM ONE STRUCTURAL QUALITY GATE  │
                        │          │ • Score: Diagnostic precision (0.0 → 2.0)       │
                        │          │ • Noul: MECE violation check (zero redundancy)  │
                        │          │ • Noul: Answerable from memory check            │
                        │          └──────────────────────────┬──────────────────────┘
                        │                                     │
                        │                                     ▼
                        │          ┌─────────────────────────────────────────────────┐
                        │          │ LAYER 2.5B: HOLISTIC THIRD-PERSON OBSERVER GATE │
                        │          │ • Step OUTSIDE the engineering loop             │
                        │          │ • Catch: XY Problem, Missing Env/Creds, Scope   │
                        │          │ • If caught: Ask ONLY the Root Unlock Question  │
                        │          └──────────────────────────┬──────────────────────┘
                        │                                     │
                        │                    ┌────────────────┴────────────────┐
                        │                    │ Approach Sound                  │ Blind Spot Detected
                        │                    ▼                                 ▼
                        │          ┌────────────────────┐            ┌────────────────────┐
                        │          │ PRESENT TO HUMAN   │            │ RESTRUCTURE ROUTE  │
                        │          │ (Max 3 Questions)  │            │ Ask single root    │
                        │          └─────────┬──────────┘            │ unlock question    │
                        │                    │                       └─────────┬──────────┘
                        │                    │ (Human Answers in NL)           │
                        │                    ▼                                 │
                        │          ┌───────────────────────────────────────────┴┐
                        │          │ LAYER 3: UNIVERSAL BOSS ANSWER ENCODER     │
                        │          │ • Parses conversational natural language   │
                        │          │ • Encodes into typed engineering tokens    │
                        │          │ • Closes the human-to-machine loop         │
                        │          └─────────────────────┬──────────────────────┘
                        │                                │
                        ▼                                ▼
 ┌───────────────────────────────────────────────────────────────────────────────────┐
 │ LAYER 4: ENRICHED EXECUTION & DISPATCH                                            │
 │ • Feeds typed execution state into downstream tool runners & code generators      │
 │ • Zero guessing, zero hallucination, zero generic defaults                        │
 └───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The Five Core Architectural Layers

### Layer 0: Task Triage Gate
Classifies incoming prompts into 5 deterministic routes:
1. `proceed_autonomously`: Pure mechanical fixes, lint errors, syntax corrections, unit tests.
2. `extract_architecture_and_design`: Database choice, API paradigms, concurrency, auth models.
3. `extract_reference_and_paradigms`: Emulating an external system (*"Make it like Linear"*). Isolates dimensions to copy vs. diverge from.
4. `extract_scope_and_tier`: Prototype vs. production-hardened service; local vs. cloud runtime.
5. `escalate_high_risk_destructive`: Schema alterations, deletions, external billings, auth rotation.

### Layer 1: Memory Mining
Before asking any question, the agent mines local knowledge graphs (Obsaidy / AST), project rules (`GEMINI.md`, `AGENTS.md`), and manifests (`package.json`, `pyproject.toml`).  
**The Non-Negotiable Rule:** Never ask the human a question whose answer is already documented in the workspace.

### Layer 2: Question Architecture & Domain Banks
Enforces the **Three Laws of Question Engineering**:
1. **The MECE Law:** Mutually Exclusive, Collectively Exhaustive option taxonomies.
2. **The Anchor Law:** Rubrics must map to concrete observable phenomena, not subjective adjectives.
3. **The Falsifiability Law:** Questions must be objective; every answer must directly change code execution.
*Constraint:* **Maximum 3 questions** per interaction to eliminate conversational fatigue.

### Layer 2.5: The Dual Quality Gates
- **Gate 2.5A (Structural Gate):** System One evaluates diagnostic precision ($0.0 \to 2.0$), MECE violations, and memory answerability.
- **Gate 2.5B (Holistic Third-Person Meta-Observer Gate):** Steps completely outside the recursive loop to detect structural blind spots:
  - `missing_prerequisite_dependency`
  - `xy_problem_trap`
  - `wrong_architectural_tier`
  - `destructive_scope_blindness`
  If a blind spot is found, it intercepts and asks the single **`one_question_that_unlocks_everything`**.

### Layer 3: Boss Answer Encoder
Converts natural language, colloquial responses (*"We need high write speed and don't care about immediate consistency"*) into typed machine parameters:
```json
{
  "persistence_model__persistence_engine": "redis_in_memory",
  "persistence_model__strict_consistency_required": 0.05,
  "api_and_communication__transport_protocol": "grpc_protobuf"
}
```

---

## 4. Cross-Agent Universal Communication Bus

RCIL includes an event-driven synchronization bus allowing heterogeneous agents (Coding, DevOps, Video Editing, Multimodal) to:
- Broadcast specification updates and newly learned blind-spot patterns.
- Notify all registered workspace projects of system updates.
- Check and acknowledge pending updates on session ingress.

```bash
# Check updates for current project
rcil check

# Acknowledge updates
rcil ack

# Broadcast an update to all agents
rcil broadcast --origin main_system --type CORE_SPEC_UPDATE --title "Title" --desc "Description"
```

---

## 5. Installation & Quickstart

### Installation
```bash
git clone https://github.com/saifullahshafin/rcil-question-intelligence.git
cd rcil-question-intelligence
pip install -e .
```

### Environment Configuration
Configure your System One API credentials (copy `.env.example` to `.env`):
```bash
# TypeSafe Jev (Primary)
TYPESAFE_API_KEY=your_typesafe_api_key_here

# OpenRouter Decisions (Fallback)
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Python API Usage
```python
from rcil import run_universal_rcil

task = "Design a high-availability event sourcing system for banking transactions"

# Step 1: Pre-flight check and diagnostic question formulation
result = run_universal_rcil(task)

if result["status"] == "QUESTIONS_PENDING":
    for q in result["questions_for_human"]:
        print(f"Question: {q['question']}")

    # Step 2: Answer encoding
    answers = {
        "persistence_model": "PostgreSQL with strict ACID transactions",
        "api_and_communication": "Event-driven architecture with Kafka"
    }
    execution = run_universal_rcil(task, user_answers=answers)
    print("Typed Execution State:", execution["execution_state"])
```

### CLI Usage
```bash
# Triage a task
rcil triage "Fix typo on line 42"

# Run full loop
rcil run "Architect real-time stock ticker pipeline"

# Inspect status of registered ecosystem agents
rcil status
```

---

## 6. Running Tests

```bash
python -m unittest discover tests
```

---

## 7. License

Released under the [MIT License](LICENSE).  
Copyright (c) 2026 Saifullah Shafin.
