import unittest
from html.parser import HTMLParser
from pathlib import Path
import re
import struct
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_MD = ROOT / "docs" / "architecture" / "oss-launch-architecture.md"
ARCHITECTURE_HTML = ROOT / "docs" / "architecture" / "oss-launch-architecture.html"
COMPUTE_OFFLOAD_ARCHITECTURE_MD = (
    ROOT / "docs" / "architecture" / "compute-offload-architecture.md"
)
COMPUTE_OFFLOAD_ARCHITECTURE_HTML = (
    ROOT / "docs" / "architecture" / "compute-offload-architecture.html"
)
README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"
README_VISUAL_ARCHITECTURE_MD = (
    ROOT / "docs" / "architecture" / "readme-visual-polish-architecture.md"
)
README_VISUAL_ARCHITECTURE_HTML = (
    ROOT / "docs" / "architecture" / "readme-visual-polish-architecture.html"
)
README_ASSET_DIR = ROOT / "docs" / "assets" / "readme"
README_IMAGE_TARGETS = [
    "docs/assets/readme/hero-orchestration.webp",
    "docs/assets/readme/ownership-boundaries.svg",
    "docs/assets/readme/routing-levels.svg",
    "docs/assets/readme/parent-agent-sequence.svg",
    "docs/assets/readme/install-lifecycle.svg",
    "docs/assets/readme/evidence-gate-loop.svg",
]
MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[([^\]]+)\]\(([^)]+)\)")


def _readme_image_entries(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    entries = []
    for index, line in enumerate(lines):
        match = MARKDOWN_IMAGE_PATTERN.fullmatch(line.strip())
        if not match:
            continue
        caption = ""
        for following in lines[index + 1 :]:
            if following.strip():
                caption = following.strip()
                break
        entries.append((match.group(1), match.group(2), caption))
    return entries


def _webp_dimensions(path):
    data = path.read_bytes()
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("not a WebP RIFF container")
    chunk = data[12:16]
    payload = data[20:]
    if chunk == b"VP8 ":
        marker = payload.find(b"\x9d\x01\x2a")
        if marker < 0 or len(payload) < marker + 7:
            raise ValueError("missing VP8 frame header")
        width, height = struct.unpack_from("<HH", payload, marker + 3)
        return width & 0x3FFF, height & 0x3FFF
    if chunk == b"VP8L":
        if len(payload) < 5 or payload[0] != 0x2F:
            raise ValueError("missing VP8L frame header")
        bits = int.from_bytes(payload[1:5], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8X":
        if len(payload) < 10:
            raise ValueError("missing VP8X frame header")
        width = int.from_bytes(payload[4:7], "little") + 1
        height = int.from_bytes(payload[7:10], "little") + 1
        return width, height
    raise ValueError(f"unsupported WebP chunk: {chunk!r}")


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


class ReadmeVisualArchitectureTests(unittest.TestCase):
    def test_visual_architecture_has_required_boundaries(self):
        markdown = README_VISUAL_ARCHITECTURE_MD.read_text(encoding="utf-8")
        for text in [
            "## Module Responsibilities",
            "## Data Flow And Trust Boundaries",
            "## Failure Design And Recovery",
            "## Deployment Units",
            "## Parallelism Boundaries",
            "ImageGen hero",
            "Deterministic SVG set",
            "Bilingual README integration",
            "Documentation tests",
            "Browser visual QA",
            "GitHub publication",
        ]:
            self.assertIn(text, markdown)

    def test_visual_architecture_html_has_export_and_flow(self):
        html = README_VISUAL_ARCHITECTURE_HTML.read_text(encoding="utf-8")
        parser = _DocumentParser()
        parser.feed(html)
        self.assertIn("report-container", parser.ids)
        for text in [
            "Frozen Contracts",
            "ImageGen Hero",
            "5 Deterministic SVGs",
            "Bilingual READMEs",
            "Stdlib Tests",
            "Browser Visual QA",
            "Manual Push Gate",
            "GitHub main + CI",
            "Public README",
            "Installed runtime bundle stays unchanged",
            "function copyAsImage",
            "function downloadPNG",
            "function downloadPDF",
        ]:
            self.assertIn(text, html)
        self.assertEqual(
            [
                "https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js",
                "https://cdn.jsdelivr.net/npm/jspdf@2.5.2/dist/jspdf.umd.min.js",
            ],
            parser.scripts,
        )


class ComputeOffloadArchitectureTests(unittest.TestCase):
    def test_compute_offload_architecture_has_required_boundaries(self):
        markdown = COMPUTE_OFFLOAD_ARCHITECTURE_MD.read_text(encoding="utf-8")
        for text in [
            "## Module Responsibilities",
            "## Data Flow And Trust Boundaries",
            "## Failure Design And Recovery",
            "## Deployment Units",
            "## Parallelism Boundaries",
            "D1",
            "provider, model, account, proxy, and credential neutral",
            "maximum live lane count one",
        ]:
            self.assertIn(text, markdown)

    def test_compute_offload_diagram_has_export_and_route_flow(self):
        html = COMPUTE_OFFLOAD_ARCHITECTURE_HTML.read_text(encoding="utf-8")
        parser = _DocumentParser()
        parser.feed(html)
        self.assertIn("report-container", parser.ids)
        for text in [
            "Compute Offload Architecture",
            "L0 • D1 • L1 • L2 • L3",
            "D1 · ONE WORKER",
            "EXPLORE → D1 / L1",
            "Balanced compatibility",
            "Compute-offload admission",
            "function copyAsImage",
            "function downloadPNG",
            "function downloadPDF",
        ]:
            self.assertIn(text, html)


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
            "docs/cases/single-worker-compute-offload.md",
            "docs/runtime-surface-matrix.md",
            "docs/contracts/compute-offload-contract.md",
            "docs/architecture/compute-offload-architecture.md",
            "docs/architecture/compute-offload-architecture.html",
            "docs/architecture/readme-visual-polish-architecture.md",
            "docs/architecture/readme-visual-polish-architecture.html",
            "tests/evidence-template.md",
            *README_IMAGE_TARGETS,
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_readmes_cover_public_contract(self):
        for text in [
            "workflow contract, not a scheduler",
            "Without this skill",
            "**L0**",
            "**D1**",
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
            "compute-offload",
            "host workspace",
            "UNVERIFIED",
        ]:
            self.assertIn(text, self.readme)
        for text in [
            "不是调度器",
            "不使用这个 skill",
            "**L0**",
            "**D1**",
            "**L1**",
            "**L2**",
            "**L3**",
            "$adaptive-subagent-orchestration",
            "--target user --dry-run",
            "--replace",
            "validate.sh",
            "uninstall.sh",
            "UNVERIFIED",
            "compute-offload",
            "宿主工作区",
        ]:
            self.assertIn(text, self.readme_zh)

    def test_public_cases_keep_write_boundary_distinct(self):
        independent = (ROOT / "docs/cases/independent-write-lanes.md").read_text(
            encoding="utf-8"
        )
        serial = (ROOT / "docs/cases/shared-hotspot-serial.md").read_text(
            encoding="utf-8"
        )
        d1 = (ROOT / "docs/cases/single-worker-compute-offload.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Use two `worker` lanes in L2", independent)
        self.assertIn("no shared file", independent)
        self.assertIn("`SERIAL`", serial)
        self.assertIn("Shared writable path", serial)
        self.assertIn("Choose D1 and dispatch exactly one `worker`", d1)
        self.assertIn("Maximum simultaneous D1 subagents", d1)
        self.assertIn("does not move local CPU execution", d1)

    def test_bilingual_readmes_share_visual_manifest_and_captions(self):
        english = _readme_image_entries(README)
        chinese = _readme_image_entries(README_ZH)
        self.assertEqual(6, len(english))
        self.assertEqual(6, len(chinese))
        self.assertEqual(README_IMAGE_TARGETS, [entry[1] for entry in english])
        self.assertEqual(README_IMAGE_TARGETS, [entry[1] for entry in chinese])
        self.assertEqual(6, len({entry[0] for entry in english}))
        self.assertEqual(6, len({entry[0] for entry in chinese}))
        for ordinal, (english_entry, chinese_entry) in enumerate(
            zip(english, chinese), start=1
        ):
            self.assertTrue(english_entry[0].strip())
            self.assertTrue(chinese_entry[0].strip())
            self.assertRegex(english_entry[2], rf"^\*Figure {ordinal}\. .+\*$")
            self.assertRegex(chinese_entry[2], rf"^\*图 {ordinal}：.+\*$")
        for document in [self.readme, self.readme_zh]:
            self.assertIn(
                "docs/architecture/oss-launch-architecture.md", document
            )
            self.assertIn(
                "docs/architecture/oss-launch-architecture.html", document
            )

    def test_readme_visual_assets_are_local_and_safe(self):
        for document in [README, README_ZH]:
            for _, target, _ in _readme_image_entries(document):
                self.assertFalse(target.startswith(("http://", "https://", "data:")))
                self.assertFalse(Path(target).is_absolute())
                resolved = (document.parent / target).resolve()
                try:
                    resolved.relative_to(README_ASSET_DIR.resolve())
                except ValueError as error:
                    self.fail(f"asset escapes docs/assets/readme: {target}: {error}")
                self.assertTrue(resolved.is_file(), target)

        hero = ROOT / README_IMAGE_TARGETS[0]
        self.assertLess(hero.stat().st_size, 300_000)
        self.assertEqual((1600, 900), _webp_dimensions(hero))

        forbidden_elements = {"script", "image", "foreignObject"}
        for relative in README_IMAGE_TARGETS[1:]:
            path = ROOT / relative
            self.assertLess(path.stat().st_size, 100_000)
            root = ET.parse(path).getroot()
            self.assertTrue(root.get("viewBox"), relative)
            direct_tags = [child.tag.rsplit("}", 1)[-1] for child in list(root)[:2]]
            self.assertEqual(["title", "desc"], direct_tags, relative)
            for node in root.iter():
                tag = node.tag.rsplit("}", 1)[-1]
                self.assertNotIn(tag, forbidden_elements, relative)
                for key, value in node.attrib.items():
                    local_key = key.rsplit("}", 1)[-1]
                    self.assertFalse(local_key.lower().startswith("on"), relative)
                    if local_key in {"href", "src"}:
                        self.assertFalse(
                            value.startswith(("http://", "https://", "data:")),
                            relative,
                        )

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
        suffixes = {
            ".html",
            ".md",
            ".py",
            ".sh",
            ".svg",
            ".yaml",
            ".yml",
            ".json",
            ".txt",
        }
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
