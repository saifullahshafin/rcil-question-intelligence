"""
RCIL — Recursive Contextual Intelligence Loop
Universal Question Intelligence Layer for Autonomous AI Agents.
Originated & Architected by Saifullah Shafin.
"""

from .system1_bridge import evaluate_state, ChoiceQuestion, ScoreQuestion, NoulQuestion
from .task_triage import triage_universal_task
from .memory_miner import extract_workspace_memory
from .question_architect import architect_universal_questions
from .answer_encoder import encode_universal_answers
from .universal_rcil import run_universal_rcil
from . import rcil_bus

__version__ = "1.1.0"

__all__ = [
    "evaluate_state",
    "ChoiceQuestion",
    "ScoreQuestion",
    "NoulQuestion",
    "triage_universal_task",
    "extract_workspace_memory",
    "architect_universal_questions",
    "encode_universal_answers",
    "run_universal_rcil",
    "rcil_bus",
]
