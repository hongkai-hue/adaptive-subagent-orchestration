# Recovery And Continuous Execution

## Cold Recovery

1. Re-read the latest user request; do not resume a stale goal.
2. Read project rules, ROADMAP, Flow DAG, status, questions, contracts, and readiness.
3. Inspect current diff and distinguish user, accepted, and unknown changes.
4. Rerun critical accepted Gates that lack current evidence.
5. When state conflicts with the candidate, trust the Gate and mark affected nodes `needs_rework`.
6. Resume the earliest ready affected node in topological order; do not restart the whole Flow.
7. Recheck owner scopes and revoke stale leases before dispatch.

## Lost Worker Or Lease

Cancel or close the old agent, revoke its lease, and mark the node blocked before creating a new
owner. Audit the existing diff. A new owner reads existing evidence and either continues the node or
rebuilds it. Output after lease expiry or revocation is not merged automatically.

## Valid State Edges

```text
not_started -> in_progress
not_started -> waiting_for_manual_gate
not_started -> cancelled
in_progress -> blocked | ready_for_review | cancelled
blocked -> in_progress | cancelled
ready_for_review -> accepted | needs_rework
accepted -> needs_rework
needs_rework -> in_progress | cancelled
waiting_for_manual_gate -> in_progress | accepted | cancelled
```

Reject and record any undeclared edge. A dependency entering `needs_rework` or `cancelled` cancels
live consumers and invalidates review-ready or accepted consumers. Check the graph for cycles before
dispatch.

## Contract Change

Record the question and impact, version the revised contract, mark the previous version
`superseded`, invalidate all consuming nodes, and restart from the earliest affected Wave. Frequent
contract churn means architecture or the original Contract Gate is insufficient.

## Non-blocking Progress

A blocking question freezes only dependent branches. While agents run, A0 may inspect contracts,
test discovery, evidence, and other non-conflicting parent-owned work. A new user request that
changes the goal cancels conflicting nodes before DAG revision.

## Manual Gate Recovery

Record the exact action, target, risk, rollback, and dependent nodes. Execute only the authorized
action. After deployment or publication, verify the real user access path before acceptance. User
rejection either removes the optional action from scope or cancels the dependent branch.
