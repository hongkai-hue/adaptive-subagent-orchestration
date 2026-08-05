import re
import os
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEAVY = ROOT / "skills" / "orchestrate-heavy-goals"
RUNTIME_VALUE = os.environ.get("HEAVY_SKILL_RUNTIME")
RUNTIME = Path(RUNTIME_VALUE).expanduser() if RUNTIME_VALUE else None


class HeavySkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skill = (HEAVY / "SKILL.md").read_text(encoding="utf-8")
        cls.metadata = (HEAVY / "agents" / "openai.yaml").read_text(encoding="utf-8")

    def test_exact_runtime_allowlist_exists(self):
        expected = {
            "SKILL.md",
            "agents/openai.yaml",
            "references/architecture-baseline.md",
            "references/diagram-baseline.md",
            "references/artifact-templates.md",
            "references/l3-handoff.md",
            "references/node-contract.md",
            "references/qa-gates.md",
            "references/recovery.md",
            "scripts/scaffold_flow.py",
        }
        actual = {
            path.relative_to(HEAVY).as_posix()
            for path in HEAVY.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        self.assertEqual(expected, actual)

    def test_installed_runtime_matches_canonical_source(self):
        if RUNTIME is None:
            self.assertIsNone(RUNTIME)
            return
        for source in HEAVY.rglob("*"):
            if source.is_file() and "__pycache__" not in source.parts:
                relative = source.relative_to(HEAVY)
                self.assertEqual(source.read_bytes(), (RUNTIME / relative).read_bytes(), str(relative))

    def test_frontmatter_and_metadata(self):
        match = re.match(r"\A---\n(.*?)\n---\n", self.skill, re.DOTALL)
        self.assertIsNotNone(match)
        self.assertIn("name: orchestrate-heavy-goals", match.group(0))
        self.assertIn('display_name: "Heavy Goal Orchestrator"', self.metadata)
        self.assertIn("allow_implicit_invocation: true", self.metadata)

    def test_heavy_flow_is_self_contained(self):
        required = [
            "Accept An L3 Handoff",
            "Use The Heavy Boundary",
            "Keep One Orchestrator",
            "Establish Architecture",
            "Freeze Contract",
            "Build The Wave DAG",
            "Record Async Questions",
            "Execute And Recover",
            "Run Layered QA And Readiness",
            "Stop At Manual Gates",
            "They are the mandatory,",
            "self-contained baseline",
            "optional enhancements",
        ]
        for text in required:
            self.assertIn(text, self.skill)

    def test_runtime_is_provider_and_credential_neutral(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in HEAVY.rglob("*")
            if path.is_file() and path.suffix in {".md", ".yaml", ".py"}
        )
        for pattern in [
            r"sk-[A-Za-z0-9]{20,}",
            "OPENAI_" + r"API_KEY\s*=",
            r"base_url\s*=",
            r"model_provider\s*=",
            r"(?m)^\s*model\s*=",
        ]:
            self.assertIsNone(re.search(pattern, combined, re.IGNORECASE), pattern)


if __name__ == "__main__":
    unittest.main()
