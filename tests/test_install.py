import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
NAME = "adaptive-subagent-orchestration"


class LifecycleScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(
            prefix=".adaptive-install-", dir=str(ROOT)
        )
        self.workspace = Path(self.temp.name)
        self.home = self.workspace / "home"
        self.repo = self.workspace / "repo"
        self.home.mkdir()
        self.repo.mkdir()
        self.env = os.environ.copy()
        self.env["HOME"] = str(self.home)

    def tearDown(self):
        self.temp.cleanup()

    def run_script(self, script, *args, cwd=None):
        return subprocess.run(
            [str(SCRIPTS / script), *args],
            cwd=str(cwd or self.repo),
            env=self.env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def user_target(self):
        return self.home / ".agents" / "skills" / NAME

    def test_dry_run_has_no_mutation(self):
        result = self.run_script("install.sh", "--target", "user", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.user_target().exists())
        self.assertFalse((self.home / ".agents").exists())

    def test_install_writes_runtime_and_v1_manifest(self):
        result = self.run_script("install.sh", "--target", "user")
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.user_target()
        self.assertTrue(target.is_dir())
        self.assertEqual(
            (ROOT / "SKILL.md").read_bytes(), (target / "SKILL.md").read_bytes()
        )
        self.assertEqual(
            (ROOT / "agents" / "openai.yaml").read_bytes(),
            (target / "agents" / "openai.yaml").read_bytes(),
        )
        manifest = json.loads((target / ".install-manifest.json").read_text())
        self.assertEqual(
            {"schema_version", "skill_name", "installed_version", "files"},
            set(manifest),
        )
        self.assertEqual("1", manifest["schema_version"])
        self.assertEqual(NAME, manifest["skill_name"])
        self.assertEqual("0.1.0", manifest["installed_version"])
        self.assertEqual({"SKILL.md", "agents/openai.yaml"}, set(manifest["files"]))
        for relative in ("SKILL.md", "agents/openai.yaml"):
            digest = hashlib.sha256((target / relative).read_bytes()).hexdigest()
            self.assertEqual("sha256:" + digest, manifest["files"][relative])

    def test_repeated_install_rejects_without_replace(self):
        first = self.run_script("install.sh", "--target", "user")
        self.assertEqual(first.returncode, 0, first.stderr)
        target = self.user_target()
        before = {
            "skill": (target / "SKILL.md").read_bytes(),
            "manifest": (target / ".install-manifest.json").read_bytes(),
        }
        second = self.run_script("install.sh", "--target", "user")
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("--replace", second.stderr)
        self.assertEqual(before["skill"], (target / "SKILL.md").read_bytes())
        self.assertEqual(before["manifest"], (target / ".install-manifest.json").read_bytes())

    def test_replace_creates_timestamped_unique_sibling_backup(self):
        first = self.run_script("install.sh", "--target", "user")
        self.assertEqual(first.returncode, 0, first.stderr)
        target = self.user_target()
        old_skill = (target / "SKILL.md").read_bytes()
        result = self.run_script("install.sh", "--target", "user", "--replace")
        self.assertEqual(result.returncode, 0, result.stderr)
        backups = sorted(target.parent.glob(NAME + ".backup-*"))
        self.assertEqual(1, len(backups))
        self.assertEqual(old_skill, (backups[0] / "SKILL.md").read_bytes())
        self.assertFalse(list(target.parent.glob("." + NAME + ".staging-*")))

    def test_validate_accepts_source_and_installed_bundle(self):
        source = self.run_script("validate.sh", str(ROOT))
        self.assertEqual(source.returncode, 0, source.stderr)
        installed = self.run_script("install.sh", "--target", "user")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        result = self.run_script("validate.sh", str(self.user_target()))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_modified_owned_file_blocks_uninstall_and_preserves_files(self):
        installed = self.run_script("install.sh", "--target", "user")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        target = self.user_target()
        modified = (target / "SKILL.md").read_bytes() + b"\nuser edit\n"
        (target / "SKILL.md").write_bytes(modified)
        result = self.run_script("uninstall.sh", "--target", "user")
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(target.is_dir())
        self.assertEqual(modified, (target / "SKILL.md").read_bytes())
        self.assertTrue((target / ".install-manifest.json").is_file())

    def test_clean_uninstall_removes_bundle(self):
        installed = self.run_script("install.sh", "--target", "user")
        self.assertEqual(installed.returncode, 0, installed.stderr)
        result = self.run_script("uninstall.sh", "--target", "user")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.user_target().exists())

    def test_repo_and_custom_targets(self):
        repo_result = self.run_script("install.sh", "--target", "repo")
        self.assertEqual(repo_result.returncode, 0, repo_result.stderr)
        repo_target = self.repo / ".agents" / "skills" / NAME
        self.assertTrue(repo_target.is_dir())

        custom = self.workspace / "custom" / NAME
        custom_result = self.run_script("install.sh", "--target", str(custom))
        self.assertEqual(custom_result.returncode, 0, custom_result.stderr)
        self.assertTrue(custom.is_dir())

    def test_invalid_and_symlink_targets_are_blocked(self):
        relative = self.run_script("install.sh", "--target", "relative/" + NAME)
        self.assertNotEqual(relative.returncode, 0)
        wrong_name = self.run_script("install.sh", "--target", str(self.workspace / "wrong"))
        self.assertNotEqual(wrong_name.returncode, 0)

        real = self.workspace / "real" / NAME
        real.parent.mkdir()
        link_target = self.workspace / NAME
        os.symlink(real, link_target)
        symlink_target = self.run_script("install.sh", "--target", str(link_target))
        self.assertNotEqual(symlink_target.returncode, 0)
        self.assertFalse(real.exists())

        real_parent = self.workspace / "real-parent"
        real_parent.mkdir()
        link_parent = self.workspace / "link-parent"
        os.symlink(real_parent, link_parent)
        symlink_parent = self.run_script(
            "install.sh", "--target", str(link_parent / NAME)
        )
        self.assertNotEqual(symlink_parent.returncode, 0)
        self.assertFalse((real_parent / NAME).exists())

    def test_target_scoped_lock_blocks_mutation(self):
        target = self.user_target()
        target.parent.mkdir(parents=True)
        lock = target.parent / ("." + NAME + ".lock")
        lock.mkdir()
        result = self.run_script("install.sh", "--target", "user")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
