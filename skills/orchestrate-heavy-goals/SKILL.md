---
name: orchestrate-heavy-goals
description: Deliver large cross-module goals through an architecture-first, recoverable Flow with frozen contracts, wave DAGs, bounded multi-agent work, async questions, layered QA, and manual release gates. Use for at least three modules and four acceptance nodes, cross-session recovery, or an explicit l3-v1 handoff; do not use for small edits, pure research, or work whose orchestration costs as much as direct execution.
---

# Orchestrate Heavy Goals

Model one large goal as a recoverable, auditable, verifiable Flow. Establish facts and architecture
before freezing contracts or dispatching implementation nodes. Keep shared hotspots, integration,
state, manual Gates, and final acceptance under the parent-thread A0.

## Accept An L3 Handoff

When invoked by `adaptive-subagent-orchestration`, accept only handoff version `l3-v1` with these
exact identity constants:

```text
source_skill: adaptive-subagent-orchestration
target_skill: orchestrate-heavy-goals
orchestrator_owner: parent
```

Require every packet field before work begins:

```text
handoff_version, handoff_id, ownership_epoch, source_skill, target_skill,
orchestrator_owner, objective, done_when, non_goals, constraints, known_facts,
evidence_paths, project_rules, baseline_revision, existing_changes,
sensitive_context, required_manual_gates, open_questions,
cancelled_adaptive_lanes
```

Reject unknown versions or fields. Require `sensitive_context.status: minimized`, a valid packet
digest, one to three verifiable `done_when` conditions, and proof that every adaptive lane is
`cancelled` or `closed` with its write scope released. `HANDOFF_READY` transfers orchestration to
heavy A0 in the same parent thread; heavy is never spawned as a worker and adaptive must not keep a
second Flow. Follow the complete bundled contract in [references/l3-handoff.md](references/l3-handoff.md).

## Use The Heavy Boundary

Use this workflow when any condition applies:

- The goal spans at least three modules or directories and has four or more independently accepted nodes.
- It introduces or changes a cross-module API, state machine, protocol, or data format.
- It requires a DAG, waves, retries, recovery, independent QA, or Release Readiness.
- It continues across tasks or sessions and must recover from persisted artifacts.
- The user explicitly requests heavy orchestration or supplies a valid `l3-v1` handoff.

Do not use it for a single-file fix, a small local feature, pure research, a speculative spike, or
fewer than four acceptance nodes. If orchestration costs as much as direct work, execute linearly.

## Keep One Orchestrator

- **A0 Orchestrator:** the parent thread; owns facts, architecture, contract, DAG, state,
  questions, integration, and user communication.
- **Architecture/Contract reviewer:** optional read-only evidence and boundary audit.
- **Domain agents:** implement exact nodes with exclusive scopes and reproducible Gates.
- **QA agent:** validates and assigns failure ownership; does not repair product code.
- **Docs/Release agent:** may organize evidence but cannot invent it or authorize release.

Only A0 orchestrates. Every subagent must not create, delegate to, or manage another subagent.

## Run The Six Phases

### 0. Establish Baseline

1. Read current user intent, project rules, README, ROADMAP, Flow files, and open questions.
2. Inspect worktree changes and preserve user-owned work.
3. Run the narrow baseline Gate and record the real revision and result.
4. Use the bundled `scripts/scaffold_flow.py` when a new Flow needs artifacts. It creates only
   missing Markdown files and never fabricates the architecture HTML.

### 1. Establish Architecture

Read and follow [references/architecture-baseline.md](references/architecture-baseline.md) and
[references/diagram-baseline.md](references/diagram-baseline.md). They are the mandatory,
self-contained baseline. If the host also provides architecture-specialist skills, they are
optional enhancements and their absence must not block the Flow.

Produce architecture Markdown plus a verified Mermaid or self-contained HTML diagram. Identify
module responsibilities, data flow, trust boundaries, failures, deployment units, shared hotspots,
parallel lanes, and hard dependencies. Keep complexity proportional to the actual project.

### 2. Freeze Contract

Write the cross-node interface under `docs/contracts/`. Include version, scope, input/output,
schema, states, errors and owners, authorization, idempotency, concurrency, compatibility,
migration, examples, and a required Contract Gate. Domain agents may not redefine a frozen
contract. A contract change invalidates every consuming artifact and node.

### 3. Build The Wave DAG

Use [references/artifact-templates.md](references/artifact-templates.md) and
[references/node-contract.md](references/node-contract.md). Each node declares ID, owner, wave,
dependencies, condition, inputs, exclusive write scope, shared read scope, outputs, Gate
criticality, expected result, forbidden scope, failure owner, and retry policy.

The DAG must be acyclic. A node is ready only when hard dependencies are `accepted`, its condition
is true, no blocking question applies, and its owner lease is available. Same-wave nodes may run
in parallel only with zero write overlap, no dependency on same-wave output, and no shared mutable
port, environment, generated sequence, or service. A shared workspace permits one write agent;
other agents are read-only.

### 4. Record Async Questions

Write questions once in `docs/project/questions.md`. A blocking question freezes only dependent
branches. A non-blocking question has an executable default whose correction is confined to one
node. When an answer changes a contract or accepted artifact, cancel affected live nodes and mark
all affected accepted or review-ready consumers `needs_rework`.

### 5. Execute And Recover

Register every agent ID, node, base revision, lease, and scope before dispatch. Give the agent only
the required context, output, Gate, and forbidden paths. A0 reviews changed paths and reruns the
node Gate before `accepted`. Close the agent and release its lease immediately after acceptance or
cancellation. Follow [references/recovery.md](references/recovery.md) after interruption, drift,
lease loss, or contract change; resume from the earliest affected node instead of restarting.

Implementation rework is limited to two attempts. A third repeated failure triggers architecture,
contract, node-size, or reproducibility review rather than another same-direction patch.

### 6. Run Layered QA And Readiness

Follow [references/qa-gates.md](references/qa-gates.md). Architecture, Contract, every
Implementation Node, Integration, and Recursive Regression are always required. UI, persistence,
security, and distributable artifact work adds the corresponding required Gate.

`NOT_RUN`, fake, mock, transport completion, or agent completion cannot satisfy a required Gate.
The final Release Readiness lists delivered scope, node evidence, integration/security/browser/
restart evidence, questions and defaults, risks, rollback, manual steps, and the final unchanged
candidate Gate.

## Stop At Manual Gates

Deletion, rollback, database schema or migration, credentials, CI/CD, system configuration,
production deployment, public publication, paid actions, and user-designated brand or aesthetic
choices require exact user authorization. A Gate blocks only dependent branches. If public release
is part of the goal, a candidate waiting for authorization is not released or complete.

## Complete With Evidence

Declare the heavy goal complete only when every required node is `accepted`, every required Gate
passes on the final unchanged candidate, conditional/informational omissions are recorded, open
questions have decisions and impact, and Release Readiness exists. Runtime, account, provider,
model, reasoning identity, performance, cost, and implicit invocation remain `UNVERIFIED` unless
direct sanitized evidence proves them.
