#!/usr/bin/env python3
"""
Cross-Agent Sync Example
========================
Demonstrates how multiple autonomous agents synchronize via the RCIL Universal Bus.
"""

from rcil import rcil_bus

def main():
    print("=== RCIL Cross-Agent Communication Bus ===")
    
    # 1. Register two agents
    rcil_bus.register_agent("backend_agent", "./backend", domain="backend_services")
    rcil_bus.register_agent("frontend_agent", "./frontend", domain="frontend_ui")
    
    # 2. Backend agent broadcasts an architectural specification update
    event = rcil_bus.broadcast_update(
        origin_agent="backend_agent",
        event_type="CORE_SPEC_UPDATE",
        title="Auth Token Format Upgraded to Ed25519 JWT",
        description="Backend upgraded token signing algorithm. Frontend must parse new claims.",
        version="1.2.0"
    )
    print(f"Broadcasted event #{event['event_id']} from {event['origin_agent']}: {event['title']}")

    # 3. Frontend agent checks for updates
    has_updates, pending = rcil_bus.check_updates("frontend_agent")
    print(f"\nFrontend Agent: Has pending updates? {has_updates} ({len(pending)} pending)")
    for ev in pending:
        print(f"  - Received: #{ev['event_id']} [{ev['event_type']}] {ev['title']}")

    # 4. Frontend agent acknowledges and syncs
    synced_id = rcil_bus.ack_updates("frontend_agent")
    print(f"Frontend Agent acknowledged up to event #{synced_id}.")

    # 5. Verify sync
    has_updates_now, _ = rcil_bus.check_updates("frontend_agent")
    print(f"Frontend Agent: Has pending updates now? {has_updates_now}")

if __name__ == "__main__":
    main()
