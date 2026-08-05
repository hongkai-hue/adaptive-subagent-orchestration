#!/usr/bin/env python3
"""Create a safe, non-destructive Markdown scaffold for a heavy-goal flow."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import stat


SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PREFIX_RE = re.compile(r"^[A-Z][A-Z0-9]{0,7}$")


def fail(message: str) -> "NoReturn":
    raise SystemExit(f"error[HEAVY_SCAFFOLD_INVALID]: {message}")


def safe_root(raw: str) -> Path:
    supplied = Path(raw)
    if any(part == ".." for part in supplied.parts):
        fail("--root cannot contain '..'")
    root = supplied if supplied.is_absolute() else Path.cwd() / supplied
    root = Path(os.path.normpath(str(root)))
    if not root.is_dir():
        fail(f"project root does not exist: {root}")
    current = Path(root.anchor)
    for part in root.parts[1:]:
        current /= part
        try:
            mode = current.lstat().st_mode
        except OSError as exc:
            fail(f"cannot inspect root component {current}: {exc}")
        if stat.S_ISLNK(mode):
            fail(f"project root cannot traverse a symlink: {current}")
    return root


def required_markers(content: str) -> list[str]:
    return [
        line
        for line in content.splitlines()
        if line.startswith("## ")
        or line.startswith("| ID | Status |")
        or line.startswith("| Node | State |")
    ]


def ensure_inside(root: Path, path: Path) -> None:
    try:
        path.relative_to(root)
    except ValueError:
        fail(f"generated path escapes project root: {path}")
    current = root
    for part in path.relative_to(root).parts:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            continue
        except OSError as exc:
            fail(f"cannot inspect output path {current}: {exc}")
        if stat.S_ISLNK(mode):
            fail(f"output path cannot traverse a symlink: {current}")


def write_new(root: Path, path: Path, content: str, dry_run: bool) -> str:
    ensure_inside(root, path)
    if path.exists():
        if not path.is_file():
            fail(f"existing output is not a regular file: {path}")
        current = path.read_text(encoding="utf-8", errors="replace")
        missing = [marker for marker in required_markers(content) if marker not in current]
        suffix = f"; WARN missing: {', '.join(missing)}" if missing else ""
        return f"SKIP {path} (exists){suffix}"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        ensure_inside(root, path.parent)
        path.write_text(content, encoding="utf-8")
    return f"CREATE {path}"


def architecture(title: str) -> str:
    return f"""# {title} Architecture

## Context And Constraints
## Quality Attributes
## Module Responsibilities
## Data Flow And Trust Boundaries
## Failure Design And Recovery
## Deployment Units
## Decisions And Tradeoffs
## Parallelism Boundaries
## Architecture Gate

- [ ] Each module has one clear responsibility.
- [ ] Every cross-module interface is identified.
- [ ] Parallel and hard-dependent work is explicit.
- [ ] The architecture diagram HTML has been generated and inspected.
"""


def contract(title: str) -> str:
    return f"""# {title} Contract

- Version: v1
- Status: draft
- Owners: A0, A1

## Scope And Non-goals
## Inputs And Outputs
## Data Schema
## State Transitions
## Errors And Failure Ownership
## Authentication And Authorization
## Idempotency And Concurrency
## Compatibility And Migration
## Examples
## Contract Gate
"""


def dag(title: str, prefix: str) -> str:
    return f"""# {title} DAG

## Objective
## Architecture And Contract Inputs
## Flow

```mermaid
flowchart LR
  {prefix}00["{prefix}-00 Baseline"] --> {prefix}01["{prefix}-01 Architecture"]
  {prefix}01 --> {prefix}02["{prefix}-02 Contract"]
  {prefix}02 --> {prefix}03["{prefix}-03 Implementation"]
  {prefix}03 --> {prefix}04["{prefix}-04 Integration QA"]
  {prefix}04 --> {prefix}05["{prefix}-05 Manual release gate"]
```

## Waves

| Wave | Nodes | Parallel rule |
| --- | --- | --- |
| W0 | {prefix}-00 | Baseline only |
| W1 | {prefix}-01 | Architecture only |
| W2 | {prefix}-02 | Contract freeze |
| W3 | {prefix}-03 | Replace with domain nodes after contract acceptance |
| W4 | {prefix}-04 | Integration QA after implementation acceptance |
| W5 | {prefix}-05 | Manual release gate after QA acceptance |

## Nodes

Each node must define ID, owner, wave, dependencies, condition, exclusive write scope,
outputs, required/conditional/informational Gate, forbidden scope, failure owner, and retry.

## File Ownership

| Path / glob | Write owner | Readers | Notes |
| --- | --- | --- | --- |

## Manual Gates
## Conditions And Cancellation
"""


def status(title: str) -> str:
    return f"""# {title} Status

Last verified: not yet verified

| Node | State | Owner | Evidence | Attempts | Lease / agent | Blocker / next action |
| --- | --- | --- | --- | ---: | --- | --- |

## State Rules

`not_started / in_progress / blocked / ready_for_review / accepted / needs_rework / waiting_for_manual_gate / cancelled`

## Active Worker Registry

| Agent ID | Node | Base revision | Scope | Started | Lease expires | State |
| --- | --- | --- | --- | --- | --- | --- |

## Latest Recovery Check
"""


def questions() -> str:
    return """# Questions

| ID | Status | Class | Node | Affected branch | Question | Default decision | Adopted at | Answer | Impact |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""


def readiness(title: str) -> str:
    return f"""# {title} Release Readiness

## Decision

Not ready. This document is not a production release confirmation.

## Delivered Scope
## Node Evidence

| Node | Gate | Actual result | Evidence |
| --- | --- | --- | --- |

## Integration And Security Evidence
## Browser / Visual Evidence
## Persistence And Restart Evidence
## Open Questions And Defaults
## Residual Risks
## Rollback Or Disable Path
## Manual Release Steps
## Final Gate
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="Project root")
    parser.add_argument("--slug", required=True, help="Lowercase hyphenated flow slug")
    parser.add_argument("--title", required=True, help="Human-readable flow title")
    parser.add_argument("--prefix", required=True, help="Uppercase node prefix, e.g. FM")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = safe_root(args.root)
    if not SLUG_RE.fullmatch(args.slug):
        fail("--slug must use lowercase letters, digits, and single hyphens")
    if not PREFIX_RE.fullmatch(args.prefix):
        fail("--prefix must be 1-8 uppercase letters or digits, starting with a letter")

    files = {
        root / "docs" / "architecture" / f"{args.slug}-architecture.md": architecture(args.title),
        root / "docs" / "contracts" / f"{args.slug}-contract.md": contract(args.title),
        root / "docs" / "project" / f"{args.slug}-dag.md": dag(args.title, args.prefix),
        root / "docs" / "project" / f"{args.slug}-status.md": status(args.title),
        root / "docs" / "project" / "questions.md": questions(),
        root / "docs" / "project" / f"{args.slug}-release-readiness.md": readiness(args.title),
    }
    for path, content in files.items():
        print(write_new(root, path, content, args.dry_run))
    html_path = root / "docs" / "architecture" / f"{args.slug}-architecture.html"
    ensure_inside(root, html_path)
    if not html_path.exists():
        print(f"PENDING {html_path} (generate and inspect separately; Markdown scaffold only)")
    print("HEAVY_SCAFFOLD_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
