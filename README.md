# Adaptive Subagent Orchestration

Route a medium Codex task to the smallest useful set of lanes, keep one owner for each writable path, and finish with evidence that the parent agent can verify. This repository is the canonical source for the skill, its UI metadata, lifecycle scripts, tests, and public guidance. It is a workflow contract, not a scheduler or a replacement for the Codex runtime.

**Current support status:** v0.2.0 is the current release. It keeps balanced routing as the default, retains opt-in D1 compute offload, and bundles `orchestrate-heavy-goals` so L3 has a versioned, testable execution path in the same repository. Static contracts, atomic suite lifecycle behavior, and forward fixtures are covered by repository tests. Request-level D1/L3 execution across every App/CLI and OS surface, implicit triggering, and runtime identity remain unverified. See the [runtime surface matrix](docs/runtime-surface-matrix.md).

![Abstract parent hub routing work through two isolated lanes and merging two evidence tokens into one result.](docs/assets/readme/hero-orchestration.webp)

*Figure 1. One parent keeps control while two isolated lanes return evidence to a single result.*

## What changes

| Without this skill | With this skill |
| --- | --- |
| Decide ad hoc whether to delegate. | Start with L0/D1/L1/L2/L3 routing criteria and a documented handoff boundary. |
| Let multiple writers discover ownership while editing. | Assign every writable path to one owner for the full run. |
| Treat a completed transport call as success. | Require a structured result, changed paths, verification, evidence, and residual risk. |
| Reuse stale evidence after the candidate changes. | Invalidate the old pass and rerun the final Gate. |
| Retry without a changed diagnosis. | Allow at most one focused retry with a concrete Delta and the same owner/scope. |

![Disjoint L2 write lanes with independent Gates compared with a shared-hotspot serial path.](docs/assets/readme/ownership-boundaries.svg)

*Figure 2. Independent scopes can use L2; a shared writable path stays serial on the parent.*

The competing-lane distinction matters: one bounded implementation can use opt-in D1, while disjoint, independently testable write scopes can use L2. A shared hotspot, strict dependency, sensitive context, migration, or release stays serial on the main thread. A cross-module contract or multi-wave DAG is an L3 handoff to heavy orchestration.

## Routing levels

![Balanced and compute-offload routing from L0 local work through D1 single-worker offload, L1 exploration, L2 parallel implementation, and L3 heavy handoff.](docs/assets/readme/routing-levels.svg)

*Figure 3. Choose the smallest routing level that creates a useful independent lane.*

| Level | Use when | Agents | Outcome |
| --- | --- | ---: | --- |
| **L0** | One small or ordered task has no useful independent lane. | 0 | The parent works and runs the final Gate. |
| **D1** | In explicit `compute-offload` mode, one non-trivial implementation has an exact owner, bounded write scope, reproducible Gate, and positive delegation value. | 1 `worker`, sequential | The worker implements; the parent inspects and reruns the final Gate. Work below five minutes stays L0. |
| **L1** | Two independent read-only investigations materially reduce uncertainty. | 1-2 `explorer` | Each lane returns paths, lines, command output, or a clear blocker. |
| **L2** | Two or more implementation lanes have disjoint scopes and independent Gates. | 1-3 `worker`/`default` | The parent integrates, rechecks ownership, and runs the final Gate. |
| **L3** | The work spans modules, freezes a contract, or needs waves, recovery, or release readiness. | Parent A0 + bounded domain/QA agents | Close adaptive lanes, transfer one `l3-v1` packet, then run the bundled heavy architecture → contract → DAG → implementation → QA flow. |

`balanced` is the default and keeps ordinary single-lane work in L0. `compute-offload` is explicit and adds D1 for work estimated at least 10 minutes or with a recorded context-isolation benefit. A D1 discovery `explorer`, implementation `worker`, and optional read-only reviewer run sequentially, never simultaneously. Capacity, ownership, privacy, and dependency checks can still force `SERIAL` or `BLOCKED`.

## Use it explicitly

In a Codex task, invoke the skill by name:

```text
Use $adaptive-subagent-orchestration to assess this task, create only worthwhile independent lanes, and integrate verified results.
```

To offload one bounded daily implementation, select the mode explicitly:

```text
Use $adaptive-subagent-orchestration in compute-offload mode. Give one worker the exact owned scope and Gate, then inspect the result and rerun the final Gate in the parent.
```

To start a heavy goal directly, or after an adaptive L3 decision:

```text
Use $orchestrate-heavy-goals to establish the architecture, freeze contracts, build the wave DAG, execute bounded nodes, recover from drift, and produce verified release readiness. Stop at every manual Gate.
```

Adaptive and heavy keep one parent-thread orchestrator. A valid `l3-v1` handoff closes adaptive ownership before heavy A0 starts; unknown fields, active lanes, sensitive context, digest mismatch, baseline drift, or a missing heavy capability fail closed. See the [L3 handoff contract](docs/contracts/l3-handoff-contract.md).

![Sequence from user goal through parent preflight, bounded lane work, structured result inspection, and the parent final Gate.](docs/assets/readme/parent-agent-sequence.svg)

*Figure 4. Transport completion is not business PASS; the parent inspects, integrates, and verifies.*

The UI metadata permits implicit eligibility, but it cannot make triggering deterministic. Explicit invocation is the reliable path. An optional rule can be copied manually into a repository or user `AGENTS.md`; the installer never edits those files. See [templates/AGENTS-routing.md](templates/AGENTS-routing.md).

## Install safely

![Fail-closed lifecycle covering target preflight, staging, validation, install, explicit replacement with backup, and checksum-safe uninstall.](docs/assets/readme/install-lifecycle.svg)

*Figure 5. Lifecycle scripts mutate only after validation and preserve the target on uncertainty.*

The package itself has no third-party runtime dependency and does not configure an account, provider, model, proxy, API key, or token. Codex supplies skill discovery and subagent capabilities. The lifecycle registry manages two exact runtime allowlists and one checksum manifest per installed skill.

Preview the recommended complete-suite install:

```bash
./scripts/install.sh --target user --skills all --dry-run
```

Install both skills into the canonical user or current repository scope:

```bash
./scripts/install.sh --target user --skills all
./scripts/install.sh --target repo --skills all
```

`--skills adaptive` remains the default for v0.1 command compatibility; use `--skills heavy` for only the heavy runtime. The recommended closed-loop setup is `--skills all`.

For a custom suite root, pass an absolute skills directory:

```bash
./scripts/install.sh --target-root /absolute/path/to/skills --skills all --dry-run
./scripts/install.sh --target-root /absolute/path/to/skills --skills all
```

The legacy absolute `--target /absolute/path/adaptive-subagent-orchestration` remains adaptive-only. The default user root is `$HOME/.agents/skills`; the repository root is `.agents/skills` below the current working directory. Existing targets are never overwritten silently. Run with `--replace` only after reviewing every selected target:

```bash
./scripts/install.sh --target user --skills all --replace
```

Replacement validates all selected manifests and exact tree shapes, stages every bundle, creates each timestamped sibling backup, then activates and validates the suite atomically. A failure rolls all selected targets back; an unrecognized private directory is never replaced. Manifest v2 records exact files and the `l3-source:l3-v1` or `l3-target:l3-v1` capability.

Validate a source or installed bundle:

```bash
./scripts/validate.sh .
./scripts/validate.sh "$HOME/.agents/skills/adaptive-subagent-orchestration"
./scripts/validate.sh "$HOME/.agents/skills/orchestrate-heavy-goals"
```

Uninstall is dry-run capable and fail-closed. It removes only manifest-owned files whose checksums still match; a modified owned file, malformed manifest, symlink escape, or lock conflict blocks deletion and leaves the target in place:

```bash
./scripts/uninstall.sh --target user --skills all --dry-run
./scripts/uninstall.sh --target user --skills all
```

Full-suite uninstall validates both members, logically removes both by rename, then cleans the staged directories. A partial suite, unknown entry, checksum drift, symlink, or lock conflict deletes nothing.

Private legacy installs are not migrated automatically. Use an explicit custom target only when you intend to operate on it. Do not point a target at this source checkout.

## Cases

Read the public cases before splitting work:

- [Single-worker compute offload](docs/cases/single-worker-compute-offload.md) shows D1 admission, sequential discovery/review, and fail-closed boundaries.
- [Independent write lanes](docs/cases/independent-write-lanes.md) shows an L2 split with disjoint owners and separate Gates.
- [Shared hotspot serial](docs/cases/shared-hotspot-serial.md) shows why two writers touching one file stay on the main thread.
- [L3 end-to-end flow](docs/cases/l3-end-to-end-flow.md) shows adaptive detection, ownership release, the `l3-v1` packet, heavy phases, layered QA, and the manual publication Gate.

The cases are contract examples, not performance promises. Token budgets, conflicts, task duration, and runtime scheduling remain host- and task-dependent.

## Support and limitations

- **Account/provider/model neutrality:** no account, provider, model, proxy, API key, or token configuration is read, written, or inferred by this repository. Static metadata is not request-level runtime identity.
- **Implicit invocation:** `allow_implicit_invocation` expresses eligibility only. Codex may choose not to trigger a skill; explicit `$adaptive-subagent-orchestration` invocation is recommended.
- **Runtime identity:** exact provider, model, account, and reasoning identity are `UNVERIFIED` unless a sanitized request-level record proves them. Never infer them from role names or local configuration.
- **Conflicts and tokens:** the skill can classify shared ownership and note token or context limits, but it cannot reserve files, guarantee token availability, or promise speed, cost, or quality improvements.
- **Runtime boundary:** Codex, not this repository, creates, waits for, and closes subagents. Transport completion is not a business `PASS`; the parent must inspect the structured result and rerun any invalidated Gate.
- **Command boundary:** builds, tests, and shell commands still run in the host workspace. D1 delegates model reasoning and tool control; it does not move local CPU execution to a remote model service.
- **Heavy boundary:** the bundled heavy skill provides the workflow and local scaffold, not a persistent scheduler. A0 still depends on Codex task state and committed Flow artifacts for recovery.
- **Platform status:** the [runtime surface matrix](docs/runtime-surface-matrix.md) distinguishes static and forward evidence from unverified App, CLI, and OS coverage. Windows remains outside the current support claim.

![Evidence loop in which candidate changes invalidate stale results and force affected verification before the parent final Gate.](docs/assets/readme/evidence-gate-loop.svg)

*Figure 6. Evidence belongs to one exact candidate; a relevant change makes the previous PASS stale.*

## Development

The canonical source is this repository. Adaptive installs two runtime files; heavy installs its Skill, metadata, seven references, and scaffold script. Each installed directory also has one manifest; repository tests and public docs are not copied.

Run the standard-library test suite and source validation:

```bash
python3 -m unittest discover -s tests -v
./scripts/validate.sh .
python3 -m compileall -q scripts tests
bash -n scripts/*.sh
git diff --check
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before opening a change. The project is published under Apache-2.0 at `https://github.com/hongkai-hue/adaptive-subagent-orchestration`.

For the integrated routing, handoff, heavy Flow, and atomic lifecycle, read the [suite architecture](docs/architecture/integrated-suite-architecture.md) or open its [interactive diagram](docs/architecture/integrated-suite-architecture.html). D1 remains specified by the [compute-offload contract](docs/contracts/compute-offload-contract.md); L3 is frozen by the [handoff contract](docs/contracts/l3-handoff-contract.md) and [suite lifecycle contract](docs/contracts/suite-lifecycle-contract.md).

The original publication model remains documented in the [v0.1 architecture notes](docs/architecture/oss-launch-architecture.md) and [interactive launch diagram](docs/architecture/oss-launch-architecture.html).

## Repository map

- [`SKILL.md`](SKILL.md) is the English runtime routing contract.
- [`agents/openai.yaml`](agents/openai.yaml) contains discovery and invocation metadata.
- [`skills/orchestrate-heavy-goals/`](skills/orchestrate-heavy-goals/) is the self-contained heavy runtime source.
- [`scripts/`](scripts/) contains install, validate, and uninstall entry points.
- [`docs/contracts/l3-handoff-contract.md`](docs/contracts/l3-handoff-contract.md) freezes the adaptive-to-heavy ownership transfer.
- [`docs/contracts/suite-lifecycle-contract.md`](docs/contracts/suite-lifecycle-contract.md) freezes manifest v2 and atomic two-skill lifecycle behavior.
- [`docs/contracts/oss-launch-contract.md`](docs/contracts/oss-launch-contract.md) freezes the v1 lifecycle boundary.
- [`docs/architecture/oss-launch-architecture.md`](docs/architecture/oss-launch-architecture.md) explains module ownership and trust boundaries.
- [`docs/runtime-surface-matrix.md`](docs/runtime-surface-matrix.md) records current evidence and limitations.
- [`tests/forward-test-record.md`](tests/forward-test-record.md) is the sanitized forward evidence record.
