---
name: adaptive-subagent-orchestration
description: Route medium Codex tasks through the smallest useful set of 1-3 subagents. Use when work is likely to exceed 20 minutes or has at least two independent 3-5 minute lanes for research, implementation, testing, or review. Keep small, ordered, shared-state, migration, release, and heavy-DAG work on the main thread or hand it to orchestrate-heavy-goals.
---

# Adaptive Subagent Orchestration

Choose the smallest useful concurrency for a medium task. Parallelize only results
that can be accepted independently. Keep architecture, shared state, integration,
and the final Gate under parent-thread control.

## Route The Task

Evaluate these rules in order before creating any agent.

### 1. Escalate to L3

Stop this workflow and hand the task to `orchestrate-heavy-goals` when any condition
applies:

- The work spans at least three modules or directories and has four or more independent acceptance nodes.
- The work must freeze a cross-module API, protocol, state machine, or data format.
- The work will continue across multiple Codex tasks or sessions.
- The work needs a DAG, waves, retries, recovery, independent QA, or release readiness.

Do not let two skills manage the same work.

### 2. Keep Unsafe Work Serial

Do not create parallel write workers when any condition applies:

- Two lanes write the same hot file or shared mutable state.
- The main steps have a strict dependency order.
- The work includes a database schema change, data migration, production release, or another destructive operation.
- You cannot declare exclusive write scopes, one file owner, or independent Gates.
- A lane would receive a secret, credential, production datum, or private context that cannot be minimized.
- Splitting, waiting, and merging cost as much as completing the task directly.

When useful, use one read-only `explorer`; otherwise keep the work on the main thread. Never expand the authority granted by the user.

### 3. Select A Level

- **L0:** Fewer than two independent lanes, or a task below 20 minutes without a clear context-isolation benefit. Do not create a subagent.
- **L1:** Two independent research, diagnosis, log-analysis, test-analysis, or review lanes. Create one or two `explorer` agents.
- **L2:** Two or more independent implementation lanes with disjoint write scopes and independent acceptance Gates. Create two or three `worker` agents.

Treat 20 minutes as a routing signal, not a promise. Use L1 when two read-only lanes materially reduce uncertainty even below that threshold.

### 4. Define Goal And Done When

Before creating a lane, state:

```text
Goal: what the user must receive.
Done when: 1-3 observable, verifiable completion conditions.
```

Map every lane to at least one `Done when`. Do not create an unmapped lane. Point each condition to a file, behavior, command result, or checkable conclusion. If the goal is unclear, clarify or explore serially instead of guessing.

### 5. Batch By Live Capacity

For each batch, use the minimum of ready independent lanes, current live capacity, and three. Count only lanes whose dependencies are satisfied and whose owners are confirmed. An active agent consumes one live-capacity slot; defer the rest to the next batch without changing owners, dependencies, or Gates.

If capacity cannot be read reliably, choose the smallest manageable batch. Do not probe the limit by spawning duplicates or by filling slots with low-value lanes.

## Declare Ownership And Lane Packets

Create one owner matrix for the full run:

```text
File or directory scope | Owner | Lane ID | Shared integration surface?
```

Give every writable file one owner for the entire run. Do not transfer that owner between batches, waits, or retries. Assign shared integration files to the parent thread or one explicitly named owner. If a path is dynamic, overlapping, or unclear, run it serially.

Define every lane with this packet:

```text
Lane ID:
Role: explorer | worker | default
Goal:
Supported Done when:
Known facts and required context:
Allowed read scope:
Exclusive write scope:
File owner:
Forbidden changes:
Dependencies:
Deliverable:
Verification command or evidence:
First checkpoint:
Required return:
```

Keep `explorer` write scope empty. Give each `worker` or `default` an exact write scope, owner, deliverable, and Gate. The first checkpoint may be a target file, minimal diff, command evidence, or an explicit blocker.

If a packet is missing a required field, has conflicting owners, lacks a dependency, or exceeds authorization, return `BLOCKED` before writing. Do not guess, widen the scope, or create a replacement owner.

Pass only necessary context. Never pass `.env` files, tokens, cookies, API keys, production data, private logs, or unrelated personal data. Do not assign a provider, model, account, proxy, or reasoning route; let the host runtime choose those.

## Dispatch And Observe

1. Read the project rules, relevant README and ROADMAP, and current worktree before dispatch. Record existing user changes and the candidate baseline.
2. State the Goal, Done when, lane owners, and shared write boundaries in parent commentary.
3. Register the plan, then dispatch only the ready lanes.
4. Keep the parent thread moving on non-conflicting integration work. Do not sit in a blocking wait or poll at high frequency.
5. Check each lane's first artifact, evidence, and blocker at normal tool boundaries. Stop or narrow a lane that produces no useful artifact or evidence.
6. Wait for required lanes only when integration needs them, then close each accepted or cancelled agent.

If subagent controls are unavailable, complete the work serially in the parent thread. If a new user request changes the goal, stop or revise every lane that no longer applies.

## Enforce Role Boundaries

Keep `explorer` agents read-only. Require paths, line numbers, command output, or a reliable source, and separate facts from inferences and unknowns.

Require `worker` and `default` agents to stay inside their owner matrix. They must stop on a shared-hotspot, contract, or scope conflict and return `BLOCKED`.

Only the parent thread may orchestrate. Every subagent must not create, delegate to, or manage another subagent. A transport completion, spawn success, or agent status never proves the business result.

## Require A Structured Result

Every lane must return:

```text
Lane ID:
Status: PASS | BLOCKED
Summary:
Changed:
Verification:
Evidence:
Failure class: runtime | permission | dependency | scope | verification | conflict | none
Blocker:
Residual risk:
Out-of-scope changes: none | paths
```

Accept `PASS` only when evidence covers the deliverable and its exact scope. A read-only lane reports `Changed: none`; a write lane lists only owner-approved paths. An unrun command is not evidence and must be marked as such.

## Integrate And Run The Final Gate

Keep requirement interpretation, architecture, public interfaces, shared files, user-change protection, result integration, and the final Gate in the parent thread.

1. Compare actual changed paths with the owner matrix and inspect the candidate diff.
2. If the candidate changes after a lane passes, invalidate the old `PASS` and its evidence. Re-run the affected verification and final Gate.
3. Use the existing lockfile, package manager, project scripts, and toolchain. Do not update dependencies or generate lockfiles without authorization.
4. Have the parent run each relevant Gate and the parent final Gate on the final unchanged candidate. Never treat `transport completed` as `PASS`; require a structured `PASS`, scope evidence, owner evidence, and the final Gate.
5. Close agents after acceptance or cancellation. Do not use an agent's running state as its business result.

## Allow One Focused Retry

Retry a failed lane at most once, and continue with the original owner and exact same write scope. The retry packet must include the failure class, a concrete `Delta`, and new evidence or a changed verification requirement. Do not retry when there is no Delta, no new evidence, or no task difference.

If that focused retry fails, the parent takes over or reports `BLOCKED`; do not keep redispatching. Declare the overall task complete only after every required lane and the parent final Gate pass on the same candidate.

## State Limits And Claims

This skill routes work; it does not implement Codex transport, a persistent DAG, or a provider-specific scheduler. Do not claim deterministic implicit invocation, performance gains, or a verified runtime identity without direct evidence. Mark provider, model, account, and reasoning identity `UNVERIFIED` when it cannot be observed. Keep runtime files portable, dependency-free, and neutral to host setup.
