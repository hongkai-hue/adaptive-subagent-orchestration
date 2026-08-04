#!/usr/bin/env python3
"""Dependency-free lifecycle implementation for the skill bundle."""

from __future__ import annotations

import argparse
import contextlib
import datetime as _datetime
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import sys
from typing import Dict, Iterator, Optional, Tuple


SKILL_NAME = "adaptive-subagent-orchestration"
INSTALLED_VERSION = "0.1.0"
MANIFEST_NAME = ".install-manifest.json"
RUNTIME_FILES = ("SKILL.md", "agents/openai.yaml")
MANIFEST_KEYS = {"schema_version", "skill_name", "installed_version", "files"}
FILE_HASH_RE = re.compile(r"\Asha256:[0-9a-f]{64}\Z")


class LifecycleError(Exception):
    """An expected, actionable lifecycle failure."""


SOURCE_ROOT = Path(__file__).resolve().parent.parent


def _lstat(path: Path):
    try:
        return path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise LifecycleError(f"cannot inspect path {path}: {exc.strerror or exc}") from exc


def _is_symlink(path: Path) -> bool:
    st = _lstat(path)
    return st is not None and stat.S_ISLNK(st.st_mode)


def _reject_symlink_components(path: Path) -> None:
    """Reject symlinks in every existing target/parent component."""

    if not path.is_absolute():
        raise LifecycleError(f"target path must be absolute: {path}")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        st = _lstat(current)
        if st is not None and stat.S_ISLNK(st.st_mode):
            raise LifecycleError(f"target or parent is a symlink: {current}")


def _ensure_directory_chain(path: Path) -> None:
    """Create missing directories one component at a time without following links."""

    if not path.is_absolute():
        raise LifecycleError(f"directory path must be absolute: {path}")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        st = _lstat(current)
        if st is None:
            try:
                os.mkdir(current, 0o755)
            except FileExistsError:
                st = _lstat(current)
            except OSError as exc:
                raise LifecycleError(
                    f"cannot create directory {current}: {exc.strerror or exc}"
                ) from exc
            if st is None:
                st = _lstat(current)
        if st is None:
            raise LifecycleError(f"cannot inspect created directory {current}")
        if stat.S_ISLNK(st.st_mode):
            raise LifecycleError(f"target or parent is a symlink: {current}")
        if not stat.S_ISDIR(st.st_mode):
            raise LifecycleError(f"target parent is not a directory: {current}")


def _require_directory(path: Path, label: str) -> None:
    st = _lstat(path)
    if st is None:
        raise LifecycleError(f"{label} does not exist: {path}")
    if stat.S_ISLNK(st.st_mode):
        raise LifecycleError(f"{label} is a symlink: {path}")
    if not stat.S_ISDIR(st.st_mode):
        raise LifecycleError(f"{label} is not a directory: {path}")


def _require_regular(path: Path, label: str) -> None:
    st = _lstat(path)
    if st is None:
        raise LifecycleError(f"{label} is missing: {path}")
    if stat.S_ISLNK(st.st_mode):
        raise LifecycleError(f"{label} is a symlink: {path}")
    if not stat.S_ISREG(st.st_mode):
        raise LifecycleError(f"{label} is not a regular file: {path}")


def _absolute_input(raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    return Path(os.path.normpath(str(path)))


def resolve_target(raw: str) -> Path:
    """Resolve a contract target while retaining lexical safety checks."""

    if raw == "user":
        home_raw = os.environ.get("HOME")
        if not home_raw:
            raise LifecycleError("HOME is required for --target user")
        home = _absolute_input(home_raw)
        target = home / ".agents" / "skills" / SKILL_NAME
    elif raw == "repo":
        target = Path.cwd() / ".agents" / "skills" / SKILL_NAME
    else:
        supplied = Path(raw).expanduser()
        if not supplied.is_absolute():
            raise LifecycleError(
                "custom --target must be an absolute path ending in " + SKILL_NAME
            )
        if any(part == ".." for part in supplied.parts):
            raise LifecycleError("custom --target cannot contain '..'")
        target = Path(os.path.normpath(str(supplied)))

    if target.name != SKILL_NAME:
        raise LifecycleError(f"target must end in {SKILL_NAME}: {target}")
    if any(part == ".." for part in target.parts):
        raise LifecycleError("target cannot contain '..'")
    _reject_symlink_components(target)

    source = SOURCE_ROOT
    if target == source:
        raise LifecycleError("target cannot be the source repository root")
    return target


def _validate_frontmatter(path: Path) -> None:
    _require_regular(path, "SKILL.md")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise LifecycleError(f"cannot read SKILL.md: {exc}") from exc
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if match is None:
        raise LifecycleError("SKILL.md is missing valid YAML frontmatter")
    keys = []
    values = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        if line[:1].isspace() or ":" not in line:
            raise LifecycleError("SKILL.md frontmatter must contain only name and description")
        key, value = line.split(":", 1)
        key = key.strip()
        if key not in {"name", "description"} or key in values:
            raise LifecycleError("SKILL.md frontmatter must contain only name and description")
        values[key] = value.strip()
        keys.append(key)
    if keys != ["name", "description"] or values.get("name") != SKILL_NAME:
        raise LifecycleError("SKILL.md frontmatter name/description contract failed")
    if not values.get("description"):
        raise LifecycleError("SKILL.md frontmatter description is empty")


def _validate_openai_yaml(path: Path) -> None:
    _require_regular(path, "agents/openai.yaml")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise LifecycleError(f"cannot read agents/openai.yaml: {exc}") from exc
    if not text.strip() or "interface:" not in text:
        raise LifecycleError("agents/openai.yaml is empty or malformed")


def sha256_file(path: Path) -> str:
    _require_regular(path, str(path))
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise LifecycleError(f"cannot hash {path}: {exc.strerror or exc}") from exc
    return digest.hexdigest()


def _read_manifest(path: Path) -> Dict[str, object]:
    _require_regular(path, MANIFEST_NAME)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LifecycleError(f"invalid {MANIFEST_NAME}: {exc}") from exc
    if not isinstance(data, dict) or set(data) != MANIFEST_KEYS:
        raise LifecycleError(f"{MANIFEST_NAME} has an invalid v1 shape")
    if data.get("schema_version") != "1":
        raise LifecycleError(f"{MANIFEST_NAME} schema_version must be '1'")
    if data.get("skill_name") != SKILL_NAME:
        raise LifecycleError(f"{MANIFEST_NAME} skill_name is invalid")
    if data.get("installed_version") != INSTALLED_VERSION:
        raise LifecycleError(f"{MANIFEST_NAME} installed_version is invalid")
    files = data.get("files")
    if not isinstance(files, dict) or set(files) != set(RUNTIME_FILES):
        raise LifecycleError(f"{MANIFEST_NAME} must own only SKILL.md and agents/openai.yaml")
    for rel in RUNTIME_FILES:
        value = files.get(rel)
        if not isinstance(value, str) or FILE_HASH_RE.fullmatch(value) is None:
            raise LifecycleError(f"{MANIFEST_NAME} has an invalid checksum for {rel}")
    return data


def validate_bundle(path: Path, require_manifest: bool = False) -> Tuple[str, Optional[Dict[str, object]]]:
    """Validate source or installed runtime files and, when present, checksums."""

    path = _absolute_input(str(path))
    _reject_symlink_components(path)
    _require_directory(path, "skill directory")
    _validate_frontmatter(path / "SKILL.md")
    _validate_openai_yaml(path / "agents" / "openai.yaml")

    manifest_path = path / MANIFEST_NAME
    manifest_stat = _lstat(manifest_path)
    if manifest_stat is None:
        if require_manifest:
            raise LifecycleError(f"{MANIFEST_NAME} is missing: {path}")
        return "source", None
    manifest = _read_manifest(manifest_path)
    files = manifest["files"]
    assert isinstance(files, dict)
    for rel in RUNTIME_FILES:
        expected = files[rel]
        assert isinstance(expected, str)
        actual = "sha256:" + sha256_file(path / rel)
        if actual != expected:
            raise LifecycleError(f"owned file checksum mismatch: {path / rel}")
    return "installed", manifest


def _stamp() -> str:
    return _datetime.datetime.now(_datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _unique_sibling(target: Path, kind: str) -> Path:
    for _ in range(100):
        token = secrets.token_hex(5)
        if kind == "backup":
            name = f"{target.name}.backup-{_stamp()}-{token}"
        else:
            name = f".{target.name}.{kind}-{_stamp()}-{token}"
        candidate = target.parent / name
        if _lstat(candidate) is None:
            return candidate
    raise LifecycleError(f"cannot allocate unique {kind} path beside {target}")


@contextlib.contextmanager
def target_lock(target: Path) -> Iterator[None]:
    lock = target.parent / f".{target.name}.lock"
    if _lstat(lock) is not None:
        raise LifecycleError(f"target is locked by another lifecycle operation: {target}")
    try:
        os.mkdir(lock, 0o700)
    except FileExistsError as exc:
        raise LifecycleError(f"target is locked by another lifecycle operation: {target}") from exc
    except OSError as exc:
        raise LifecycleError(f"cannot acquire target lock {lock}: {exc.strerror or exc}") from exc
    try:
        yield
    finally:
        try:
            os.rmdir(lock)
        except FileNotFoundError:
            pass
        except OSError:
            # A lock directory is ours, but a cleanup failure must not hide the
            # operation result. The next invocation will fail closed on the lock.
            pass


def _copy_runtime(stage: Path) -> None:
    stage.mkdir(mode=0o755)
    agents = stage / "agents"
    agents.mkdir(mode=0o755)
    for rel in RUNTIME_FILES:
        source = SOURCE_ROOT / rel
        _require_regular(source, f"source {rel}")
        destination = stage / rel
        try:
            shutil.copyfile(source, destination)
            shutil.copymode(source, destination)
        except OSError as exc:
            raise LifecycleError(f"cannot stage {rel}: {exc.strerror or exc}") from exc

    manifest = {
        "schema_version": "1",
        "skill_name": SKILL_NAME,
        "installed_version": INSTALLED_VERSION,
        "files": {
            "SKILL.md": "sha256:" + sha256_file(stage / "SKILL.md"),
            "agents/openai.yaml": "sha256:" + sha256_file(stage / "agents" / "openai.yaml"),
        },
    }
    try:
        (stage / MANIFEST_NAME).write_text(
            json.dumps(manifest, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        raise LifecycleError(f"cannot write {MANIFEST_NAME}: {exc.strerror or exc}") from exc


def _remove_created_stage(stage: Optional[Path]) -> None:
    if stage is None:
        return
    st = _lstat(stage)
    if st is None:
        return
    if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
        return
    try:
        shutil.rmtree(stage)
    except OSError:
        pass


def _target_exists(target: Path) -> bool:
    return _lstat(target) is not None


def _check_existing_install(target: Path) -> None:
    _require_directory(target, "existing target")
    validate_bundle(target, require_manifest=True)


def _rollback_replace(target: Path, backup: Optional[Path]) -> None:
    if backup is None:
        return
    current = _lstat(target)
    if current is not None:
        if stat.S_ISDIR(current.st_mode) and not stat.S_ISLNK(current.st_mode):
            _remove_created_stage(target)
        else:
            try:
                target.unlink()
            except OSError:
                pass
    if _lstat(backup) is not None and _lstat(target) is None:
        try:
            os.rename(backup, target)
        except OSError:
            pass


def install(raw_target: str, dry_run: bool, replace: bool) -> int:
    # Validate canonical inputs before any target mutation.
    validate_bundle(SOURCE_ROOT)
    target = resolve_target(raw_target)
    exists = _target_exists(target)
    if exists and not replace:
        raise LifecycleError(f"target already exists; rerun with --replace: {target}")

    if dry_run:
        if exists:
            _check_existing_install(target)
            print(f"dry-run: would replace {target}")
        else:
            print(f"dry-run: would install {target}")
        return 0

    _ensure_directory_chain(target.parent)
    stage: Optional[Path] = None
    backup: Optional[Path] = None
    with target_lock(target):
        # Re-check state after locking so an external mutation cannot turn a
        # no-op conflict into an overwrite.
        exists = _target_exists(target)
        if exists and not replace:
            raise LifecycleError(f"target already exists; rerun with --replace: {target}")
        if exists:
            _check_existing_install(target)
        try:
            stage = _unique_sibling(target, "staging")
            _copy_runtime(stage)
            validate_bundle(stage, require_manifest=True)

            if _target_exists(target):
                if not replace:
                    raise LifecycleError(f"target appeared during install: {target}")
                backup = _unique_sibling(target, "backup")
                os.rename(target, backup)
                try:
                    os.rename(stage, target)
                    stage = None
                except OSError as exc:
                    _rollback_replace(target, backup)
                    raise LifecycleError(
                        f"replacement failed; backup preserved at {backup}: {exc.strerror or exc}"
                    ) from exc
            else:
                os.rename(stage, target)
                stage = None

            try:
                validate_bundle(target, require_manifest=True)
            except LifecycleError:
                if backup is not None:
                    _rollback_replace(target, backup)
                else:
                    _remove_created_stage(target)
                raise
        finally:
            _remove_created_stage(stage)

    if backup is not None:
        print(f"installed: {target} (backup: {backup})")
    else:
        print(f"installed: {target}")
    return 0


def _remove_owned_files(target: Path) -> None:
    for rel in RUNTIME_FILES:
        path = target / rel
        _require_regular(path, rel)
    manifest = target / MANIFEST_NAME
    _require_regular(manifest, MANIFEST_NAME)
    for rel in RUNTIME_FILES:
        (target / rel).unlink()
    manifest.unlink()
    agents = target / "agents"
    if _lstat(agents) is not None:
        st = _lstat(agents)
        if st is not None and stat.S_ISDIR(st.st_mode) and not stat.S_ISLNK(st.st_mode):
            try:
                agents.rmdir()
            except OSError:
                pass
    try:
        target.rmdir()
    except OSError:
        pass


def uninstall(raw_target: str, dry_run: bool) -> int:
    target = resolve_target(raw_target)
    if not _target_exists(target):
        print(f"not installed: {target}")
        return 0
    _require_directory(target, "installed target")

    if dry_run:
        validate_bundle(target, require_manifest=True)
        print(f"dry-run: would uninstall {target}")
        return 0

    with target_lock(target):
        if not _target_exists(target):
            print(f"not installed: {target}")
            return 0
        _require_directory(target, "installed target")
        # Validation performs the complete checksum preflight. Nothing is
        # deleted if either owned file was modified or the manifest is invalid.
        validate_bundle(target, require_manifest=True)
        _remove_owned_files(target)
    print(f"uninstalled: {target}")
    return 0


def validate_command(raw_path: str) -> int:
    path = _absolute_input(raw_path)
    kind, _ = validate_bundle(path)
    print(f"valid {kind} bundle: {path}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the skill runtime bundle")
    sub = parser.add_subparsers(dest="command", required=True)

    install_parser = sub.add_parser("install")
    install_parser.add_argument("--target", default="user")
    install_parser.add_argument("--dry-run", action="store_true")
    install_parser.add_argument("--replace", action="store_true")

    uninstall_parser = sub.add_parser("uninstall")
    uninstall_parser.add_argument("--target", default="user")
    uninstall_parser.add_argument("--dry-run", action="store_true")

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("path")
    return parser


def main(argv=None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "install":
            return install(args.target, args.dry_run, args.replace)
        if args.command == "uninstall":
            return uninstall(args.target, args.dry_run)
        if args.command == "validate":
            return validate_command(args.path)
        raise LifecycleError("unknown lifecycle command")
    except LifecycleError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except (KeyboardInterrupt, BrokenPipeError):
        return 130
    except OSError as exc:
        print(f"error: filesystem operation failed: {exc.strerror or exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
