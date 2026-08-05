# L3 End-to-End Flow

This case demonstrates the closed loop between the lightweight router and the bundled heavy-goal
workflow. It is a contract example, not a performance or runtime-identity claim.

## Scenario

A change spans API, core state, and UI; it freezes a cross-module state contract and has five
independent acceptance nodes. It needs architecture review, ordered waves, restart recovery,
independent integration QA, and a public-release decision.

## Adaptive Decision

Adaptive evaluates L3 before balanced or compute-offload routing. It stops creating D1/L1/L2
lanes, cancels or closes any existing lane, releases every owned scope, minimizes context, and
records the unchanged baseline. It does not spawn heavy as a worker or retain a second Flow.

The parent creates one exact `l3-v1` packet with the source/target constants, objective, one to
three `done_when` conditions, constraints, facts, repository-relative evidence, existing changes,
manual Gates, closed lane registry, ownership epoch, and canonical SHA-256 identity. The packet is
`HANDOFF_READY` only when the installed heavy manifest advertises `l3-target:l3-v1`.

## Heavy Execution

The same parent becomes heavy A0 and executes these phases:

1. Establish and record the current baseline without overwriting existing work.
2. Produce and inspect architecture Markdown plus a Mermaid or self-contained HTML diagram.
3. Freeze the cross-node contract before domain implementation starts.
4. Build an acyclic wave DAG with exact owner, scope, dependencies, outputs, Gates, and retries.
5. Execute ready nodes with one orchestrator, exclusive write scopes, persisted status, bounded
   rework, and recovery from the earliest invalidated node.
6. Run architecture, contract, node, integration, and recursive regression Gates on the final
   unchanged candidate, then write Release Readiness.

An unknown handoff field, active adaptive lease, unminimized sensitive context, digest mismatch,
missing heavy runtime, or baseline drift fails closed. A contract or accepted-artifact change marks
every affected consumer `needs_rework`; transport completion alone never accepts a node.

## Manual Gate

The implementation may reach `WAITING_FOR_MANUAL_GATE`, but public push, tag, Release, deployment,
destructive change, migration, credentials, CI/CD, or system configuration still requires exact
user authorization. Reaching this state proves the candidate is ready for a decision; it does not
claim the external action happened.

## Evidence

- [Integrated suite architecture](../architecture/integrated-suite-architecture.md)
- [L3 handoff contract](../contracts/l3-handoff-contract.md)
- [Suite lifecycle contract](../contracts/suite-lifecycle-contract.md)
- `tests/fixtures/l3-handoff-cases.json` for ready, blocked, cancellation, privacy, missing-runtime,
  digest, baseline-drift, and L3-over-D1 outcomes.
- `tests/test_heavy_contract.py`, `tests/test_l3_handoff.py`, and `tests/test_install.py` for the
  self-contained runtime and lifecycle Gates.
