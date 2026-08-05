# Node Contract And Agent Handoff

## Node Card

```markdown
### <PREFIX>-<NN> <Node title>

- State: not_started
- Owner: A<N> / role
- Wave: W<N>
- Depends on: node IDs or none
- Condition: always or explicit predicate
- Inputs: frozen contracts and accepted artifacts
- Exclusive write scope:
  - repository/relative/path
- Shared read scope:
  - repository/relative/reference
- Outputs:
  - repository/relative/artifact
- Gate:
  - Criticality: required | conditional | informational
  - Command: reproducible command
  - Expected: exit code, count, or terminal marker
- Forbidden:
  - explicit non-goals and hotspots
- Failure owner: node ID or role
- Retry: implementation rework <= 2; third failure escalates to A0
```

A Gate cannot say “looks correct” or “development complete.” UI nodes include desktop/mobile and
empty/error/long-content evidence. Normalize scopes before dispatch and reject `..`, symlink escape,
ancestor/descendant overlap, mutable shared ports, and generated-sequence conflicts.

## Ownership Matrix

```markdown
| Path / glob | Write owner | Readers | Notes |
| --- | --- | --- | --- |
```

One writable path has one owner for the whole Flow. Dependency files, aggregate exports, routes,
database entry points, generated indexes, and deployment definitions are shared hotspots and stay
with A0 or one explicit owner.

Parallel write nodes require isolated worktrees or equivalent workspaces and a recorded base
revision. A shared workspace allows one write agent; different paths alone do not make concurrent
writes safe. A0 records pre-dispatch status/diff/hash and audits them after completion.

## Worker Packet

```text
You own node <ID>: <title>.

Dependencies accepted: <IDs and artifacts>
Lease: <agent ID, start, expiry, base revision>
Exclusive write scope: <paths>
Shared hotspots / forbidden: <paths>
Required outputs: <paths>
Gate: <command and expected result>
Non-goals: <explicit exclusions>

Do not revert or reformat out-of-scope work. Do not create or manage another agent.
Return changed files, command and result, assumptions, risks, shared-file requests,
and whether any out-of-scope path changed.
```

## Handoff Result

```markdown
### Handoff <node ID>
- Result: ready_for_review | needs_rework | blocked
- Files changed: ...
- Gate run: ...
- Actual result: ...
- Contract assumptions: ...
- Shared-file requests: ...
- Residual risks: ...
- Out-of-scope changes: none | ...
```

## A0 Acceptance

Audit scope, inspect diff, compare frozen contract, rerun the node Gate, confirm recursive test
discovery, and release the lease. Only then mark `accepted`. On the third repeated implementation
failure, stop patching and review architecture, contract, node size, environment, or ownership.
