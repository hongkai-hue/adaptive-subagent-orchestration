# Adaptive Subagent Orchestration OSS Launch Contract

- Version: v1
- Status: frozen
- Owners: A0, A1

## Scope And Non-goals

This contract freezes the public v0.1 boundary between the canonical skill package,
lifecycle scripts, tests, installed bundle, Codex runtime, and release process.

In scope:

- Portable runtime skill and UI metadata.
- User, repository, and explicit custom installation targets.
- Dry-run, conflict-safe replacement, validation, backup, uninstall, and rollback
  instructions.
- Static contract tests, lifecycle tests, public cases, and sanitized forward evidence.
- CI and a manually authorized GitHub release.

Non-goals:

- Model/provider/API key/account/proxy configuration.
- Editing user `AGENTS.md` or custom agent TOML automatically.
- Reimplementing Codex subagent transport or a persistent DAG engine.
- Claiming deterministic implicit invocation or guaranteed performance gains.
- Supporting Windows in v0.1 without a real Windows implementation and Gate.

## Inputs And Outputs

### Runtime package

Inputs are canonical `SKILL.md` and `agents/openai.yaml`. The output is an installed
directory named `adaptive-subagent-orchestration` containing exact copies plus an
ownership manifest.

### Lifecycle command

Supported forms:

```text
scripts/install.sh [--target user|repo|ABSOLUTE_PATH] [--dry-run] [--replace]
scripts/uninstall.sh [--target user|repo|ABSOLUTE_PATH] [--dry-run]
scripts/validate.sh [SOURCE_OR_INSTALLED_SKILL]
```

Defaults:

- `user` resolves to `${HOME}/.agents/skills/adaptive-subagent-orchestration`.
- `repo` resolves from the current working directory to
  `.agents/skills/adaptive-subagent-orchestration`.
- A custom target must be absolute and must end in
  `adaptive-subagent-orchestration`.

Successful commands exit `0`. Contract, validation, safety, or mutation failures exit
non-zero and include an actionable message without secret or token values.

## Data Schema

### Install manifest

`.install-manifest.json` uses this v1 schema:

```json
{
  "schema_version": "1",
  "skill_name": "adaptive-subagent-orchestration",
  "installed_version": "0.1.0",
  "files": {
    "SKILL.md": "sha256:<hex>",
    "agents/openai.yaml": "sha256:<hex>"
  }
}
```

Only relative POSIX-style file keys are allowed. Absolute paths, `..`, symbolic-link
targets, account information, source checkout paths, and timestamps are forbidden.

### Public forward evidence

```yaml
date: YYYY-MM-DD
codex_version: "..."
surface: app | cli
os: "..."
scenario: "..."
expected_route: L0 | L1 | L2 | L3 | SERIAL | BLOCKED
observed_route: L0 | L1 | L2 | L3 | SERIAL | BLOCKED
roles_requested: []
runtime_identity: VERIFIED | UNVERIFIED
owned_paths: {}
changed_paths: []
validation_commands: []
exit_codes: []
result: PASS | FAIL | BLOCKED
residual_risks: []
```

Provider names, model names, account details, API endpoints, tokens, private source
paths, and private logs are forbidden in public evidence.

## State Transitions

### Install lifecycle

```text
absent -> staged -> validated -> installed
installed -> staged_replacement -> validated -> backup_created -> replaced
installed -> manifest_verified -> uninstalled
installed -> modified_owned_file -> blocked
any staging/validation failure -> unchanged_current_state
```

The script must not report success before the final target exists, validates, and its
manifest checksums match.

### Release lifecycle

```text
local_candidate -> integration_passed -> waiting_for_manual_gate
waiting_for_manual_gate -> published_candidate  (explicit authorization only)
published_candidate -> fresh_clone_verified -> released
any required Gate failure -> needs_rework
```

## Errors And Failure Ownership

| Error class | Example | Failure owner |
| --- | --- | --- |
| Contract | malformed frontmatter or manifest | Runtime/contract node |
| Scope | target not explicit or wrong basename | Lifecycle node |
| Conflict | existing install without `--replace` | Caller decision; no mutation |
| Verification | staged or installed validation fails | Owning implementation node |
| Privacy | sensitive pattern or absolute maintainer path found | Documentation/integration owner |
| Runtime | Codex surface does not match documented behavior | Evidence owner; mark limitation |
| Publication | remote permissions, CI, or fresh clone fails | Release node; do not claim release |

No error may be swallowed or converted to PASS. `NOT_RUN` cannot satisfy a required Gate.

## Authentication And Authorization

Local lifecycle commands require only filesystem permissions for their exact target.
They never request or store an OpenAI or GitHub credential.

GitHub authentication is used only by the manual publication node. Repository creation,
push, tag, Release, and promotion require explicit authorization for the exact account
and repository. Tokens must not appear in command output, logs, manifests, or docs.

## Idempotency And Concurrency

- Re-running install against an existing target without `--replace` is a no-op failure.
- Dry-run is side-effect free and may be repeated.
- Replacement writes to one unique staging directory and one unique backup.
- Install/uninstall acquire an adjacent lock directory; a second mutation exits rather
  than racing.
- Uninstall deletes only manifest-owned files whose current checksums match.
- Parallel installers for the same target are unsupported and must fail closed.
- Different targets may be operated independently.

## Compatibility And Migration

- Contract schema v1 and manifest schema v1 are stable for the v0.1 line.
- The canonical public user install path is `~/.agents/skills` and the repository path
  is `.agents/skills`, matching current Codex documentation.
- Existing private `~/.codex/skills` installs are not migrated automatically. A custom
  absolute target can be used only when explicitly requested.
- Breaking manifest or routing-contract changes require a SemVer major release.
- A future plugin may consume the same runtime files but cannot silently change this
  lifecycle contract.

## Examples

```bash
./scripts/install.sh --target user --dry-run
./scripts/install.sh --target user
./scripts/validate.sh "$HOME/.agents/skills/adaptive-subagent-orchestration"
./scripts/uninstall.sh --target user --dry-run
```

Repository-scoped install:

```bash
./scripts/install.sh --target repo
```

Existing install behavior:

```text
install without --replace -> non-zero, no files changed
install with --replace -> validate staging, create backup, replace atomically
uninstall after user edit -> non-zero, preserve edited file
```

## Contract Gate

Required Gate:

```bash
python3 -m unittest discover -s tests -v
```

Expected: exit `0`, recursive discovery includes contract, lifecycle, privacy, and docs
tests. Contract changes invalidate every downstream implementation and QA acceptance.
