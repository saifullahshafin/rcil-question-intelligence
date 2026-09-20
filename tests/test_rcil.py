#!/usr/bin/env python3
"""
Automated Test Suite for RCIL
=============================
Runs unit and integration checks across all 5 layers.
"""

import unittest
from rcil import (
    triage_universal_task,
    run_universal_rcil,
    encode_universal_answers,
    rcil_bus,
)


class TestRCILFramework(unittest.TestCase):

    def test_layer0_autonomous_clearance(self):
        """Verify mechanical tasks proceed autonomously without questions."""
        res = triage_universal_task("Fix syntax error on line 42 of index.js")
        self.assertTrue(res["proceed_directly"])
        self.assertEqual(res["task_route"], "proceed_autonomously")
        self.assertLess(res["task_depth"], 0.8)

    def test_layer0_architecture_gating(self):
        """Verify deep tasks pause for human insight."""
        res = triage_universal_task("Design a fault-tolerant multi-region cluster for high frequency order book")
        self.assertFalse(res["proceed_directly"])
        self.assertEqual(res["task_route"], "extract_architecture_and_design")
        self.assertGreaterEqual(res["task_depth"], 0.8)

    def test_layer2_three_laws_and_cap(self):
        """Verify max 3 questions and quality score."""
        res = run_universal_rcil("Architect an enterprise microservice backend", verbose=False)
        self.assertEqual(res["status"], "QUESTIONS_PENDING")
        self.assertLessEqual(len(res["questions_for_human"]), 3)
        self.assertGreaterEqual(res["quality_score"], 1.0)

    def test_layer3_answer_encoding(self):
        """Verify natural language to typed parameter encoding."""
        q_asked = [{"id": "persistence_model"}, {"id": "api_and_communication"}]
        answers = {
            "persistence_model": "We must use PostgreSQL with relational tables and foreign keys.",
            "api_and_communication": "REST JSON endpoints with standard status codes."
        }
        encoded = encode_universal_answers(q_asked, answers)
        state = encoded["execution_state"]
        self.assertIn("persistence_model__persistence_engine", state)
        self.assertEqual(state["persistence_model__persistence_engine"], "postgresql_relational")
        self.assertEqual(state["api_and_communication__transport_protocol"], "rest_json")

    def test_cross_agent_bus(self):
        """Verify event broadcasting and update checks."""
        rcil_bus.register_agent("test_agent_a", "./test_a")
        rcil_bus.register_agent("test_agent_b", "./test_b")

        event = rcil_bus.broadcast_update(
            origin_agent="test_agent_a",
            event_type="CORE_SPEC_UPDATE",
            title="Unit Test Event",
            description="Testing bus dispatch."
        )
        self.assertGreater(event["event_id"], 0)

        has_up, pending = rcil_bus.check_updates("test_agent_b")
        self.assertTrue(has_up)
        self.assertTrue(any(e["event_id"] == event["event_id"] for e in pending))

        rcil_bus.ack_updates("test_agent_b", event["event_id"])
        has_up_after, _ = rcil_bus.check_updates("test_agent_b")
        self.assertFalse(has_up_after)


if __name__ == "__main__":
    unittest.main()
