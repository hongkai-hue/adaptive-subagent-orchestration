# Single-worker compute offload

## Scenario

A user explicitly selects `compute-offload` for a self-contained implementation expected to
take about 15 minutes. The change is limited to `src/report.py`, and the existing command
`python3 -m unittest tests.test_report -v` is a reproducible Gate. The parent will not edit that
file while the worker owns it.

## Route

Choose D1 and dispatch exactly one `worker`. The time estimate is only a signal; admission is
safe because the write scope, owner, Gate, privacy boundary, and delegation value are all known.

```text
Lane ID: D1-report
Role: worker
Goal: implement the requested report behavior
Supported Done when: the target behavior is present and the named Gate passes
Allowed read scope: src/report.py, tests/test_report.py
Exclusive write scope: src/report.py
File owner: D1-report worker for the full lane
Forbidden changes: tests, dependencies, configuration, unrelated files
Dependencies: none
Deliverable: minimal diff in src/report.py
Verification command or evidence: python3 -m unittest tests.test_report -v
First checkpoint: target function and proposed minimal diff
Required return: structured PASS or BLOCKED packet
```

The worker returns its exact changed path and verification output. The parent inspects the diff,
checks that ownership was respected, and reruns the final Gate on the unchanged candidate.

## Sequential discovery and review

If the target path is initially uncertain, run one read-only `explorer` first. Close it after it
returns file-and-line evidence, then freeze the worker packet and start D1. After a worker PASS,
the parent may run one read-only `explorer` against the unchanged candidate. That reviewer must
return `Changed: none`; the parent still owns the final Gate. Maximum simultaneous D1 subagents
is one, so this is sequential offload rather than parallel execution.

## Fail-closed boundaries

Stay in L0 when the task is below five minutes. Return `BLOCKED` before writing when D1 lacks an
exact owner, scope, or Gate. Keep the work `SERIAL` on the parent when it overlaps a parent-owned
file, needs unminimized sensitive context, performs migration or release work, or depends on a
shared hotspot. Escalate to L3 before considering D1 when the heavy-goal threshold is met.

Builds, tests, and shell commands still execute in the host workspace. This route delegates model
reasoning and tool control; it does not move local CPU execution to another service and does not
select or verify an account, provider, model, or reasoning setting.
