# L3 Handoff Runtime Contract

Accept only `l3-v1` from `adaptive-subagent-orchestration` to `orchestrate-heavy-goals`, with
`orchestrator_owner: parent`. Unknown versions or fields fail closed.

Required keys are:

```text
handoff_version, handoff_id, ownership_epoch, source_skill, target_skill,
orchestrator_owner, objective, done_when, non_goals, constraints, known_facts,
evidence_paths, project_rules, baseline_revision, existing_changes,
sensitive_context, required_manual_gates, open_questions,
cancelled_adaptive_lanes
```

Require a valid SHA-256 `handoff_id`, epoch >= 1, one to three done conditions, minimized sensitive
context, repository-relative evidence paths, and every former adaptive lane in `cancelled` or
`closed` state with released scope. The pair `(handoff_id, ownership_epoch)` identifies one exact
candidate. Any content or baseline change invalidates it and increments the epoch.

State boundary:

```text
L3_DETECTED -> HANDOFF_BLOCKED | CANCEL_THEN_HANDOFF | HANDOFF_READY
HANDOFF_READY -> HEAVY_BASELINE -> HEAVY_FLOW_ACTIVE
HEAVY_FLOW_ACTIVE -> HEAVY_NEEDS_REWORK | HEAVY_ACCEPTED | WAITING_FOR_MANUAL_GATE
WAITING_FOR_MANUAL_GATE -> HEAVY_FLOW_ACTIVE | HEAVY_ACCEPTED | CANCELLED
```

After `HANDOFF_READY`, adaptive has owner state `released`; heavy A0 has `pending`, then `active` at
`HEAVY_BASELINE`. Heavy A0 runs in the same parent thread, never as a subagent. It owns all Flow
state until accepted or cancelled.
