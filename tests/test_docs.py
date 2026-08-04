import unittest
from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_MD = ROOT / "docs" / "architecture" / "oss-launch-architecture.md"
ARCHITECTURE_HTML = ROOT / "docs" / "architecture" / "oss-launch-architecture.html"
README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"


class _DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.add(attributes["id"])
        if tag == "script" and "src" in attributes:
            self.scripts.append(attributes["src"])


class ArchitectureDocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.markdown = ARCHITECTURE_MD.read_text(encoding="utf-8")
        cls.html = ARCHITECTURE_HTML.read_text(encoding="utf-8")
        cls.parser = _DocumentParser()
        cls.parser.feed(cls.html)

    def test_architecture_has_required_sections_and_modules(self):
        for text in [
            "## Module Responsibilities",
            "## Data Flow And Trust Boundaries",
            "## Failure Design And Recovery",
            "## Deployment Units",
            "## Parallelism Boundaries",
            "Runtime skill",
            "Lifecycle scripts",
            "Contract suite",
            "Evidence and docs",
            "CI and release",
        ]:
            self.assertIn(text, self.markdown)

    def test_diagram_contains_required_flows_and_export_contract(self):
        self.assertIn("report-container", self.parser.ids)
        for text in [
            "Runtime Skill",
            "Contract + CI",
            "Lifecycle",
            "Installed Bundle",
            "Parent Codex",
            "L0–L3 Router",
            "Bounded Agents",
            "Manual Gate",
            "GitHub Repository + Release",
            "function copyAsImage",
            "function downloadPNG",
            "function downloadPDF",
        ]:
            self.assertIn(text, self.html)
        self.assertEqual(
            [
                "https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js",
                "https://cdn.jsdelivr.net/npm/jspdf@2.5.2/dist/jspdf.umd.min.js",
            ],
            self.parser.scripts,
        )


class PublicDocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.readme = README.read_text(encoding="utf-8")
        cls.readme_zh = README_ZH.read_text(encoding="utf-8")

    def test_public_docs_and_governance_exist(self):
        required = [
            "README.md",
            "README.zh-CN.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "CODE_OF_CONDUCT.md",
            "CHANGELOG.md",
            "templates/AGENTS-routing.md",
            "docs/cases/independent-write-lanes.md",
            "docs/cases/shared-hotspot-serial.md",
            "docs/runtime-surface-matrix.md",
            "tests/evidence-template.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_readmes_cover_public_contract(self):
        for text in [
            "workflow contract, not a scheduler",
            "Without this skill",
            "**L0**",
            "**L1**",
            "**L2**",
            "**L3**",
            "$adaptive-subagent-orchestration",
            "--target user --dry-run",
            "--target repo",
            "--replace",
            "validate.sh",
            "uninstall.sh",
            "timestamped sibling backup",
            "provider/model neutrality",
            "UNVERIFIED",
        ]:
            self.assertIn(text, self.readme)
        for text in [
            "不是调度器",
            "不使用这个 skill",
            "**L0**",
            "**L1**",
            "**L2**",
            "**L3**",
            "$adaptive-subagent-orchestration",
            "--target user --dry-run",
            "--replace",
            "validate.sh",
            "uninstall.sh",
            "UNVERIFIED",
        ]:
            self.assertIn(text, self.readme_zh)

    def test_public_cases_keep_write_boundary_distinct(self):
        independent = (ROOT / "docs/cases/independent-write-lanes.md").read_text(
            encoding="utf-8"
        )
        serial = (ROOT / "docs/cases/shared-hotspot-serial.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Use two `worker` lanes in L2", independent)
        self.assertIn("no shared file", independent)
        self.assertIn("`SERIAL`", serial)
        self.assertIn("Shared writable path", serial)

    def test_relative_markdown_links_resolve(self):
        documents = [
            README,
            README_ZH,
            ROOT / "CONTRIBUTING.md",
            ROOT / "docs/runtime-surface-matrix.md",
        ]
        pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for document in documents:
            for target in pattern.findall(document.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_text = target.split("#", 1)[0]
                self.assertTrue((document.parent / path_text).resolve().exists(), target)

    def test_public_candidate_has_no_private_route_or_credential_patterns(self):
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            candidates = result.stdout.splitlines()
        else:
            candidates = [
                str(path.relative_to(ROOT))
                for path in ROOT.rglob("*")
                if path.is_file()
                and ".git" not in path.parts
                and "__pycache__" not in path.parts
            ]
        forbidden = [
            re.compile(r"/Users/[A-Za-z0-9._-]+/"),
            re.compile(r"sk-[A-Za-z0-9]{20,}"),
            re.compile(r"OPENAI_API_KEY", re.IGNORECASE),
            re.compile(r"sub2api", re.IGNORECASE),
            re.compile(r"silliter", re.IGNORECASE),
            re.compile(r"gpt-5\.6-(?:sol|luna)", re.IGNORECASE),
            re.compile(r"model_provider\s*=", re.IGNORECASE),
            re.compile(r"base_url\s*=", re.IGNORECASE),
            re.compile(r"codex-silliter", re.IGNORECASE),
        ]
        suffixes = {".md", ".py", ".sh", ".yaml", ".yml", ".json", ".txt"}
        for relative in candidates:
            if relative in {"tests/test_contract.py", "tests/test_docs.py"}:
                continue
            path = ROOT / relative
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in forbidden:
                self.assertIsNone(pattern.search(text), f"{relative}: {pattern.pattern}")


if __name__ == "__main__":
    unittest.main()
