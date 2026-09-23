#!/usr/bin/env python3
"""
System One MCP Server (Model Context Protocol stdio server)
Exposes TypeSafe Jev System One decision primitives as native MCP tools to:
- OpenCode (via opencode mcp add)
- Google Antigravity (via mcp_config.json)
"""

import sys
import json
import os

# Import local or global system1_bridge
try:
    from system1_bridge import evaluate_state, ChoiceQuestion, ScoreQuestion, NoulQuestion
    from system1_holistic import hmo_step, run_holistic_audit, format_hmo_verdict_card
except ImportError:
    try:
        from .system1_bridge import evaluate_state, ChoiceQuestion, ScoreQuestion, NoulQuestion
        from .system1_holistic import hmo_step, run_holistic_audit, format_hmo_verdict_card
    except ImportError:
        sys.path.append(r"C:\Users\HP\.gemini\tools")
        from system1_bridge import evaluate_state, ChoiceQuestion, ScoreQuestion, NoulQuestion
        from system1_holistic import hmo_step, run_holistic_audit, format_hmo_verdict_card

def create_tools_manifest():
    return [
        {
            "name": "system1_choice",
            "description": "System One high-speed judgment to select exactly one option from an enumerated criteria set. Returns chosen label, confidence score, and probability distribution.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "The contextual text, code, or data to evaluate."
                    },
                    "instructions": {
                        "type": "string",
                        "description": "The question to answer about the state."
                    },
                    "criteria": {
                        "type": "object",
                        "description": "A dictionary mapping option labels to their descriptive definitions.",
                        "additionalProperties": { "type": "string" }
                    }
                },
                "required": ["state", "instructions", "criteria"]
            }
        },
        {
            "name": "system1_score",
            "description": "System One evaluation along an ordered ordinal rubric (e.g. urgency 0-2, risk 0-3). Returns integer level, label, and confidence.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "The context or text to evaluate."
                    },
                    "instructions": {
                        "type": "string",
                        "description": "The scoring question."
                    },
                    "criteria": {
                        "type": "array",
                        "items": { "type": "string" },
                        "description": "An ordered list of level descriptions from lowest to highest."
                    }
                },
                "required": ["state", "instructions", "criteria"]
            }
        },
        {
            "name": "system1_noul",
            "description": "System One binary probability evaluation. Returns probability (0.0 to 1.0) and boolean.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "state": {
                        "type": "string",
                        "description": "The context to evaluate."
                    },
                    "instructions": {
                        "type": "string",
                        "description": "The proposition to test for truth."
                    }
                },
                "required": ["state", "instructions"]
            }
        },
        {
            "name": "system1_video_eval",
            "description": "Evaluates YouTube video transcripts for signal-to-noise, virality, monetization opportunity, and content pillars in 80ms.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "transcript": {
                        "type": "string",
                        "description": "The transcript text of the video."
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional video title."
                    }
                },
                "required": ["transcript"]
            }
        },
        {
            "name": "system1_task_route",
            "description": "Evaluates an autonomous task for subsystem intent, security risk tier, stealth browser need, and human approval necessity.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "Description of the task to be executed."
                    }
                },
                "required": ["task_description"]
            }
        },
        {
            "name": "system1_hmo_step",
            "description": "One-line step progress checkpoint. Automatically triggers Holistic Meta-Observer (HMO) audits at 40-50% (Stage 1) and 60-70% (Stage 2) watermarks to arrest agent-human bias, echo chambers, and false completion.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task": { "type": "string", "description": "Original task description." },
                    "current_step": { "type": "integer", "description": "Current step number." },
                    "total_steps": { "type": "integer", "description": "Total estimated steps (default 10)." },
                    "progress_pct": { "type": "number", "description": "Explicit progress percentage 0.0 to 100.0." },
                    "step_summary": { "type": "string", "description": "Summary of current work done so far." },
                    "human_directives": { "type": "string", "description": "Any human assumptions or directives passed to the agent." }
                },
                "required": ["task", "current_step"]
            }
        },
        {
            "name": "system1_holistic_audit",
            "description": "On-demand third-person Holistic Meta-Observer (HMO) audit. Steps completely outside the execution loop to detect shared cognitive bias, XY problems, or false 100% completion.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task": { "type": "string", "description": "Original task description." },
                    "stage": { "type": "integer", "description": "Audit stage: 1 (40-50% Mid-flight bias) or 2 (60-70% Convergence)." },
                    "current_work": { "type": "string", "description": "Current implementation state or verification results." },
                    "human_directives": { "type": "string", "description": "Optional human inputs/assumptions." }
                },
                "required": ["task", "stage"]
            }
        }
    ]

def handle_tool_call(tool_name, arguments):
    if tool_name == "system1_choice":
        state = arguments.get("state", "")
        instructions = arguments.get("instructions", "")
        criteria = arguments.get("criteria", {})
        questions = { "decision": ChoiceQuestion(instructions, criteria) }
        res = evaluate_state(state, questions)
        return { "content": [{ "type": "text", "text": json.dumps(res, indent=2) }] }

    elif tool_name == "system1_score":
        state = arguments.get("state", "")
        instructions = arguments.get("instructions", "")
        criteria = arguments.get("criteria", [])
        questions = { "decision": ScoreQuestion(instructions, criteria) }
        res = evaluate_state(state, questions)
        return { "content": [{ "type": "text", "text": json.dumps(res, indent=2) }] }

    elif tool_name == "system1_noul":
        state = arguments.get("state", "")
        instructions = arguments.get("instructions", "")
        questions = { "decision": NoulQuestion(instructions) }
        res = evaluate_state(state, questions)
        return { "content": [{ "type": "text", "text": json.dumps(res, indent=2) }] }

    elif tool_name == "system1_video_eval":
        transcript = arguments.get("transcript", "")
        title = arguments.get("title", "")
        state = { "title": title, "transcript_sample": transcript[:12000] }
        questions = {
            "signal_to_noise": ScoreQuestion(
                "Evaluate the signal-to-noise ratio and depth of actionable value in `transcript_sample`.",
                [
                    "Low signal, generic filler, clickbait, or repeated beginner advice",
                    "Moderate signal, interesting insights but lacks immediate concrete execution steps",
                    "High signal, highly actionable tactical blueprint, rare case study, or proprietary framework"
                ]
            ),
            "content_pillar": ChoiceQuestion(
                "What is the primary operational category of this content?",
                {
                    "ai_architecture": "AI models, agent frameworks, LLM infrastructure, autonomous systems",
                    "client_acquisition": "High-ticket sales, lead generation, outreach pipelines, closing clients",
                    "video_and_viral_marketing": "Motion graphics, hooks, video formats, short-form algorithms",
                    "digital_business_model": "SaaS, micro-SaaS, agency structures, revenue blueprints",
                    "general_mindset": "Philosophy, productivity, habits, or non-technical discussion"
                }
            ),
            "has_monetizable_opportunity": NoulQuestion(
                "Does this content present an explicit side hustle, tool stack, or market gap that can be turned into a revenue-generating service?"
            )
        }
        res = evaluate_state(state, questions)
        return { "content": [{ "type": "text", "text": json.dumps(res, indent=2) }] }

    elif tool_name == "system1_task_route":
        task = arguments.get("task_description", "")
        state = { "task": task }
        questions = {
            "intent": ChoiceQuestion(
                "Which subsystem is required to execute `task`?",
                {
                    "phantom_research": "Requires stealth web search, DrissionPage browser, or scraping",
                    "code_engineering": "Requires code analysis, editing, git commit, or build execution",
                    "system_ops": "Requires bash commands, daemon checks, memory cleanup, or server maintenance",
                    "content_production": "Requires writing scripts, video briefs, or social media copy",
                    "direct_answer": "Factual question answerable with existing context"
                }
            ),
            "security_tier": ScoreQuestion(
                "What is the security risk of executing `task`?",
                [
                    "Read-only safe operation",
                    "Non-destructive state change or local file creation",
                    "Destructive command (file deletion, process termination, spending money, or public posting)"
                ]
            ),
            "requires_human_approval": NoulQuestion(
                "Should this task halt and request explicit confirmation before running?"
            )
        }
        res = evaluate_state(state, questions)
        return { "content": [{ "type": "text", "text": json.dumps(res, indent=2) }] }

    elif tool_name == "system1_hmo_step":
        task = arguments.get("task", "")
        current_step = arguments.get("current_step", 1)
        total_steps = arguments.get("total_steps", 10)
        progress_pct = arguments.get("progress_pct")
        step_summary = arguments.get("step_summary", "")
        human_directives = arguments.get("human_directives", "")
        
        step_res = hmo_step(
            task=task,
            current_step=current_step,
            total_steps=total_steps,
            progress_pct=progress_pct,
            step_summary=step_summary,
            human_directives=human_directives
        )
        return { "content": [{ "type": "text", "text": json.dumps(step_res, indent=2) }] }

    elif tool_name == "system1_holistic_audit":
        task = arguments.get("task", "")
        stage = arguments.get("stage", 1)
        current_work = arguments.get("current_work", "")
        human_directives = arguments.get("human_directives", "")
        
        audit_res = run_holistic_audit(
            task=task,
            stage=stage,
            current_work=current_work,
            human_directives=human_directives
        )
        card = format_hmo_verdict_card(audit_res, task, 45.0 if stage == 1 else 65.0)
        output_payload = {
            "verdict": audit_res,
            "verdict_card": card
        }
        return { "content": [{ "type": "text", "text": json.dumps(output_payload, indent=2) }] }

    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def run_stdio_server():
    """Main JSON-RPC 2.0 stdio server loop for MCP."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "system1-mcp-server",
                            "version": "1.0.0"
                        }
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "notifications/initialized":
                continue

            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": create_tools_manifest()
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            elif method == "tools/call":
                params = req.get("params", {})
                tool_name = params.get("name")
                args = params.get("arguments", {})
                try:
                    call_result = handle_tool_call(tool_name, args)
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "result": call_result
                    }
                except Exception as e:
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg_id,
                        "error": {
                            "code": -32000,
                            "message": str(e)
                        }
                    }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

            else:
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()

        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Server error: {e}"
                }
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    run_stdio_server()
