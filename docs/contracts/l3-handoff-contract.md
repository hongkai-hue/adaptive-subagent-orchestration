# L3 Handoff Contract

- Version: `l3-v1`
- Status: frozen
- Owners: adaptive parent, heavy A0

## Scope And Non-goals

This contract transfers a heavy goal from the adaptive routing workflow to the bundled
`orchestrate-heavy-goals` workflow in the same parent thread. It prevents overlapping
orchestrators, preserves user authority, and provides enough verified context to establish a
recoverable Flow.

It does not select a provider, model, account, proxy, reasoning route, worker count, or release
permission. It does not turn heavy A0 into a subagent and does not prove runtime identity.

## Inputs And Outputs

The adaptive parent produces one sanitized packet after the L3 threshold is met and before heavy
artifacts or domain writes begin. Heavy A0 accepts it only after verifying required fields,
project rules, worktree state, adaptive ownership release, and sensitive-context status.

The handoff/Flow state is one of:

`HANDOFF_BLOCKED / CANCEL_THEN_HANDOFF / HANDOFF_READY / HEAVY_BASELINE / HEAVY_FLOW_ACTIVE / HEAVY_NEEDS_REWORK / HEAVY_ACCEPTED / WAITING_FOR_MANUAL_GATE / CANCELLED`

## Data Schema

```yaml
handoff_version: l3-v1
handoff_id: "sha256:<64 lowercase hex>"
ownership_epoch: 1
source_skill: adaptive-subagent-orchestration
target_skill: orchestrate-heavy-goals
orchestrator_owner: parent
objective: "observable user outcome"
done_when:
  - "one to three verifiable conditions"
non_goals: []
constraints: []
known_facts: []
evidence_paths: []
project_rules: []
baseline_revision: "7-64 lowercase hex or UNVERIFIED"
existing_changes:
  - path: "repository/relative/path"
    owner: "user | parent | lane:<id> | unknown"
    state: "present | accepted | needs_review"
sensitive_context:
  status: minimized | blocked
  excluded: []
required_manual_gates: []
open_questions: []
cancelled_adaptive_lanes:
  - lane_id: "lane identifier"
    agent_id: "runtime identifier or UNVERIFIED"
    owned_scope: []
    state: cancelled | closed
```

### Exact field rules

- The top-level key set is exact and every displayed field is required, including empty arrays.
- `handoff_version`, `source_skill`, `target_skill`, and `orchestrator_owner` equal the constants
  shown above.
- `ownership_epoch` is an integer from 1 through 2,147,483,647. Regenerating an invalidated packet
  increments it.
- `objective` contains 1-1,000 Unicode characters after trimming.
- `done_when` contains 1-3 unique strings, each 1-500 characters and independently verifiable.
- `non_goals`, `constraints`, `known_facts`, `project_rules`, `required_manual_gates`, and
  `open_questions` each contain 0-50 unique strings of 1-500 characters.
- `evidence_paths` contains 0-100 unique repository-relative POSIX paths. Empty components, `.`,
  `..`, absolute paths, backslashes, and symlink escapes are forbidden.
- `baseline_revision` is `UNVERIFIED` or 7-64 lowercase hexadecimal characters.
- `existing_changes` contains 0-100 objects with the exact keys `path`, `owner`, and `state`.
  `path` follows the evidence path rules; `owner` is `user`, `parent`, `unknown`, or `lane:<id>`;
  `state` is `present`, `accepted`, or `needs_review`.
- `sensitive_context` has exact keys `status` and `excluded`; `excluded` contains 0-50 redacted
  category names, not secret values.
- `cancelled_adaptive_lanes` contains 0-20 exact-key objects. `owned_scope` follows path rules;
  every `state` is `cancelled` or `closed`, proving that the lease no longer writes.

`handoff_id` is the SHA-256 digest of canonical UTF-8 JSON for the complete packet excluding
`handoff_id`: keys sorted lexicographically, arrays kept in contract order, and separators `,` and
`:` without extra whitespace. A changed field therefore creates a different handoff identity.

The packet must not contain credentials, endpoints, private logs, production data, unrelated
personal context, or absolute private paths.

## State Transitions

```text
L3_DETECTED -> HANDOFF_BLOCKED
L3_DETECTED -> CANCEL_THEN_HANDOFF
CANCEL_THEN_HANDOFF -> HANDOFF_BLOCKED
CANCEL_THEN_HANDOFF -> HANDOFF_READY
L3_DETECTED -> HANDOFF_READY
HANDOFF_READY -> HEAVY_BASELINE
HEAVY_BASELINE -> HANDOFF_BLOCKED
HEAVY_BASELINE -> HEAVY_FLOW_ACTIVE
HEAVY_FLOW_ACTIVE -> HEAVY_NEEDS_REWORK
HEAVY_NEEDS_REWORK -> HEAVY_BASELINE
HEAVY_FLOW_ACTIVE -> HEAVY_ACCEPTED
HEAVY_FLOW_ACTIVE -> WAITING_FOR_MANUAL_GATE
WAITING_FOR_MANUAL_GATE -> HEAVY_FLOW_ACTIVE
WAITING_FOR_MANUAL_GATE -> HEAVY_ACCEPTED
WAITING_FOR_MANUAL_GATE -> CANCELLED
```

Baseline, worktree, objective, contract, authority, or existing-change drift invalidates the packet,
increments `ownership_epoch`, and returns the Flow to `HEAVY_NEEDS_REWORK` or blocks a not-yet-active
handoff. If a user rejects a manual action, heavy A0 either removes that action from scope and moves
to `HEAVY_ACCEPTED`, or cancels the Flow. No undeclared state edge is valid.

No adaptive lane may be created or remain active after `HANDOFF_READY`. Heavy A0 owns all later
Flow state. Returning from heavy to adaptive requires a new user goal, not an implicit state edge.

## Errors And Failure Ownership

| Code | Result | Owner | Required evidence |
| --- | --- | --- | --- |
| `L3_PACKET_INVALID` | `HANDOFF_BLOCKED` | adaptive parent | rejected fields |
| `L3_ADAPTIVE_OWNER_ACTIVE` | `CANCEL_THEN_HANDOFF` | adaptive parent | lane and lease registry |
| `L3_OWNER_RELEASE_FAILED` | `HANDOFF_BLOCKED` | adaptive parent | unresolved lane/scope |
| `L3_SENSITIVE_CONTEXT` | `HANDOFF_BLOCKED` | parent | redacted category only |
| `L3_HEAVY_RUNTIME_MISSING` | `HANDOFF_BLOCKED` | adaptive parent | suite install guidance |
| `L3_BASELINE_DRIFT` | `HANDOFF_BLOCKED` or `HEAVY_NEEDS_REWORK` | heavy A0 | old/new baseline identity |
| `L3_MANUAL_GATE_PENDING` | `WAITING_FOR_MANUAL_GATE` | heavy A0 | exact action, risk, rollback |

## Authentication And Authorization

The handoff inherits only the user's existing authority. It cannot authorize deletion, rollback,
database migration, credential changes, CI/CD mutation, system configuration, paid actions,
deployment, or public release. Those actions remain distinct manual Gates.

## Idempotency And Concurrency

The pair `(handoff_id, ownership_epoch)` identifies one exact packet and ownership transfer. Reusing
that pair with the same canonical content is idempotent. A content mismatch, lower/reused epoch for
new content, or simultaneous owner fails closed.

Only one orchestrator owns a goal. `HANDOFF_READY` requires all adaptive lane leases to be closed
or cancelled and all their scopes released. Heavy A0 may delegate domain nodes only after its own
architecture, contract, and DAG are accepted.

## Compatibility And Migration

`l3-v1` is an additive v0.2 contract. Existing v0.1 adaptive-only installs continue to route L3
but cannot claim a closed-loop heavy execution. A host must install the suite to make the bundled
target discoverable. Unknown handoff versions or fields fail closed.

The machine-readable source for positive and negative examples is
`tests/fixtures/l3-handoff-cases.json`. Contract tests assert that both runtime skills contain the
version, exact constants, required key names, ownership rule, and state boundary.

The fixture envelope is exact:

```json
{
  "schema_version": "1",
  "handoff_version": "l3-v1",
  "cases": [
    {
      "id": "lowercase-hyphenated-id",
      "kind": "routing | contract | safety",
      "packet": {},
      "traits": [],
      "expected": {
        "state": "HANDOFF_READY",
        "error_code": "none",
        "adaptive_owner": "released",
        "heavy_owner": "pending"
      }
    }
  ]
}
```

`packet` is the complete packet under test, including intentionally invalid values. `traits` is a
unique string array describing external preconditions such as runtime absence or compute-offload
mode. Expected owner enums are `active | cancelling | released | none` for adaptive and
`none | pending | active` for heavy. Fixed required case IDs are
`l3-valid-ready`, `l3-missing-done-blocked`, `l3-active-lane-cancel-first`,
`l3-sensitive-context-blocked`, `l3-heavy-runtime-missing`, `l3-overrides-d1`,
`l3-digest-mismatch-blocked`, and `l3-baseline-drift-needs-rework`.

## Examples

A three-module feature with five acceptance nodes, an unchanged baseline, minimized context, and
no active adaptive lanes produces `HANDOFF_READY`. The same task in compute-offload mode still
selects L3 because heavy and safety decisions precede D1.

A packet without `done_when`, with an absolute evidence path, with a digest mismatch, or with an
active worker that cannot be cancelled produces `HANDOFF_BLOCKED` before heavy artifacts or writes.

## Contract Gate

- Both runtime skills contain the `l3-v1` identity, exact skill constants, required field names,
  owner release rule, and unknown-version fail-closed rule.
- Existing adaptive forward fixtures use schema v3 after gaining handoff metadata; the separate
  L3 handoff fixture uses its frozen schema v1 envelope and covers ready, blocked, cancellation,
  privacy, digest, missing-runtime, and L3-over-D1 outcomes.
- Tests reject a second orchestrator after `HANDOFF_READY`.
- Public privacy tests reject private paths, credentials, endpoints, and route assignments.
