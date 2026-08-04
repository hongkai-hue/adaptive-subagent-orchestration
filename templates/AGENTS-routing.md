# Optional AGENTS routing rule

Copy this rule manually into the `AGENTS.md` that governs a repository or user scope. The installer does not edit `AGENTS.md`.

## Adaptive subagent routing

For medium Codex tasks, invoke `$adaptive-subagent-orchestration` explicitly and follow its L0-L3 routing contract. Use the smallest useful number of lanes, at most three in one batch.

- Keep L0, strict dependencies, shared hotspots, sensitive context, migrations, and releases on the main thread.
- Use L1 only for independent read-only investigations.
- Use L2 only when each writable path has one owner for the full run, scopes are disjoint, and each lane has an independent Gate.
- Hand cross-module contracts, multi-wave recovery, or release-readiness work to L3 heavy orchestration.
- Require a structured `PASS` or `BLOCKED` result with changed paths, verification, evidence, failure class, blocker, residual risk, and out-of-scope changes.
- Invalidate accepted evidence when the candidate changes. Allow one focused retry only with a concrete Delta and the same owner and scope.
