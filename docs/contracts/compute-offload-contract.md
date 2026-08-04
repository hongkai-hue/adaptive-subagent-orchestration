# Compute Offload Contract

- Version: v1
- Status: frozen
- Owners: A0

## Scope And Non-goals

This contract adds an opt-in compute-offload mode and the D1 single-worker route while preserving
balanced mode as the public default.

Non-goals include provider/model selection, deterministic implicit invocation, remote CPU
execution, persistent queues, recursive delegation, automatic publication, and performance or
cost guarantees.

## Inputs And Outputs

Inputs are the user goal, host-selected mode, estimated effort, lane types, write scopes, task
traits, project rules, live capacity, and available verification Gates.

Evaluate in this fixed order: L3 threshold; safety and packet failures that require `SERIAL` or
`BLOCKED`; explicit/default mode; then the eligible balanced or compute-offload route. D1 cannot
override an earlier heavy or safety decision. The routing output is one of:

`L0 / D1 / L1 / L2 / L3 / SERIAL / BLOCKED`

It also includes the ordered roles, maximum simultaneous subagents, owner matrix, lane packets,
and evidence rule. Maximum simultaneous subagents is not the total number of sequential stages.

## Mode Contract

- `balanced` is the default when no explicit mode is supplied. It preserves the v0.1 routing
  behavior: a single ordinary implementation remains L0.
- `compute-offload` may be selected by the user, repository policy, or user-level host policy.
- Conflicts resolve in this order: current user task, repository policy, user-level host policy,
  then the `balanced` default.
- Mode selection never implies or verifies a provider, account, model, reasoning effort, speed,
  cost, or quality level.
- A mode instruction cannot override safety, authorization, ownership, or manual release Gates.

## D1 Admission

D1 delegates exactly one bounded implementation lane to one `worker`. Admit it only when every
condition holds:

1. `compute-offload` is explicitly selected.
2. The work is non-trivial: estimated effort is at least 10 minutes, or a recorded
   `context-isolation-value` trait shows that delegation materially protects the parent thread.
3. The deliverable and exclusive write scope are exact, with one owner for the full run.
4. At least one reproducible verification Gate covers the deliverable.
5. The parent will not edit the worker-owned scope while the lane is active.
6. Sensitive context can be excluded and the user has authorized the underlying work.
7. Delegation, review, and integration cost is lower than direct parent execution.

A task estimated below 5 minutes stays L0 even when context isolation is requested. A shared
hotspot, strict dependency, destructive action, migration, production release, or unminimizable
sensitive context stays `SERIAL` or behind its existing manual Gate. Missing packet fields cause
`BLOCKED` before writing, not speculative execution.

## Sequential Explore To D1

Compute-offload may run one read-only `explorer` before D1 when the parent cannot yet freeze the
write scope or Gate. The explorer must close with evidence before the parent creates the worker
packet. The worker receives the verified facts needed for implementation, not the explorer's
unverified conclusions. Maximum simultaneous subagents for this sequence is one.

## Optional Read-only Review

After a D1 worker closes with structured PASS, the parent may send the exact unchanged candidate
to one `explorer` for independent review. The reviewer has no write scope, returns
`Changed: none`, and checks the worker's diff, Gate evidence, or failure paths. The parent still
owns acceptance and the final Gate. If the candidate changes, both worker and review evidence
become stale. D1→review is sequential and has maximum simultaneous subagents one.

## Data Schema

Forward fixtures use schema version `2`.

```text
input.mode: balanced | compute-offload
input.estimated_minutes: integer
input.lane_types: readonly | write | verification[]
input.lane_count: integer
input.write_scopes: string[]
input.traits: string[]

expected.level: L0 | D1 | L1 | L2 | L3 | SERIAL | BLOCKED
expected.roles: explorer | worker | default[] in dispatch order
expected.max_agents: integer maximum simultaneously live subagents
expected.business_status: PASS | BLOCKED | UNVERIFIED
expected.evidence_rule: string
```

## State Transitions

```text
balanced single lane -> L0
compute-offload eligible single lane -> D1
compute-offload uncertain scope -> explorer -> parent packet freeze -> D1
D1 packet conflict -> BLOCKED before write
D1 runtime failure -> one focused retry with Delta | parent local takeover | BLOCKED
D1 PASS -> optional read-only review -> parent scope audit -> parent final Gate -> accepted result
candidate changed -> prior evidence STALE -> affected Gate rerun
heavy threshold -> L3 handoff
```

## Errors And Failure Ownership

| Failure class | Owner | Result |
| --- | --- | --- |
| Unclear goal or mode | Parent | clarify or use balanced |
| Requested D1 missing scope, owner, or Gate | Parent packet | `BLOCKED` before write |
| Runtime/provider unavailability | Host runtime | structured runtime failure; no identity inference |
| Worker scope violation | D1 lane | reject result and return to parent |
| Verification failure | Original owner | one focused retry with Delta |
| Shared integration failure | Parent | integrate serially and rerun final Gate |

## Authentication And Authorization

This repository does not authenticate or configure model requests. Existing user authority,
project rules, sensitive-data restrictions, and manual gates remain controlling. Lane prompts
must not contain credentials, private routes, production data, or unrelated personal context.

## Idempotency And Concurrency

Mode evaluation is read-only and repeatable for the same task facts. A D1 write scope has one
owner for the full run. Parent writes to that scope invalidate the lane and require a new packet.
Retries keep the same owner and scope and require a concrete Delta. No subagent may delegate.

## Compatibility And Migration

Balanced mode is backward-compatible with the published v0.1 behavior. Fixture schema v2 adds
`input.mode` and the `D1` level. Hosts that want the previous behavior need no policy change.
Hosts that opt into compute-offload must update their routing instruction after installing the
new runtime; installing the skill never edits host policy or private agent routes.

## Examples

| Task | Mode | Route | Reason |
| --- | --- | --- | --- |
| Three-minute typo fix | compute-offload | L0 | delegation overhead exceeds value |
| Bounded module implementation with unit Gate | compute-offload | D1 worker | exact scope and reproducible Gate |
| Unknown failure location, then bounded fix | compute-offload | explorer → D1 worker | discovery closes before writing |
| Bounded fix needs independent challenge | compute-offload | D1 worker → explorer review | same candidate, read-only review |
| Same bounded implementation | balanced | L0 | public default preserves prior behavior |
| Two disjoint independently testable modules | either | L2 | useful implementation concurrency |
| Shared configuration hotspot | either | SERIAL | one writer only |

## Contract Gate

- Runtime text defines both modes, D1 admission, sequential explore→D1, and final parent Gate.
- Fixtures cover positive, negative, compatibility, safety, and fallback cases.
- Tests reject provider/model/account route assignments in runtime and public docs.
- Local host policy and active installation are verified separately from the public candidate.
