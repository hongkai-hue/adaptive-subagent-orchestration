# Adaptive Subagent Orchestration

Route a medium Codex task to the smallest useful set of lanes, keep one owner for each writable path, and finish with evidence that the parent agent can verify. This repository is the canonical source for the skill, its UI metadata, lifecycle scripts, tests, and public guidance. It is a workflow contract, not a scheduler or a replacement for the Codex runtime.

**Current support status:** v0.1.0 release-ready. The public repository, GitHub Actions matrix, and fresh-clone lifecycle Gate have passed; the version tag and Release are the remaining publication steps. Static contracts, lifecycle behavior, and selected forward cases are covered by the repository tests. A sanitized desktop forward record covers representative routing and result collection. Complete App/CLI and OS coverage, implicit triggering, and request-level runtime identity remain unverified; see the [runtime surface matrix](docs/runtime-surface-matrix.md).

## What changes

| Without this skill | With this skill |
| --- | --- |
| Decide ad hoc whether to delegate. | Start with L0-L3 routing criteria and a documented handoff boundary. |
| Let multiple writers discover ownership while editing. | Assign every writable path to one owner for the full run. |
| Treat a completed transport call as success. | Require a structured result, changed paths, verification, evidence, and residual risk. |
| Reuse stale evidence after the candidate changes. | Invalidate the old pass and rerun the final Gate. |
| Retry without a changed diagnosis. | Allow at most one focused retry with a concrete Delta and the same owner/scope. |

The competing-lane distinction matters: disjoint, independently testable write scopes can be L2; a shared hotspot, strict dependency, sensitive context, migration, or release stays serial on the main thread. A cross-module contract or multi-wave DAG is an L3 handoff to heavy orchestration.

## Routing levels

| Level | Use when | Agents | Outcome |
| --- | --- | ---: | --- |
| **L0** | One small or ordered task has no useful independent lane. | 0 | The parent works and runs the final Gate. |
| **L1** | Two independent read-only investigations materially reduce uncertainty. | 1-2 `explorer` | Each lane returns paths, lines, command output, or a clear blocker. |
| **L2** | Two or more implementation lanes have disjoint scopes and independent Gates. | 1-3 `worker`/`default` | The parent integrates, rechecks ownership, and runs the final Gate. |
| **L3** | The work spans modules, freezes a contract, or needs waves, recovery, or release readiness. | 0 here | Hand off to `orchestrate-heavy-goals`; do not run two orchestrators. |

The limit is one to three subagents per dispatch batch. Capacity, ownership, privacy, and dependency checks can still force `SERIAL` or `BLOCKED`.

## Use it explicitly

In a Codex task, invoke the skill by name:

```text
Use $adaptive-subagent-orchestration to assess this task, create only worthwhile independent lanes, and integrate verified results.
```

The UI metadata permits implicit eligibility, but it cannot make triggering deterministic. Explicit invocation is the reliable path. An optional rule can be copied manually into a repository or user `AGENTS.md`; the installer never edits those files. See [templates/AGENTS-routing.md](templates/AGENTS-routing.md).

## Install safely

The package itself has no third-party runtime dependency and does not configure an account, provider, model, proxy, API key, or token. Codex supplies skill discovery and subagent capabilities. The scripts only manage the two runtime files and an ownership manifest.

Preview a user install:

```bash
./scripts/install.sh --target user --dry-run
```

Install into the canonical user or current repository scope:

```bash
./scripts/install.sh --target user
./scripts/install.sh --target repo
```

For a custom location, pass an absolute path whose final component is exactly `adaptive-subagent-orchestration`:

```bash
./scripts/install.sh --target /absolute/path/adaptive-subagent-orchestration --dry-run
./scripts/install.sh --target /absolute/path/adaptive-subagent-orchestration
```

The default user target is `$HOME/.agents/skills/adaptive-subagent-orchestration`; the repository target is `.agents/skills/adaptive-subagent-orchestration` below the current working directory. Existing targets are never overwritten silently. Run with `--replace` only after reviewing the target:

```bash
./scripts/install.sh --target user --replace
```

Replacement validates the existing manifest, stages and validates a fresh bundle, renames the old directory to a timestamped sibling backup, and validates the final target before reporting success. A failed replacement keeps the backup and reports its path. The manifest owns only `SKILL.md` and `agents/openai.yaml`.

Validate a source or installed bundle:

```bash
./scripts/validate.sh .
./scripts/validate.sh "$HOME/.agents/skills/adaptive-subagent-orchestration"
```

Uninstall is dry-run capable and fail-closed. It removes only manifest-owned files whose checksums still match; a modified owned file, malformed manifest, symlink escape, or lock conflict blocks deletion and leaves the target in place:

```bash
./scripts/uninstall.sh --target user --dry-run
./scripts/uninstall.sh --target user
```

Private legacy installs are not migrated automatically. Use an explicit custom target only when you intend to operate on it. Do not point a target at this source checkout.

## Cases

Read the two small public cases before splitting work:

- [Independent write lanes](docs/cases/independent-write-lanes.md) shows an L2 split with disjoint owners and separate Gates.
- [Shared hotspot serial](docs/cases/shared-hotspot-serial.md) shows why two writers touching one file stay on the main thread.

The cases are contract examples, not performance promises. Token budgets, conflicts, task duration, and runtime scheduling remain host- and task-dependent.

## Support and limitations

- **Account/provider/model neutrality:** no account, provider, model, proxy, API key, or token configuration is read, written, or inferred by this repository. Static metadata is not request-level runtime identity.
- **Implicit invocation:** `allow_implicit_invocation` expresses eligibility only. Codex may choose not to trigger a skill; explicit `$adaptive-subagent-orchestration` invocation is recommended.
- **Runtime identity:** exact provider, model, account, and reasoning identity are `UNVERIFIED` unless a sanitized request-level record proves them. Never infer them from role names or local configuration.
- **Conflicts and tokens:** the skill can classify shared ownership and note token or context limits, but it cannot reserve files, guarantee token availability, or promise speed, cost, or quality improvements.
- **Runtime boundary:** Codex, not this repository, creates, waits for, and closes subagents. Transport completion is not a business `PASS`; the parent must inspect the structured result and rerun any invalidated Gate.
- **Platform status:** the [runtime surface matrix](docs/runtime-surface-matrix.md) distinguishes static and forward evidence from unverified App, CLI, and OS coverage. Windows is outside the v0.1 support claim.

## Development

The canonical source is this repository. The runtime bundle is limited to `SKILL.md`, `agents/openai.yaml`, and `.install-manifest.json` after installation; tests and docs are not copied into it.

Run the standard-library test suite and source validation:

```bash
python3 -m unittest discover -s tests -v
./scripts/validate.sh .
python3 -m compileall -q scripts
git diff --check
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before opening a change. The project is published under Apache-2.0 at `https://github.com/hongkai-hue/adaptive-subagent-orchestration`.

## Repository map

- [`SKILL.md`](SKILL.md) is the English runtime routing contract.
- [`agents/openai.yaml`](agents/openai.yaml) contains discovery and invocation metadata.
- [`scripts/`](scripts/) contains install, validate, and uninstall entry points.
- [`docs/contracts/oss-launch-contract.md`](docs/contracts/oss-launch-contract.md) freezes the v1 lifecycle boundary.
- [`docs/architecture/oss-launch-architecture.md`](docs/architecture/oss-launch-architecture.md) explains module ownership and trust boundaries.
- [`docs/runtime-surface-matrix.md`](docs/runtime-surface-matrix.md) records current evidence and limitations.
- [`tests/forward-test-record.md`](tests/forward-test-record.md) is the sanitized forward evidence record.
