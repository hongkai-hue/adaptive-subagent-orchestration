import hashlib
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "l3-handoff-cases.json"
PACKET_KEYS = {
    "handoff_version", "handoff_id", "ownership_epoch", "source_skill", "target_skill",
    "orchestrator_owner", "objective", "done_when", "non_goals", "constraints",
    "known_facts", "evidence_paths", "project_rules", "baseline_revision",
    "existing_changes", "sensitive_context", "required_manual_gates", "open_questions",
    "cancelled_adaptive_lanes",
}


def packet_digest(packet):
    content = {key: value for key, value in packet.items() if key != "handoff_id"}
    canonical = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class L3HandoffFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.cases = {case["id"]: case for case in cls.fixture["cases"]}

    def test_exact_envelope_and_required_case_ids(self):
        self.assertEqual({"schema_version", "handoff_version", "cases"}, set(self.fixture))
        self.assertEqual("1", self.fixture["schema_version"])
        self.assertEqual("l3-v1", self.fixture["handoff_version"])
        required = {
            "l3-valid-ready", "l3-missing-done-blocked", "l3-active-lane-cancel-first",
            "l3-sensitive-context-blocked", "l3-heavy-runtime-missing", "l3-overrides-d1",
            "l3-digest-mismatch-blocked", "l3-baseline-drift-needs-rework",
        }
        self.assertEqual(required, set(self.cases))

    def test_case_shape_and_owner_enums(self):
        for case in self.cases.values():
            self.assertEqual({"id", "kind", "packet", "traits", "expected"}, set(case))
            self.assertRegex(case["id"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertIn(case["kind"], {"routing", "contract", "safety"})
            self.assertEqual(len(case["traits"]), len(set(case["traits"])))
            self.assertEqual(
                {"state", "error_code", "adaptive_owner", "heavy_owner"},
                set(case["expected"]),
            )
            self.assertIn(case["expected"]["adaptive_owner"], {"active", "cancelling", "released", "none"})
            self.assertIn(case["expected"]["heavy_owner"], {"none", "pending", "active"})

    def test_ready_packets_are_exact_and_digest_valid(self):
        for case_id in ("l3-valid-ready", "l3-overrides-d1"):
            packet = self.cases[case_id]["packet"]
            self.assertEqual(PACKET_KEYS, set(packet))
            self.assertEqual(packet_digest(packet), packet["handoff_id"])
            self.assertEqual("minimized", packet["sensitive_context"]["status"])
            self.assertEqual("HANDOFF_READY", self.cases[case_id]["expected"]["state"])

    def test_negative_cases_fail_closed_with_frozen_outcomes(self):
        expected = {
            "l3-missing-done-blocked": ("HANDOFF_BLOCKED", "L3_PACKET_INVALID"),
            "l3-active-lane-cancel-first": ("CANCEL_THEN_HANDOFF", "L3_ADAPTIVE_OWNER_ACTIVE"),
            "l3-sensitive-context-blocked": ("HANDOFF_BLOCKED", "L3_SENSITIVE_CONTEXT"),
            "l3-heavy-runtime-missing": ("HANDOFF_BLOCKED", "L3_HEAVY_RUNTIME_MISSING"),
            "l3-digest-mismatch-blocked": ("HANDOFF_BLOCKED", "L3_PACKET_INVALID"),
            "l3-baseline-drift-needs-rework": ("HEAVY_NEEDS_REWORK", "L3_BASELINE_DRIFT"),
        }
        for case_id, outcome in expected.items():
            actual = self.cases[case_id]["expected"]
            self.assertEqual(outcome, (actual["state"], actual["error_code"]))
        mismatch = self.cases["l3-digest-mismatch-blocked"]["packet"]
        self.assertNotEqual(packet_digest(mismatch), mismatch["handoff_id"])


if __name__ == "__main__":
    unittest.main()
