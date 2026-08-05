import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "orchestrate-heavy-goals" / "scripts" / "scaffold_flow.py"
REAL_TEMP_ROOT = Path(tempfile.gettempdir()).resolve()


class ScaffoldFlowTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [str(SCRIPT), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def test_dry_run_creates_nothing_and_reports_terminal_marker(self):
        with tempfile.TemporaryDirectory(prefix="heavy-scaffold-", dir=REAL_TEMP_ROOT) as raw:
            root = Path(raw)
            result = self.run_script(
                "--root", str(root), "--slug", "sample-flow", "--title", "Sample Flow",
                "--prefix", "SF", "--dry-run",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("HEAVY_SCAFFOLD_PASS", result.stdout)
            self.assertIn("PENDING", result.stdout)
            self.assertFalse((root / "docs").exists())

    def test_create_is_non_destructive_and_reports_missing_sections(self):
        with tempfile.TemporaryDirectory(prefix="heavy-scaffold-", dir=REAL_TEMP_ROOT) as raw:
            root = Path(raw)
            args = ("--root", str(root), "--slug", "sample-flow", "--title", "Sample Flow", "--prefix", "SF")
            first = self.run_script(*args)
            self.assertEqual(0, first.returncode, first.stderr)
            architecture = root / "docs" / "architecture" / "sample-flow-architecture.md"
            architecture.write_text("# user content\n", encoding="utf-8")
            second = self.run_script(*args)
            self.assertEqual(0, second.returncode, second.stderr)
            self.assertEqual("# user content\n", architecture.read_text(encoding="utf-8"))
            self.assertIn("WARN missing:", second.stdout)

    def test_invalid_slug_prefix_and_symlink_escape_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix="heavy-scaffold-", dir=REAL_TEMP_ROOT) as raw:
            root = Path(raw)
            invalid = self.run_script("--root", str(root), "--slug", "Bad", "--title", "Bad", "--prefix", "x")
            self.assertNotEqual(0, invalid.returncode)
            outside = root / "outside"
            outside.mkdir()
            (root / "docs").mkdir()
            os.symlink(outside, root / "docs" / "architecture")
            escaped = self.run_script("--root", str(root), "--slug", "safe", "--title", "Safe", "--prefix", "SF")
            self.assertNotEqual(0, escaped.returncode)
            self.assertFalse((outside / "safe-architecture.md").exists())


if __name__ == "__main__":
    unittest.main()
