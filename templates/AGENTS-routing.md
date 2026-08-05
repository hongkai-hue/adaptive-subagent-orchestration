# Optional AGENTS routing rule

Copy this rule manually into the `AGENTS.md` that governs a repository or user scope. The installer does not edit `AGENTS.md`.

## Adaptive subagent routing

For medium Codex tasks, invoke `$adaptive-subagent-orchestration` explicitly and use `balanced` mode unless this policy or the current user task explicitly selects `compute-offload`. Follow its L0/D1/L1/L2/L3 routing contract and use the smallest useful number of lanes, at most three in one batch.

- Keep L0, strict dependencies, shared hotspots, sensitive context, migrations, and releases on the main thread.
- In explicit `compute-offload` mode, use D1 for one implementation estimated at least 10 minutes, or with a recorded context-isolation benefit, only when its owner, write scope, and reproducible Gate are exact. Keep work below five minutes in L0.
- When D1 needs discovery, close one read-only `explorer` before starting one `worker`. An optional independent review is also read-only and sequential; never run more than one D1 subagent at once.
- Use L1 only for independent read-only investigations.
- Use L2 only when each writable path has one owner for the full run, scopes are disjoint, and each lane has an independent Gate.
- Hand cross-module contracts, multi-wave recovery, or release-readiness work to the bundled `$orchestrate-heavy-goals` runtime. Close adaptive lanes, release their scopes, keep the same parent A0, and transfer only a valid `l3-v1` packet. Unknown fields, active ownership, unminimized context, digest mismatch, baseline drift, or a missing `l3-target:l3-v1` capability fails closed.
- Require a structured `PASS` or `BLOCKED` result with changed paths, verification, evidence, failure class, blocker, residual risk, and out-of-scope changes.
- Invalidate accepted evidence when the candidate changes. Allow one focused retry only with a concrete Delta and the same owner and scope.

The skill remains account, provider, and model neutral. Host configuration selects the execution route. Build, test, and shell commands still run in the host workspace; D1 offloads model reasoning and tool control, not local CPU execution.

For a direct L3 task, invoke `$orchestrate-heavy-goals`. Establish architecture before freezing contracts, freeze contracts before dispatching domain nodes, persist the wave DAG and status, run layered QA on the unchanged candidate, and stop at deletion, migration, credentials, CI/CD, system configuration, deployment, publication, and other manual Gates.
