#!/usr/bin/env python3
"""
RCIL Universal Event & Communication Bus
=========================================
Connects all agents to a single, unified Question Intelligence Layer.
Enables cross-agent specification broadcasting, update notifications,
and multi-project synchronization.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

RCIL_HOME = Path(os.environ.get("RCIL_HOME", Path.home() / ".rcil"))
REGISTRY_FILE = RCIL_HOME / "registry.json"
EVENTS_FILE = RCIL_HOME / "events.jsonl"


def _ensure_paths():
    RCIL_HOME.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_FILE.exists():
        initial = {
            "version": "1.1.0",
            "last_updated": datetime.now().isoformat(),
            "agents": {}
        }
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(initial, f, indent=2)
    if not EVENTS_FILE.exists():
        EVENTS_FILE.touch()


def load_registry() -> dict:
    _ensure_paths()
    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"version": "1.1.0", "last_updated": datetime.now().isoformat(), "agents": {}}


def save_registry(registry: dict):
    _ensure_paths()
    registry["last_updated"] = datetime.now().isoformat()
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)


def register_agent(
    agent_id: str,
    project_path: str,
    domain: str = "general_software",
    custom_layer: bool = False,
    notes: str = ""
) -> dict:
    registry = load_registry()
    norm_path = str(Path(project_path).resolve())
    
    agent_entry = {
        "agent_id": agent_id,
        "project_path": norm_path,
        "domain": domain,
        "custom_layer": custom_layer,
        "notes": notes,
        "registered_at": registry.get("agents", {}).get(agent_id, {}).get("registered_at", datetime.now().isoformat()),
        "last_seen_at": datetime.now().isoformat(),
        "last_synced_event_id": registry.get("agents", {}).get(agent_id, {}).get("last_synced_event_id", 0)
    }
    
    registry.setdefault("agents", {})[agent_id] = agent_entry
    save_registry(registry)
    return agent_entry


def get_all_events() -> List[Dict[str, Any]]:
    _ensure_paths()
    events = []
    if not EVENTS_FILE.exists():
        return events
    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    except Exception:
        pass
    return events


def broadcast_update(
    origin_agent: str,
    event_type: str,
    title: str,
    description: str,
    version: str = "1.1.0",
    payload: Optional[Dict[str, Any]] = None
) -> dict:
    _ensure_paths()
    events = get_all_events()
    new_event_id = len(events) + 1

    event = {
        "event_id": new_event_id,
        "timestamp": datetime.now().isoformat(),
        "origin_agent": origin_agent,
        "event_type": event_type,
        "version": version,
        "title": title,
        "description": description,
        "payload": payload or {}
    }

    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    registry = load_registry()
    for ag_id, ag_info in registry.get("agents", {}).items():
        if ag_id == origin_agent:
            ag_info["last_synced_event_id"] = new_event_id
            continue
        p_path = Path(ag_info["project_path"])
        if p_path.exists() and p_path.is_dir():
            notify_file = p_path / ".rcil_notifications.json"
            try:
                notifications = []
                if notify_file.exists():
                    try:
                        notifications = json.loads(notify_file.read_text(encoding="utf-8"))
                    except Exception:
                        notifications = []
                notifications.append({
                    "event_id": new_event_id,
                    "timestamp": event["timestamp"],
                    "origin_agent": origin_agent,
                    "event_type": event_type,
                    "title": title,
                    "read": False
                })
                notify_file.write_text(json.dumps(notifications[-20:], indent=2), encoding="utf-8")
            except Exception:
                pass

    save_registry(registry)
    return event


def check_updates(agent_id_or_path: str) -> Tuple[bool, List[Dict[str, Any]]]:
    registry = load_registry()
    agents = registry.get("agents", {})
    
    target_agent_id = None
    if agent_id_or_path in agents:
        target_agent_id = agent_id_or_path
    else:
        norm_in = str(Path(agent_id_or_path).resolve())
        for ag_id, ag_info in agents.items():
            if str(Path(ag_info["project_path"]).resolve()) == norm_in:
                target_agent_id = ag_id
                break

    last_synced_id = 0
    if target_agent_id:
        last_synced_id = agents[target_agent_id].get("last_synced_event_id", 0)

    events = get_all_events()
    pending = [e for e in events if e["event_id"] > last_synced_id]
    return (len(pending) > 0, pending)


def ack_updates(agent_id_or_path: str, up_to_event_id: Optional[int] = None) -> int:
    registry = load_registry()
    agents = registry.get("agents", {})
    
    target_agent_id = None
    if agent_id_or_path in agents:
        target_agent_id = agent_id_or_path
    else:
        norm_in = str(Path(agent_id_or_path).resolve())
        for ag_id, ag_info in agents.items():
            if str(Path(ag_info["project_path"]).resolve()) == norm_in:
                target_agent_id = ag_id
                break

    events = get_all_events()
    latest_id = events[-1]["event_id"] if events else 0
    target_sync_id = up_to_event_id if up_to_event_id is not None else latest_id

    if target_agent_id and target_agent_id in agents:
        agents[target_agent_id]["last_synced_event_id"] = target_sync_id
        agents[target_agent_id]["last_seen_at"] = datetime.now().isoformat()
        save_registry(registry)
    return target_sync_id


def get_status_summary() -> dict:
    _ensure_paths()
    registry = load_registry()
    events = get_all_events()
    agents = registry.get("agents", {})

    return {
        "total_registered_agents": len(agents),
        "total_broadcast_events": len(events),
        "latest_event": events[-1] if events else None,
        "agents": {
            k: {
                "domain": v["domain"],
                "custom_layer": v["custom_layer"],
                "last_synced_event_id": v["last_synced_event_id"],
                "pending_updates": len(events) - v.get("last_synced_event_id", 0)
            }
            for k, v in agents.items()
        }
    }
