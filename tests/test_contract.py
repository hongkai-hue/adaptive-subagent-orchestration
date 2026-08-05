import json
import os
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_VALUE = os.environ.get("ADAPTIVE_SKILL_RUNTIME")
RUNTIME = Path(RUNTIME_VALUE).expanduser() if RUNTIME_VALUE else None
SKILL = ROOT / "SKILL.md"
OPENAI_YAML = ROOT / "agents" / "openai.yaml"
FIXTURES = ROOT / "tests" / "fixtures" / "forward-cases.json"


class SkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill_text = SKILL.read_text(encoding="utf-8")
        cls.yaml_text = OPENAI_YAML.read_text(encoding="utf-8")
        cls.fixture = json.loads(FIXTURES.read_text(encoding="utf-8"))

    def test_runtime_files_match_canonical_source(self):
        if RUNTIME is None:
            self.assertIsNone(RUNTIME)
            return
        self.assertEqual(
            SKILL.read_bytes(),
            (RUNTIME / "SKILL.md").read_bytes(),
            "runtime SKILL.md differs from canonical source",
        )
        self.assertEqual(
            OPENAI_YAML.read_bytes(),
            (RUNTIME / "agents" / "openai.yaml").read_bytes(),
            "runtime openai.yaml differs from canonical source",
        )

    def test_frontmatter_only_contains_name_and_description(self):
        match = re.match(r"\A---\n(.*?)\n---\n", self.skill_text, re.DOTALL)
        self.assertIsNotNone(match, "missing YAML frontmatter")
        keys = []
        for line in match.group(1).splitlines():
            if line and not line.startswith((" ", "\t", "-")) and ":" in line:
                keys.append(line.split(":", 1)[0])
        self.assertEqual(["name", "description"], keys)
        self.assertIn("name: adaptive-subagent-orchestration", match.group(0))

    def test_skill_stays_lightweight(self):
        line_count = len(self.skill_text.splitlines())
        self.assertGreaterEqual(line_count, 150)
        self.assertLessEqual(line_count, 220)

    def test_goal_owner_and_packet_contract(self):
        required = [
            "Goal: what the user must receive",
            "Done when: 1-3 observable, verifiable completion conditions",
            "Map every lane to at least one `Done when`",
            "File or directory scope | Owner | Lane ID | Shared integration surface?",
            "Give every writable file one owner for the entire run",
            "Supported Done when:",
            "File owner:",
            "First checkpoint:",
            "return `BLOCKED` before writing",
        ]
        for text in required:
            self.assertIn(text, self.skill_text)

    def test_result_contract_is_complete(self):
        for field in [
            "Lane ID:",
            "Status: PASS | BLOCKED",
            "Summary:",
            "Changed:",
            "Verification:",
            "Evidence:",
            "Failure class:",
            "Blocker:",
            "Residual risk:",
            "Out-of-scope changes:",
        ]:
            self.assertIn(field, self.skill_text)

    def test_evidence_transport_retry_and_recursion_guards(self):
        required = [
            "invalidate the old `PASS` and its evidence",
            "transport completed",
            "Never treat `transport completed` as `PASS`",
            "original owner and exact same write scope",
            "failure class, a concrete `Delta`",
            "no Delta, no new evidence, or no task difference",
            "Every subagent must not create, delegate to, or manage another subagent",
        ]
        for text in required:
            self.assertIn(text, self.skill_text)

    def test_capacity_and_verification_hygiene(self):
        required = [
            "minimum of ready independent lanes, current live capacity, and three",
            "Do not probe the limit by spawning duplicates",
            "Do not sit in a blocking wait or poll at high frequency",
            "existing lockfile, package manager, project scripts, and toolchain",
            "Do not update dependencies or generate lockfiles without authorization",
        ]
        for text in required:
            self.assertIn(text, self.skill_text)

    def test_openai_metadata_contract(self):
        required = [
            'display_name: "Adaptive Subagent Orchestrator"',
            'short_description: "Route local, offloaded, parallel, or bundled heavy-goal work safely"',
            "$adaptive-subagent-orchestration",
            "balanced mode unless host policy explicitly selects compute-offload",
            "allow_implicit_invocation: true",
        ]
        for text in required:
            self.assertIn(text, self.yaml_text)

    def test_skill_has_no_embedded_credentials_or_route_assignments(self):
        combined = self.skill_text + "\n" + self.yaml_text
        forbidden_patterns = [
            r"sk-[A-Za-z0-9]{20,}",
            r"OPENAI_API_KEY\s*=",
            r"base_url\s*=",
            r"model_provider\s*=",
            r"(?m)^\s*model\s*=",
            r"https://sub2api\.",
        ]
        for pattern in forbidden_patterns:
            self.assertIsNone(re.search(pattern, combined, re.IGNORECASE), pattern)

    def test_forward_fixture_schema_and_ids(self):
        self.assertEqual("3", self.fixture["schema_version"])
        cases = self.fixture["cases"]
        self.assertGreaterEqual(len(cases), 25)
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        for case in cases:
            self.assertRegex(case["id"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
            self.assertIn(case["kind"], {"routing", "contract", "safety"})
            self.assertEqual(
                {"mode", "estimated_minutes", "lane_types", "lane_count", "write_scopes", "traits"},
                set(case["input"]),
            )
            self.assertIn(case["input"]["mode"], {"balanced", "compute-offload"})
            self.assertEqual(
                {"level", "roles", "max_agents", "business_status", "evidence_rule", "handoff_state"},
                set(case["expected"]),
            )
            self.assertIn(case["expected"]["level"], {"L0", "D1", "L1", "L2", "L3", "SERIAL", "BLOCKED"})
            self.assertIn(case["expected"]["business_status"], {"PASS", "BLOCKED", "UNVERIFIED"})
            self.assertLessEqual(case["expected"]["max_agents"], 3)
            self.assertTrue(set(case["expected"]["roles"]).issubset({"explorer", "worker", "default"}))
            expected_handoff = "HANDOFF_READY" if case["expected"]["level"] == "L3" else "none"
            self.assertEqual(expected_handoff, case["expected"]["handoff_state"])

    def test_l3_handoff_runtime_contract(self):
        required = [
            "l3-v1",
            "source_skill: adaptive-subagent-orchestration",
            "target_skill: orchestrate-heavy-goals",
            "orchestrator_owner: parent",
            "ownership_epoch",
            "cancelled_adaptive_lanes",
            "l3-target:l3-v1",
            "HANDOFF_READY",
            "Unknown versions or fields",
        ]
        for text in required:
            self.assertIn(text, self.skill_text)

    def test_required_forward_cases_have_expected_outcomes(self):
        cases = {case["id"]: case["expected"] for case in self.fixture["cases"]}
        expected = {
            "l0-single-file": ("L0", 0),
            "l1-two-readonly": ("L1", 2),
            "l2-two-disjoint-workers": ("L2", 2),
            "shared-hotspot-serial": ("SERIAL", 0),
            "missing-write-scope-blocked": ("BLOCKED", 0),
            "owner-conflict-blocked": ("BLOCKED", 0),
            "l3-cross-module-contract": ("L3", 0),
            "sensitive-context-main-thread": ("SERIAL", 0),
            "migration-release-serial": ("SERIAL", 0),
            "capacity-batches-at-three": ("L2", 3),
            "d1-single-worker-offload": ("D1", 1),
            "d1-tiny-stays-l0": ("L0", 0),
            "d1-explorer-then-worker": ("D1", 1),
            "d1-worker-then-readonly-review": ("D1", 1),
            "d1-missing-gate-blocked": ("BLOCKED", 0),
            "d1-parent-overlap-serial": ("SERIAL", 0),
            "d1-sensitive-context-serial": ("SERIAL", 0),
            "compute-offload-heavy-still-l3": ("L3", 0),
        }
        for case_id, outcome in expected.items():
            self.assertIn(case_id, cases)
            self.assertEqual(outcome, (cases[case_id]["level"], cases[case_id]["max_agents"]))

    def test_contract_failure_cases_close_safely(self):
        cases = {case["id"]: case["expected"] for case in self.fixture["cases"]}
        blocked = {
            "missing-write-scope-blocked",
            "owner-conflict-blocked",
            "candidate-change-stales-evidence",
            "retry-without-delta-blocked",
            "worker-recursive-spawn-blocked",
            "d1-missing-gate-blocked",
        }
        for case_id in blocked:
            self.assertEqual("BLOCKED", cases[case_id]["business_status"])
        self.assertEqual("PASS", cases["final-candidate-gate-pass"]["business_status"])
        self.assertEqual(
            "require-structured-pass-scope-evidence-and-final-gate",
            cases["transport-completed-not-pass"]["evidence_rule"],
        )

    def test_compute_offload_contract_and_dispatch_order(self):
        required = [
            "Use **balanced** when no explicit mode is supplied",
            "**compute-offload** only when the user, repository, or host policy explicitly selects it",
            "**D1:** In compute-offload mode",
            "estimated at least 10 minutes",
            "A task below five minutes stays L0",
            "Evaluate L3 first, then unsafe `SERIAL`/`BLOCKED` outcomes, then mode and level",
            "maximum simultaneous subagents is one",
            "returns `Changed: none`",
            "candidate change invalidates both worker and review evidence",
        ]
        for text in required:
            self.assertIn(text, self.skill_text)

        cases = {case["id"]: case for case in self.fixture["cases"]}
        self.assertEqual(["worker"], cases["d1-single-worker-offload"]["expected"]["roles"])
        self.assertEqual(
            ["explorer", "worker"],
            cases["d1-explorer-then-worker"]["expected"]["roles"],
        )
        self.assertEqual(
            ["worker", "explorer"],
            cases["d1-worker-then-readonly-review"]["expected"]["roles"],
        )
        self.assertEqual(1, cases["d1-explorer-then-worker"]["expected"]["max_agents"])
        self.assertEqual(1, cases["d1-worker-then-readonly-review"]["expected"]["max_agents"])
        self.assertEqual("PASS", cases["d1-worker-then-readonly-review"]["expected"]["business_status"])


if __name__ == "__main__":
    unittest.main()
