# Compute Offload Architecture

## Context And Constraints

The existing workflow optimizes for useful concurrency: a small task stays on the parent and
implementation delegation normally begins only when two disjoint lanes exist. The new opt-in
compute-offload mode must also support one bounded execution lane so a host can delegate routine
implementation work without claiming that sequential delegation is parallelism.

The public runtime remains provider, model, account, proxy, and credential neutral. A host policy
may select compute-offload mode, while private role configuration chooses the actual execution
route. The parent retains requirement interpretation, shared files, integration, and the final
Gate in every mode.

## Quality Attributes

- **Safe by default:** balanced remains the public default and preserves existing L0-L3 behavior.
- **Useful offload:** one non-trivial, bounded, verifiable implementation may use D1.
- **Fail closed:** missing scope, Gate, authority, or privacy isolation prevents delegation.
- **Portable:** the runtime bundle adds no dependency and contains no provider-specific route.
- **Auditable:** mode, route, owner, changed paths, evidence, and final Gate remain observable.
- **Recoverable:** the parent can stop a failed lane and resume locally without ownership drift.

## Module Responsibilities

| Module | Single responsibility | Change trigger |
| --- | --- | --- |
| Host mode policy | Select `balanced` or `compute-offload` through explicit prompt or host rules | User or repository policy changes |
| Routing kernel | Choose L0, D1, L1, L2, L3, `SERIAL`, or `BLOCKED` | Public routing contract changes |
| Safety admission | Check scope, owner, Gate, privacy, parent overlap, authority, and delegation value | Safety contract changes |
| Lane scheduler | Dispatch one D1 lane, sequential explore→D1, or bounded L1/L2 batches | Capacity or sequencing rules change |
| Host role routing | Resolve role to account, provider, model, and reasoning outside this repository | Private host configuration changes |
| Parent integration Gate | Audit scope and evidence, integrate, invalidate stale PASS, and declare completion | Project verification changes |

## Data Flow And Trust Boundaries

1. The user goal, project rules, and optional host mode enter the routing kernel.
2. Safety admission derives an eligible route. It never reads or assigns provider/model identity.
3. For D1, the parent freezes one owner, one bounded write scope, one deliverable, and one Gate.
4. When discovery is required, one read-only explorer closes before the D1 worker is admitted.
5. The host runtime maps `explorer`, `worker`, or `default` to its private role configuration.
6. After D1, the unchanged candidate may receive one closed-scope read-only review; the worker
   must close first and the reviewer returns `Changed: none`.
7. Structured results return to the parent, which audits changed paths and reruns the final Gate.

The public repository boundary ends at role names. Private agent configuration and request-level
identity stay outside the runtime bundle, public docs, fixtures, logs, and forward evidence.

## Failure Design And Recovery

| Failure | Required behavior |
| --- | --- |
| Mode absent or ambiguous | Use `balanced`; do not infer compute-offload from provider config |
| D1 scope or Gate missing | Keep the work local or return `BLOCKED` before a worker writes |
| Parent and worker would edit the same path | Use one owner and run serially |
| Explorer cannot establish a safe scope | Stop the sequence; do not dispatch the worker |
| Role route unavailable or rate-limited | Record runtime failure and let the parent continue locally or retry once with a Delta |
| Candidate changes after lane PASS | Invalidate affected evidence and rerun the Gate |
| Sensitive context cannot be minimized | Keep the task on the parent |

## Deployment Units

| Unit | Contents | Mutation boundary |
| --- | --- | --- |
| Canonical source | `SKILL.md`, metadata, fixtures, tests, docs | Repository commit |
| Installed runtime | `SKILL.md`, `agents/openai.yaml`, ownership manifest | Lifecycle scripts or an explicit legacy migration |
| Host mode overlay | User or repository `AGENTS.md` rule | Explicit local policy update |
| Private role routes | Host-managed agent TOML | Outside public project control |

## Decisions And Tradeoffs

- D1 is a delegation route, not a parallel lane. This avoids overstating wall-clock gains.
- Compute-offload is opt-in. A public default that delegates every small edit would create noise,
  cost, and ownership risk for users with different runtime economics.
- The skill defines admission policy but not a numeric cost model. Estimated time is a signal;
  exact scope, a reproducible Gate, and context-isolation value are stronger evidence.
- Sequential explorer→D1 is allowed only after the explorer closes and the parent freezes the
  worker packet. This spends more inference but prevents speculative writing.

## Parallelism Boundaries

- D1 uses exactly one active write agent; the parent does not write its owned scope.
- Sequential explorer→D1 has maximum live lane count one for that branch.
- Optional D1→review is also sequential and keeps maximum live lane count one.
- L1 and L2 keep the existing maximum of three subagents per dispatch batch.
- Shared integration files remain parent-owned or have one explicit owner.
- L3 remains a handoff to heavy orchestration; two orchestrators never manage one goal.

## Architecture Gate

- [x] Each module has one clear responsibility.
- [x] Public and private trust boundaries are explicit.
- [x] D1, sequential exploration/review, L1/L2 concurrency, and L3 handoff are distinct.
- [x] Failure ownership and local fallback are defined.
- [x] The HTML architecture diagram has been generated and inspected at 1440×1200 without overflow.
