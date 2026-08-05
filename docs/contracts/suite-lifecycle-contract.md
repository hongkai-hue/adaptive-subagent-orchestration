# Suite Lifecycle Contract

- Version: v2
- Status: frozen
- Owners: lifecycle kernel, contract tests

## Scope And Non-goals

This contract installs, validates, replaces, and uninstalls the adaptive and heavy runtime bundles
from one repository. It preserves existing adaptive-only commands and adds an explicit atomic suite
operation. It does not modify host policy, credentials, account, provider, model, proxy, agent role
configuration, or project source files outside selected installed targets.

## Bundle Registry

The registry is machine-coded in `scripts/_lifecycle.py` and asserted here exactly:

| Selector | Skill name | Canonical source | Capability | Exact runtime files |
| --- | --- | --- | --- | --- |
| `adaptive` | `adaptive-subagent-orchestration` | repository root | `l3-source:l3-v1` | `SKILL.md`; `agents/openai.yaml` |
| `heavy` | `orchestrate-heavy-goals` | `skills/orchestrate-heavy-goals` | `l3-target:l3-v1` | `SKILL.md`; `agents/openai.yaml`; `references/architecture-baseline.md`; `references/diagram-baseline.md`; `references/artifact-templates.md`; `references/l3-handoff.md`; `references/node-contract.md`; `references/qa-gates.md`; `references/recovery.md`; `scripts/scaffold_flow.py` |

`all` selects adaptive followed by heavy. Runtime order is stable for staging, activation,
validation, rollback, and output. No runtime file is optional.

## Inputs And Outputs

```text
install --target user|repo [--skills adaptive|heavy|all] [--replace] [--dry-run]
install --target /absolute/path/adaptive-subagent-orchestration [--replace] [--dry-run]
install --target-root /absolute/skills-root --skills adaptive|heavy|all [--replace] [--dry-run]
uninstall --target user|repo [--skills adaptive|heavy|all] [--dry-run]
uninstall --target /absolute/path/adaptive-subagent-orchestration [--dry-run]
uninstall --target-root /absolute/skills-root --skills adaptive|heavy|all [--dry-run]
validate <suite-source-root | installed-skill-path>
```

`--skills` defaults to `adaptive`, preserving v0.1 behavior. The parser records `--target` as
unset; when neither target option is supplied it resolves to `user`. Only explicitly supplying both
`--target` and `--target-root` is an error, so `--target-root` never conflicts with an implicit
default. `--target-root` is not expanded from `~`; it must already be absolute, must not
contain `..`, must not be a symlink or traverse one, and must not equal or live within the canonical
source repository. The built-in `repo` target is the only permitted source-repository descendant
and resolves exactly to `<cwd>/.agents/skills`.

The legacy absolute `--target` form is accepted only with selector `adaptive`, and its final
component must be `adaptive-subagent-orchestration`. Heavy or multi-skill custom installation uses
`--target-root`. A target cannot equal either canonical source directory.

`validate` recognizes the repository suite root by the presence of both canonical source locations.
Otherwise, the validated directory's exact final component selects adaptive or heavy; any other
name fails. Installed validation requires a manifest, while source validation uses the registry.

Successful commands exit `0`. Contract, safety, conflict, or mutation failures exit `2` and begin
stderr with a stable error code such as `error[LIFECYCLE_TARGET_INVALID]:`. Output never includes
file content, credentials, or token values.

## Data Schema

Manifest v2 is written at `<installed-skill>/.install-manifest.json` with the exact top-level keys
and types below. Extra keys fail validation.

```json
{
  "schema_version": "2",
  "suite_name": "adaptive-subagent-orchestration",
  "skill_name": "orchestrate-heavy-goals",
  "installed_version": "0.2.0",
  "capabilities": ["l3-target:l3-v1"],
  "files": {
    "SKILL.md": "sha256:<64 lowercase hex>"
  }
}
```

- All scalar values are strings and equal the selected bundle registry constants.
- `capabilities` is a one-item string array equal to the selected registry capability.
- `files` is an object whose key set exactly equals the selected runtime allowlist and whose values
  match `sha256:[0-9a-f]{64}`.
- File keys are relative POSIX paths. Absolute paths, empty components, `.`, `..`, and backslashes
  fail validation.
- The generated manifest is lifecycle-owned metadata but is not included in its own checksum map.

An installed v1 or v2 tree may contain only the manifest, exact runtime files, and the parent directories
required by those files. Every entry must be a regular file or real directory; symlinks, unknown
files, unknown directories, sockets, and devices fail closed before replace or uninstall. Source
trees may contain repository-only files outside each canonical bundle root, but only allowlisted
runtime files are staged.

The reader accepts manifest v1 only for adaptive when all of these are exact: top-level keys
`schema_version`, `skill_name`, `installed_version`, `files`; schema `1`; skill name
`adaptive-subagent-orchestration`; version `0.1.0`; and files `SKILL.md`, `agents/openai.yaml` with
valid checksums. The writer emits only manifest v2.

## Target And Existing-state Matrix

| Operation | Existing state | Required result |
| --- | --- | --- |
| install one | selected target absent | install selected v2 bundle |
| install one | valid selected target present, no `--replace` | fail before staging |
| install one | valid selected target present with `--replace` | backup, replace, preserve backup |
| install one | target present without recognized valid manifest | fail; never replace private content |
| install all | both absent | install both |
| install all | one or both valid targets present, no `--replace` | fail before staging |
| install all | one valid target present with `--replace` | backup existing target, install both atomically |
| install all | both valid targets present with `--replace` | backup both, replace both atomically |
| install all | either target unrecognized, invalid, or checksum-drifted | fail and preserve both |
| uninstall one | selected target absent | report `not installed`, exit 0 |
| uninstall one | selected target valid | logical uninstall by directory staging, then cleanup |
| uninstall all | both absent | report suite not installed, exit 0 |
| uninstall all | exactly one target present | `LIFECYCLE_PARTIAL_SUITE`; delete nothing |
| uninstall all | both valid | logical uninstall both atomically, then cleanup |
| uninstall all | either target invalid or drifted | fail and delete nothing |

## Lock And Transaction Protocol

Every selector uses the same root lock:

`<skills-root>/.adaptive-subagent-orchestration-suite.lock`

The lock is a real directory created with mode `0700`. A single adaptive or heavy operation therefore
cannot race an `all` operation. Different skills roots are independent. Failure to remove a lock is
reported as cleanup debt and causes later operations to fail closed.

### Install / replace

1. Validate every selected canonical source before target directory creation.
2. Resolve targets and reject unsafe paths.
3. For dry-run, perform the full read-only preflight and return without creating root, lock, stage,
   backup, or manifest.
4. Create the skills root when needed, acquire the suite-root lock, and repeat target preflight.
5. Create one unique sibling stage per selected target; copy only its allowlist, preserve mode, write
   manifest v2, and validate the complete exact installed tree.
6. After every stage passes, rename each existing target to a unique sibling backup in registry
   order. No backup is deleted on successful replacement.
7. Rename every stage to its target in registry order, then validate both activated targets.
8. On any backup, activation, or post-activation validation failure: remove lifecycle-created new
   targets, restore backups in reverse registry order, remove remaining stages, and exit `2`.
9. If rollback cannot restore a target, preserve its backup or stage at the reported sibling path,
   emit `LIFECYCLE_ROLLBACK_INCOMPLETE`, and never report success.

### Uninstall

1. Resolve, lock, and validate all selected exact installed trees before renaming either target.
2. Rename each selected target to a unique sibling `.uninstall-*` directory in registry order. This
   is the logical uninstall transaction.
3. If any rename fails, restore already-renamed targets in reverse order and exit `2`.
4. After all selected targets are absent, recursively remove only the exact validated uninstall
   staging directories. Unknown content could not enter this phase because preflight rejects it.
5. If cleanup fails, the logical uninstall remains complete, the recoverable `.uninstall-*` path is
   reported with `LIFECYCLE_UNINSTALL_CLEANUP_PENDING`, and the command exits `2`. It does not
   recreate only one member of an `all` suite.

Internal wrappers for rename, tree removal, and installed validation are the fault-injection seams
used by standard-library unit mocks. No test-only environment flag exists in production CLI.

## Errors And Failure Ownership

| Code | Owner | Required behavior |
| --- | --- | --- |
| `LIFECYCLE_SOURCE_INVALID` | canonical bundle owner | stop before target mutation |
| `LIFECYCLE_TARGET_INVALID` | caller | reject path before directory creation |
| `LIFECYCLE_TARGET_EXISTS` | caller | require explicit `--replace` |
| `LIFECYCLE_PRIVATE_OR_DRIFTED` | target owner | preserve target and report validation reason |
| `LIFECYCLE_PARTIAL_SUITE` | target owner | delete nothing; choose single-skill or repair install |
| `LIFECYCLE_LOCKED` | lifecycle kernel | return non-zero without mutation |
| `LIFECYCLE_STAGE_FAILED` | lifecycle kernel | remove lifecycle-created stages only |
| `LIFECYCLE_ACTIVATION_FAILED` | lifecycle kernel | restore every prior target |
| `LIFECYCLE_ROLLBACK_INCOMPLETE` | lifecycle kernel | preserve and report recoverable sibling paths |
| `LIFECYCLE_UNINSTALL_CLEANUP_PENDING` | lifecycle kernel | targets remain absent; report cleanup path |

## Authentication And Authorization

The scripts operate only on explicitly selected skill targets. `--replace` authorizes replacement
only after manifest and checksum validation. `uninstall` authorizes removal only after the entire
installed tree exactly matches lifecycle-owned content. No command gains authority to edit host
policy or private configuration.

## Idempotency And Concurrency

Dry-run is mutation-free. Repeated install without `--replace` fails closed. The shared suite-root
lock serializes adaptive, heavy, and all mutations within one skills root. Staging, backup,
uninstall-staging, and lock names are sibling paths with collision-resistant suffixes.

## Compatibility And Migration

- Old `install.sh --target user|repo` remains adaptive-only.
- `--replace --skills adaptive` accepts and upgrades a valid adaptive v1 target to v2.
- `--replace --skills all` accepts a valid adaptive v1 target plus an absent heavy target and
  activates both v2 targets atomically.
- An existing heavy directory without a valid v2 manifest is private/unrecognized and is never
  silently replaced, even with `--replace`.
- Existing valid v2 targets may be replaced only when their exact skill/capability registry matches.
- No automatic migration occurs between legacy private skill roots and canonical user roots.
- Removing v1 read support or changing legacy command meaning requires a major release.

The adaptive parent considers bundled heavy compatible only when installed validation succeeds and
its manifest capability equals `l3-target:l3-v1`. A role name or directory alone is insufficient.

## Examples

`install.sh --target user --skills all --dry-run` reports two actions and creates nothing. The same
command installs two sibling v2 targets. If a heavy stage fails, neither target changes.

`uninstall.sh --target user --skills all` refuses a partial suite. A caller may explicitly uninstall
the one selected valid skill or repair the suite first.

## Contract Gate

- Tests assert the exact registry, manifest keys/types/capabilities, v1 reader, and v2 writer.
- Lifecycle tests cover parser defaults, the existing-state matrix, suite atomicity, rollback seams, root lock,
  symlink/path rejection, unknown entries, checksum drift, dry-run, and uninstall cleanup debt.
- Source validation covers both canonical bundles; installed validation uses exact directory name,
  manifest identity, capability, allowlist, tree shape, and checksums.
- Standard-library recursive tests and public privacy scans pass on a fresh clone.
