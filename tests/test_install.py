import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
NAME = "adaptive-subagent-orchestration"
HEAVY_NAME = "orchestrate-heavy-goals"
REAL_TEMP_ROOT = Path(tempfile.gettempdir()).resolve()


def load_lifecycle():
    spec = importlib.util.spec_from_file_location("suite_lifecycle", SCRIPTS / "_lifecycle.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LifecycleScriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(
            prefix=".adaptive-install-", dir=str(ROOT)
        )
        self.external = tempfile.TemporaryDirectory(prefix="adaptive-suite-", dir=REAL_TEMP_ROOT)
        self.workspace = Path(self.temp.name)
        self.home = self.workspace / "home"
        self.repo = self.workspace / "repo"
        self.home.mkdir()
        self.repo.mkdir()
        self.env = os.environ.copy()
        self.env["HOME"] = str(self.home)

    def tearDown(self):
        self.temp.cleanup()
        self.external.cleanup()

    def external_root(self, name):
        return Path(self.external.name) / name

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

    def test_install_writes_runtime_and_v2_manifest(self):
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
            {"schema_version", "suite_name", "skill_name", "installed_version", "capabilities", "files"},
            set(manifest),
        )
        self.assertEqual("2", manifest["schema_version"])
        self.assertEqual(NAME, manifest["suite_name"])
        self.assertEqual(NAME, manifest["skill_name"])
        self.assertEqual("0.2.0", manifest["installed_version"])
        self.assertEqual(["l3-source:l3-v1"], manifest["capabilities"])
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
        lock = target.parent / ".adaptive-subagent-orchestration-suite.lock"
        lock.mkdir()
        result = self.run_script("install.sh", "--target", "user")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(target.exists())

    def test_default_remains_adaptive_only(self):
        result = self.run_script("install.sh", "--target", "user")
        self.assertEqual(0, result.returncode, result.stderr)
        root = self.home / ".agents" / "skills"
        self.assertTrue((root / NAME).is_dir())
        self.assertFalse((root / HEAVY_NAME).exists())

    def test_install_validate_and_uninstall_full_suite(self):
        root = self.external_root("suite-root")
        result = self.run_script("install.sh", "--target-root", str(root), "--skills", "all")
        self.assertEqual(0, result.returncode, result.stderr)
        adaptive = root / NAME
        heavy = root / HEAVY_NAME
        self.assertTrue(adaptive.is_dir())
        self.assertTrue(heavy.is_dir())
        heavy_manifest = json.loads((heavy / ".install-manifest.json").read_text())
        self.assertEqual(["l3-target:l3-v1"], heavy_manifest["capabilities"])
        self.assertEqual(10, len(heavy_manifest["files"]))
        for target in (adaptive, heavy):
            checked = self.run_script("validate.sh", str(target))
            self.assertEqual(0, checked.returncode, checked.stderr)
        removed = self.run_script("uninstall.sh", "--target-root", str(root), "--skills", "all")
        self.assertEqual(0, removed.returncode, removed.stderr)
        self.assertFalse(adaptive.exists())
        self.assertFalse(heavy.exists())

    def test_target_root_works_without_explicit_target_and_conflict_fails(self):
        root = self.external_root("custom-root")
        okay = self.run_script("install.sh", "--target-root", str(root), "--skills", "heavy")
        self.assertEqual(0, okay.returncode, okay.stderr)
        conflict = self.run_script(
            "install.sh", "--target", "user", "--target-root", str(root), "--skills", "adaptive"
        )
        self.assertNotEqual(0, conflict.returncode)
        self.assertIn("LIFECYCLE_TARGET_INVALID", conflict.stderr)

    def test_partial_suite_uninstall_fails_without_deleting_member(self):
        root = self.external_root("partial-root")
        installed = self.run_script("install.sh", "--target-root", str(root), "--skills", "adaptive")
        self.assertEqual(0, installed.returncode, installed.stderr)
        result = self.run_script("uninstall.sh", "--target-root", str(root), "--skills", "all")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("LIFECYCLE_PARTIAL_SUITE", result.stderr)
        self.assertTrue((root / NAME).is_dir())

    def test_unknown_installed_entry_blocks_replace_and_uninstall(self):
        root = self.external_root("unknown-root")
        installed = self.run_script("install.sh", "--target-root", str(root), "--skills", "heavy")
        self.assertEqual(0, installed.returncode, installed.stderr)
        unknown = root / HEAVY_NAME / "private.txt"
        unknown.write_text("user data", encoding="utf-8")
        replaced = self.run_script(
            "install.sh", "--target-root", str(root), "--skills", "heavy", "--replace"
        )
        removed = self.run_script("uninstall.sh", "--target-root", str(root), "--skills", "heavy")
        self.assertNotEqual(0, replaced.returncode)
        self.assertNotEqual(0, removed.returncode)
        self.assertEqual("user data", unknown.read_text(encoding="utf-8"))

    def test_valid_legacy_adaptive_v1_upgrades_to_v2(self):
        installed = self.run_script("install.sh", "--target", "user")
        self.assertEqual(0, installed.returncode, installed.stderr)
        target = self.user_target()
        current = json.loads((target / ".install-manifest.json").read_text())
        legacy = {
            "schema_version": "1",
            "skill_name": NAME,
            "installed_version": "0.1.0",
            "files": current["files"],
        }
        (target / ".install-manifest.json").write_text(json.dumps(legacy) + "\n")
        upgraded = self.run_script("install.sh", "--target", "user", "--replace")
        self.assertEqual(0, upgraded.returncode, upgraded.stderr)
        manifest = json.loads((target / ".install-manifest.json").read_text())
        self.assertEqual("2", manifest["schema_version"])

    def test_stage_failure_leaves_suite_targets_absent(self):
        lifecycle = load_lifecycle()
        with tempfile.TemporaryDirectory(prefix="suite-fault-", dir=REAL_TEMP_ROOT) as raw:
            root = Path(raw) / "skills"
            original = lifecycle._copy_stage

            def fail_heavy(stage, bundle):
                if bundle.selector == "heavy":
                    raise lifecycle.LifecycleError("LIFECYCLE_STAGE_FAILED", "injected")
                return original(stage, bundle)

            with mock.patch.object(lifecycle, "_copy_stage", side_effect=fail_heavy):
                with self.assertRaises(lifecycle.LifecycleError):
                    lifecycle.install(None, str(root), "all", False, False)
            self.assertFalse((root / NAME).exists())
            self.assertFalse((root / HEAVY_NAME).exists())
            self.assertFalse(list(root.glob(".*.staging-*")))

    def test_activation_failure_rolls_back_new_suite(self):
        lifecycle = load_lifecycle()
        with tempfile.TemporaryDirectory(prefix="suite-fault-", dir=REAL_TEMP_ROOT) as raw:
            root = Path(raw) / "skills"
            original = lifecycle._rename

            def fail_heavy_activation(source, target):
                if target.name == HEAVY_NAME and ".staging-" in source.name:
                    raise OSError("injected activation failure")
                return original(source, target)

            with mock.patch.object(lifecycle, "_rename", side_effect=fail_heavy_activation):
                with self.assertRaises(lifecycle.LifecycleError):
                    lifecycle.install(None, str(root), "all", False, False)
            self.assertFalse((root / NAME).exists())
            self.assertFalse((root / HEAVY_NAME).exists())

    def test_uninstall_cleanup_failure_keeps_logical_uninstall(self):
        lifecycle = load_lifecycle()
        with tempfile.TemporaryDirectory(prefix="suite-fault-", dir=REAL_TEMP_ROOT) as raw:
            root = Path(raw) / "skills"
            lifecycle.install(None, str(root), "all", False, False)
            with mock.patch.object(lifecycle, "_remove_tree", side_effect=OSError("injected cleanup failure")):
                with self.assertRaises(lifecycle.LifecycleError) as raised:
                    lifecycle.uninstall(None, str(root), "all", False)
            self.assertEqual("LIFECYCLE_UNINSTALL_CLEANUP_PENDING", raised.exception.code)
            self.assertFalse((root / NAME).exists())
            self.assertFalse((root / HEAVY_NAME).exists())
            self.assertEqual(2, len(list(root.glob(".*.uninstall-*"))))


if __name__ == "__main__":
    unittest.main()
