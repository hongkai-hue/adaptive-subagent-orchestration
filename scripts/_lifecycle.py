#!/usr/bin/env python3
"""Dependency-free, transactional lifecycle for the two-skill suite."""

from __future__ import annotations

import argparse
import contextlib
from dataclasses import dataclass
import datetime as dt
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import shutil
import stat
import sys
from typing import Iterator


SUITE_NAME = "adaptive-subagent-orchestration"
VERSION = "0.2.0"
MANIFEST_NAME = ".install-manifest.json"
SOURCE_ROOT = Path(__file__).resolve().parent.parent
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class Bundle:
    selector: str
    skill_name: str
    source_root: Path
    capability: str
    runtime_files: tuple[str, ...]


ADAPTIVE = Bundle(
    "adaptive",
    "adaptive-subagent-orchestration",
    SOURCE_ROOT,
    "l3-source:l3-v1",
    ("SKILL.md", "agents/openai.yaml"),
)
HEAVY = Bundle(
    "heavy",
    "orchestrate-heavy-goals",
    SOURCE_ROOT / "skills" / "orchestrate-heavy-goals",
    "l3-target:l3-v1",
    (
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
    ),
)
BUNDLES = {bundle.selector: bundle for bundle in (ADAPTIVE, HEAVY)}


class LifecycleError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def fail(code: str, message: str) -> "NoReturn":
    raise LifecycleError(code, message)


def _lstat(path: Path):
    try:
        return path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        fail("LIFECYCLE_TARGET_INVALID", f"cannot inspect {path}: {exc}")


def _require_dir(path: Path, code: str, label: str) -> None:
    mode = _lstat(path)
    if mode is None or stat.S_ISLNK(mode.st_mode) or not stat.S_ISDIR(mode.st_mode):
        fail(code, f"{label} is not a real directory: {path}")


def _require_file(path: Path, code: str, label: str) -> None:
    mode = _lstat(path)
    if mode is None or stat.S_ISLNK(mode.st_mode) or not stat.S_ISREG(mode.st_mode):
        fail(code, f"{label} is not a regular file: {path}")


def _reject_symlinks(path: Path, code: str = "LIFECYCLE_TARGET_INVALID") -> None:
    if not path.is_absolute():
        fail(code, f"path must be absolute: {path}")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        mode = _lstat(current)
        if mode is not None and stat.S_ISLNK(mode.st_mode):
            fail(code, f"path cannot traverse a symlink: {current}")


def _make_dirs(path: Path) -> None:
    if not path.is_absolute():
        fail("LIFECYCLE_TARGET_INVALID", f"directory must be absolute: {path}")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        mode = _lstat(current)
        if mode is None:
            try:
                os.mkdir(current, 0o755)
            except FileExistsError:
                pass
            except OSError as exc:
                fail("LIFECYCLE_TARGET_INVALID", f"cannot create {current}: {exc}")
            mode = _lstat(current)
        if mode is None or stat.S_ISLNK(mode.st_mode) or not stat.S_ISDIR(mode.st_mode):
            fail("LIFECYCLE_TARGET_INVALID", f"target parent is unsafe: {current}")


def _normalize_abs(raw: str, *, expand_user: bool, relative_ok: bool) -> Path:
    supplied = Path(raw).expanduser() if expand_user else Path(raw)
    if any(part == ".." for part in supplied.parts):
        fail("LIFECYCLE_TARGET_INVALID", "path cannot contain '..'")
    if not supplied.is_absolute():
        if not relative_ok:
            fail("LIFECYCLE_TARGET_INVALID", f"path must be absolute: {raw}")
        supplied = Path.cwd() / supplied
    return Path(os.path.normpath(str(supplied)))


def _inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _sha(path: Path) -> str:
    _require_file(path, "LIFECYCLE_PRIVATE_OR_DRIFTED", str(path))
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        fail("LIFECYCLE_PRIVATE_OR_DRIFTED", f"cannot hash {path}: {exc}")
    return "sha256:" + digest.hexdigest()


def _validate_frontmatter(path: Path, bundle: Bundle, code: str) -> None:
    _require_file(path, code, "SKILL.md")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        fail(code, f"cannot read {path}: {exc}")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if match is None:
        fail(code, f"invalid frontmatter: {path}")
    entries: list[tuple[str, str]] = []
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if line[:1].isspace() or ":" not in line:
            fail(code, f"frontmatter must contain only name and description: {path}")
        key, value = line.split(":", 1)
        entries.append((key.strip(), value.strip()))
    if [key for key, _ in entries] != ["name", "description"]:
        fail(code, f"frontmatter keys are invalid: {path}")
    if entries[0][1] != bundle.skill_name or not entries[1][1]:
        fail(code, f"frontmatter identity is invalid: {path}")


def _validate_metadata(path: Path, code: str) -> None:
    _require_file(path, code, "agents/openai.yaml")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        fail(code, f"cannot read {path}: {exc}")
    if "interface:" not in text or "allow_implicit_invocation:" not in text:
        fail(code, f"agents/openai.yaml is malformed: {path}")


def validate_source(bundle: Bundle) -> None:
    code = "LIFECYCLE_SOURCE_INVALID"
    _reject_symlinks(bundle.source_root, code)
    _require_dir(bundle.source_root, code, "canonical source")
    for rel in bundle.runtime_files:
        _require_file(bundle.source_root / rel, code, f"source {rel}")
    _validate_frontmatter(bundle.source_root / "SKILL.md", bundle, code)
    _validate_metadata(bundle.source_root / "agents/openai.yaml", code)


def _valid_rel(rel: str) -> bool:
    posix = PurePosixPath(rel)
    return bool(rel) and "\\" not in rel and not posix.is_absolute() and all(
        part not in {"", ".", ".."} for part in posix.parts
    )


def _read_manifest(path: Path, bundle: Bundle) -> dict:
    _require_file(path, "LIFECYCLE_PRIVATE_OR_DRIFTED", MANIFEST_NAME)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail("LIFECYCLE_PRIVATE_OR_DRIFTED", f"invalid manifest at {path}: {exc}")
    if not isinstance(data, dict):
        fail("LIFECYCLE_PRIVATE_OR_DRIFTED", f"manifest must be an object: {path}")
    schema = data.get("schema_version")
    if schema == "1":
        if bundle != ADAPTIVE or set(data) != {"schema_version", "skill_name", "installed_version", "files"}:
            fail("LIFECYCLE_PRIVATE_OR_DRIFTED", "manifest v1 is accepted only for legacy adaptive")
        if data.get("skill_name") != ADAPTIVE.skill_name or data.get("installed_version") != "0.1.0":
            fail("LIFECYCLE_PRIVATE_OR_DRIFTED", "legacy adaptive manifest identity mismatch")
    elif schema == "2":
        if set(data) != {"schema_version", "suite_name", "skill_name", "installed_version", "capabilities", "files"}:
            fail("LIFECYCLE_PRIVATE_OR_DRIFTED", "manifest v2 keys are invalid")
        if (
            data.get("suite_name") != SUITE_NAME
            or data.get("skill_name") != bundle.skill_name
            or data.get("installed_version") != VERSION
            or data.get("capabilities") != [bundle.capability]
        ):
            fail("LIFECYCLE_PRIVATE_OR_DRIFTED", "manifest v2 identity or capability mismatch")
    else:
        fail("LIFECYCLE_PRIVATE_OR_DRIFTED", f"unsupported manifest schema: {schema!r}")
    files = data.get("files")
    if not isinstance(files, dict) or set(files) != set(bundle.runtime_files):
        fail("LIFECYCLE_PRIVATE_OR_DRIFTED", "manifest file allowlist mismatch")
    for rel, digest in files.items():
        if not isinstance(rel, str) or not _valid_rel(rel) or not isinstance(digest, str) or not HASH_RE.fullmatch(digest):
            fail("LIFECYCLE_PRIVATE_OR_DRIFTED", f"invalid manifest entry: {rel!r}")
    return data


def _expected_entries(bundle: Bundle) -> set[str]:
    entries = {MANIFEST_NAME, *bundle.runtime_files}
    for rel in bundle.runtime_files:
        parent = PurePosixPath(rel).parent
        while str(parent) != ".":
            entries.add(parent.as_posix())
            parent = parent.parent
    return entries


def _validate_exact_tree(path: Path, bundle: Bundle) -> None:
    expected = _expected_entries(bundle)
    actual: set[str] = set()
    try:
        for current, dirs, files in os.walk(path, topdown=True, followlinks=False):
            current_path = Path(current)
            for name in dirs + files:
                entry = current_path / name
                rel = entry.relative_to(path).as_posix()
                mode = entry.lstat().st_mode
                if stat.S_ISLNK(mode) or not (stat.S_ISDIR(mode) or stat.S_ISREG(mode)):
                    fail("LIFECYCLE_PRIVATE_OR_DRIFTED", f"unsafe installed entry: {entry}")
                actual.add(rel)
    except OSError as exc:
        fail("LIFECYCLE_PRIVATE_OR_DRIFTED", f"cannot inspect installed tree {path}: {exc}")
    if actual != expected:
        fail("LIFECYCLE_PRIVATE_OR_DRIFTED", f"installed tree differs from allowlist: {path}")


def _validate_installed(path: Path, bundle: Bundle) -> dict:
    _reject_symlinks(path, "LIFECYCLE_PRIVATE_OR_DRIFTED")
    _require_dir(path, "LIFECYCLE_PRIVATE_OR_DRIFTED", "installed target")
    if path.name != bundle.skill_name:
        fail("LIFECYCLE_PRIVATE_OR_DRIFTED", f"installed directory name mismatch: {path}")
    manifest = _read_manifest(path / MANIFEST_NAME, bundle)
    _validate_exact_tree(path, bundle)
    _validate_frontmatter(path / "SKILL.md", bundle, "LIFECYCLE_PRIVATE_OR_DRIFTED")
    _validate_metadata(path / "agents/openai.yaml", "LIFECYCLE_PRIVATE_OR_DRIFTED")
    for rel, expected in manifest["files"].items():
        if _sha(path / rel) != expected:
            fail("LIFECYCLE_PRIVATE_OR_DRIFTED", f"checksum mismatch: {path / rel}")
    return manifest


def _manifest(stage: Path, bundle: Bundle) -> dict:
    return {
        "schema_version": "2",
        "suite_name": SUITE_NAME,
        "skill_name": bundle.skill_name,
        "installed_version": VERSION,
        "capabilities": [bundle.capability],
        "files": {rel: _sha(stage / rel) for rel in bundle.runtime_files},
    }


def _selected(selector: str) -> tuple[Bundle, ...]:
    return (ADAPTIVE, HEAVY) if selector == "all" else (BUNDLES[selector],)


def resolve_targets(target: str | None, target_root: str | None, selector: str) -> tuple[Path, dict[str, Path]]:
    bundles = _selected(selector)
    if target is not None and target_root is not None:
        fail("LIFECYCLE_TARGET_INVALID", "--target and --target-root are mutually exclusive")
    target = "user" if target is None and target_root is None else target
    if target_root is not None:
        root = _normalize_abs(target_root, expand_user=False, relative_ok=False)
        if _inside(root, SOURCE_ROOT):
            fail("LIFECYCLE_TARGET_INVALID", "custom target root cannot be inside the source repository")
    elif target == "user":
        home = os.environ.get("HOME")
        if not home:
            fail("LIFECYCLE_TARGET_INVALID", "HOME is required for --target user")
        root = _normalize_abs(home, expand_user=True, relative_ok=False) / ".agents" / "skills"
    elif target == "repo":
        root = Path.cwd() / ".agents" / "skills"
    else:
        if selector != "adaptive" or target is None:
            fail("LIFECYCLE_TARGET_INVALID", "legacy absolute --target supports only adaptive")
        exact = _normalize_abs(target, expand_user=True, relative_ok=False)
        if exact.name != ADAPTIVE.skill_name:
            fail("LIFECYCLE_TARGET_INVALID", f"legacy target must end in {ADAPTIVE.skill_name}")
        root = exact.parent
    root = Path(os.path.normpath(str(root)))
    _reject_symlinks(root)
    targets = {bundle.selector: root / bundle.skill_name for bundle in bundles}
    for bundle in bundles:
        candidate = targets[bundle.selector]
        _reject_symlinks(candidate)
        if candidate == bundle.source_root:
            fail("LIFECYCLE_TARGET_INVALID", "target cannot equal canonical source")
    return root, targets


def _stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _sibling(target: Path, kind: str) -> Path:
    for _ in range(100):
        hidden = kind != "backup"
        prefix = "." if hidden else ""
        candidate = target.parent / f"{prefix}{target.name}.{kind}-{_stamp()}-{secrets.token_hex(5)}"
        if _lstat(candidate) is None:
            return candidate
    fail("LIFECYCLE_STAGE_FAILED", f"cannot allocate {kind} path beside {target}")


def _rename(source: Path, target: Path) -> None:
    os.rename(source, target)


def _remove_tree(path: Path) -> None:
    shutil.rmtree(path)


@contextlib.contextmanager
def suite_lock(root: Path) -> Iterator[None]:
    lock = root / ".adaptive-subagent-orchestration-suite.lock"
    if _lstat(lock) is not None:
        fail("LIFECYCLE_LOCKED", f"skills root is locked: {root}")
    try:
        os.mkdir(lock, 0o700)
    except FileExistsError:
        fail("LIFECYCLE_LOCKED", f"skills root is locked: {root}")
    except OSError as exc:
        fail("LIFECYCLE_LOCKED", f"cannot acquire lock {lock}: {exc}")
    operation_error = False
    try:
        yield
    except Exception:
        operation_error = True
        raise
    finally:
        try:
            os.rmdir(lock)
        except FileNotFoundError:
            pass
        except OSError as exc:
            if not operation_error:
                fail("LIFECYCLE_LOCKED", f"lock cleanup pending at {lock}: {exc}")


def _copy_stage(stage: Path, bundle: Bundle) -> None:
    try:
        stage.mkdir(mode=0o755)
        for rel in bundle.runtime_files:
            destination = stage / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(bundle.source_root / rel, destination)
            shutil.copymode(bundle.source_root / rel, destination)
        (stage / MANIFEST_NAME).write_text(
            json.dumps(_manifest(stage, bundle), indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        fail("LIFECYCLE_STAGE_FAILED", f"cannot stage {bundle.skill_name}: {exc}")


def _cleanup_stage(path: Path | None) -> None:
    if path is None:
        return
    mode = _lstat(path)
    if mode is not None and stat.S_ISDIR(mode.st_mode) and not stat.S_ISLNK(mode.st_mode):
        try:
            _remove_tree(path)
        except OSError:
            pass


def _preflight_install(bundles: tuple[Bundle, ...], targets: dict[str, Path], replace: bool) -> None:
    for bundle in bundles:
        validate_source(bundle)
        target = targets[bundle.selector]
        if _lstat(target) is not None:
            if not replace:
                fail("LIFECYCLE_TARGET_EXISTS", f"target exists; rerun with --replace: {target}")
            _validate_installed(target, bundle)


def install(target: str | None, target_root: str | None, selector: str, dry_run: bool, replace: bool) -> int:
    bundles = _selected(selector)
    root, targets = resolve_targets(target, target_root, selector)
    _preflight_install(bundles, targets, replace)
    if dry_run:
        for bundle in bundles:
            action = "replace" if _lstat(targets[bundle.selector]) is not None else "install"
            print(f"dry-run: would {action} {targets[bundle.selector]}")
        return 0
    _make_dirs(root)
    stages: dict[str, Path] = {}
    backups: dict[str, Path] = {}
    activated: list[Bundle] = []
    with suite_lock(root):
        _preflight_install(bundles, targets, replace)
        try:
            for bundle in bundles:
                stage = _sibling(targets[bundle.selector], "staging")
                stages[bundle.selector] = stage
                _copy_stage(stage, bundle)
                # The stage has a unique name, so validate its contents with the intended identity.
                manifest = _read_manifest(stage / MANIFEST_NAME, bundle)
                _validate_exact_tree(stage, bundle)
                _validate_frontmatter(stage / "SKILL.md", bundle, "LIFECYCLE_STAGE_FAILED")
                _validate_metadata(stage / "agents/openai.yaml", "LIFECYCLE_STAGE_FAILED")
                for rel, expected in manifest["files"].items():
                    if _sha(stage / rel) != expected:
                        fail("LIFECYCLE_STAGE_FAILED", f"staged checksum mismatch: {stage / rel}")
            for bundle in bundles:
                current = targets[bundle.selector]
                if _lstat(current) is not None:
                    backup = _sibling(current, "backup")
                    _rename(current, backup)
                    backups[bundle.selector] = backup
            for bundle in bundles:
                _rename(stages[bundle.selector], targets[bundle.selector])
                stages.pop(bundle.selector)
                activated.append(bundle)
            for bundle in bundles:
                _validate_installed(targets[bundle.selector], bundle)
        except Exception as original:
            rollback_errors: list[str] = []
            for bundle in reversed(activated):
                current = targets[bundle.selector]
                if _lstat(current) is not None:
                    try:
                        _remove_tree(current)
                    except OSError as exc:
                        rollback_errors.append(f"remove {current}: {exc}")
            for bundle in reversed(bundles):
                backup = backups.get(bundle.selector)
                if backup is not None and _lstat(targets[bundle.selector]) is None:
                    try:
                        _rename(backup, targets[bundle.selector])
                    except OSError as exc:
                        rollback_errors.append(f"restore {backup}: {exc}")
            for stage in stages.values():
                _cleanup_stage(stage)
            if rollback_errors:
                fail("LIFECYCLE_ROLLBACK_INCOMPLETE", "; ".join(rollback_errors))
            if isinstance(original, LifecycleError):
                if original.code == "LIFECYCLE_STAGE_FAILED":
                    raise original
                fail("LIFECYCLE_ACTIVATION_FAILED", str(original))
            fail("LIFECYCLE_ACTIVATION_FAILED", str(original))
    for bundle in bundles:
        suffix = f" (backup: {backups[bundle.selector]})" if bundle.selector in backups else ""
        print(f"installed: {targets[bundle.selector]}{suffix}")
    return 0


def _preflight_uninstall(bundles: tuple[Bundle, ...], targets: dict[str, Path], selector: str) -> bool:
    present = [bundle for bundle in bundles if _lstat(targets[bundle.selector]) is not None]
    if selector == "all" and len(present) == 1:
        fail("LIFECYCLE_PARTIAL_SUITE", "only one suite member is installed; delete nothing")
    if not present:
        return False
    for bundle in present:
        _validate_installed(targets[bundle.selector], bundle)
    return True


def uninstall(target: str | None, target_root: str | None, selector: str, dry_run: bool) -> int:
    bundles = _selected(selector)
    root, targets = resolve_targets(target, target_root, selector)
    if not _preflight_uninstall(bundles, targets, selector):
        print("suite not installed" if selector == "all" else f"not installed: {next(iter(targets.values()))}")
        return 0
    if dry_run:
        for bundle in bundles:
            print(f"dry-run: would uninstall {targets[bundle.selector]}")
        return 0
    stages: dict[str, Path] = {}
    with suite_lock(root):
        _preflight_uninstall(bundles, targets, selector)
        try:
            for bundle in bundles:
                stage = _sibling(targets[bundle.selector], "uninstall")
                _rename(targets[bundle.selector], stage)
                stages[bundle.selector] = stage
        except OSError as exc:
            for bundle in reversed(bundles):
                stage = stages.get(bundle.selector)
                if stage is not None and _lstat(targets[bundle.selector]) is None:
                    try:
                        _rename(stage, targets[bundle.selector])
                    except OSError as rollback_exc:
                        fail("LIFECYCLE_ROLLBACK_INCOMPLETE", f"cannot restore {stage}: {rollback_exc}")
            fail("LIFECYCLE_ACTIVATION_FAILED", f"logical uninstall failed: {exc}")
        cleanup_errors: list[str] = []
        for bundle in bundles:
            stage = stages[bundle.selector]
            try:
                _remove_tree(stage)
            except OSError as exc:
                cleanup_errors.append(f"{stage}: {exc}")
        if cleanup_errors:
            fail("LIFECYCLE_UNINSTALL_CLEANUP_PENDING", "; ".join(cleanup_errors))
    for bundle in bundles:
        print(f"uninstalled: {targets[bundle.selector]}")
    return 0


def validate_command(raw: str) -> int:
    path = _normalize_abs(raw, expand_user=True, relative_ok=True)
    if path == SOURCE_ROOT:
        for bundle in (ADAPTIVE, HEAVY):
            validate_source(bundle)
        print(f"valid source suite: {path}")
        return 0
    for bundle in (ADAPTIVE, HEAVY):
        if path == bundle.source_root:
            validate_source(bundle)
            print(f"valid source bundle: {path}")
            return 0
        if path.name == bundle.skill_name:
            _validate_installed(path, bundle)
            print(f"valid installed bundle: {path}")
            return 0
    fail("LIFECYCLE_TARGET_INVALID", f"unrecognized validation path: {path}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    for name in ("install", "uninstall"):
        command = commands.add_parser(name)
        command.add_argument("--target", default=None)
        command.add_argument("--target-root", default=None)
        command.add_argument("--skills", choices=("adaptive", "heavy", "all"), default="adaptive")
        command.add_argument("--dry-run", action="store_true")
        if name == "install":
            command.add_argument("--replace", action="store_true")
    validate = commands.add_parser("validate")
    validate.add_argument("path")
    return result


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "install":
            return install(args.target, args.target_root, args.skills, args.dry_run, args.replace)
        if args.command == "uninstall":
            return uninstall(args.target, args.target_root, args.skills, args.dry_run)
        return validate_command(args.path)
    except LifecycleError as exc:
        print(f"error[{exc.code}]: {exc}", file=sys.stderr)
        return 2
    except (KeyboardInterrupt, BrokenPipeError):
        return 130
    except OSError as exc:
        print(f"error[LIFECYCLE_ACTIVATION_FAILED]: filesystem operation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
