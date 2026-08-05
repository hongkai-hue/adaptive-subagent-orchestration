# Integrated Orchestration Suite Architecture

## Context And Constraints

The repository must provide a complete L0-through-L3 workflow without creating a second
repository or merging two orchestration roles into one oversized skill. Existing v0.1 adaptive
installs and commands must remain valid. Both runtimes remain dependency-free, portable, and
neutral to account, provider, model, proxy, and reasoning configuration.

The repository is one release unit with two Codex discovery units. The root adaptive skill owns
routing through L0, D1, L1, and L2 and creates a frozen L3 handoff. The bundled heavy skill owns
architecture-first DAG delivery after handoff. The parent thread remains the orchestrator in both
skills; L3 is a workflow transition, not recursive subagent delegation.

## Quality Attributes

- **Closed loop:** a fresh clone can install both skills without another repository.
- **Backward compatible:** the old install command still installs only adaptive.
- **Fail closed:** incomplete handoffs, unsafe context, invalid manifests, and partial suite
  mutations do not proceed.
- **Atomic lifecycle:** suite install and uninstall cannot silently leave one managed skill active.
- **Lazy complexity:** adaptive does not load heavy references unless an L3 route is selected.
- **Auditable:** every installed file is checksummed; every L3 Flow has reproducible evidence.
- **Neutral:** public runtime never selects or claims a request identity.

## Module Responsibilities

| Module | Single responsibility | Source boundary |
| --- | --- | --- |
| Adaptive runtime | Select L0/D1/L1/L2/L3 and freeze `l3-v1` handoff packets | `SKILL.md`, `agents/openai.yaml` |
| Heavy runtime | Deliver L3 goals through architecture, contract, DAG, recovery, QA, and readiness | `skills/orchestrate-heavy-goals/**` |
| Handoff contract | Define the only stable transition between the two runtimes | `docs/contracts/l3-handoff-contract.md` |
| Lifecycle kernel | Validate, stage, atomically install, replace, and uninstall selected skills | `scripts/_lifecycle.py` |
| Contract suite | Reject runtime, handoff, lifecycle, safety, privacy, or compatibility drift | `tests/**` |
| Public guidance | Explain installation, roles, evidence, and limitations without private routes | `README*.md`, `docs/cases/**` |

## Data Flow And Trust Boundaries

1. A user goal and project rules enter the adaptive parent.
2. Adaptive evaluates L3 and safety before balanced or compute-offload routes.
3. L0/D1/L1/L2 return structured evidence to the adaptive parent final Gate.
4. L3 freezes a sanitized `l3-v1` packet, closes adaptive lanes, and transfers workflow ownership
   to the heavy A0 running in the same parent thread.
5. Heavy A0 creates architecture, contract, DAG, status, questions, and readiness artifacts.
6. Domain agents receive only exact node scope and Gates. They never orchestrate another agent.
7. Required QA returns to heavy A0. Protected external mutations stop at a user manual Gate.

The public repository boundary ends at role names and workflow contracts. Host account, provider,
model, proxy, reasoning, credentials, private data, and request-level identity remain outside the
source bundle, manifests, prompts, fixtures, logs, and evidence.

## Failure Design And Recovery

| Failure | Owner | Required behavior |
| --- | --- | --- |
| Heavy runtime missing or invalid | Adaptive parent | `HANDOFF_BLOCKED`; provide suite install guidance |
| Handoff field missing | Adaptive parent | block before heavy artifacts or writes |
| Adaptive lane still active | Adaptive parent | cancel and release ownership before handoff |
| Sensitive context cannot be minimized | Parent | keep serial or block; never copy into packet |
| One suite stage fails | Lifecycle kernel | remove stages; do not mutate targets |
| One suite activation fails | Lifecycle kernel | remove new targets and restore every prior target |
| Installed checksum drift | Lifecycle kernel | fail closed before replacement or uninstall |
| Contract changes during Flow | Heavy A0 | version contract and invalidate affected nodes |
| Worker or Gate failure | Node owner / heavy A0 | focused retry, then architecture or split review |
| Release not authorized | Heavy A0 | remain `waiting_for_manual_gate` |

## Deployment Units

| Unit | Contents | Installed destination |
| --- | --- | --- |
| Adaptive skill | root `SKILL.md`, root metadata | `<skills-root>/adaptive-subagent-orchestration` |
| Heavy skill | nested runtime, references, scaffold script | `<skills-root>/orchestrate-heavy-goals` |
| Lifecycle tooling | repository-only standard-library scripts | never copied into either skill except the heavy scaffold |
| Docs and tests | contracts, cases, evidence, regression suite | repository only |

## Decisions And Tradeoffs

- Keep two skills in one repository. This preserves discovery and lazy context boundaries while
  making source, release, installation, and compatibility a single product.
- Keep adaptive at the root. Moving it would break published source and installation assumptions.
- Write manifest v2 while reading adaptive v1. This permits safe minor-version migration without
  redefining an existing installed manifest.
- Make `--skills all` explicit. Existing users do not receive heavy behavior without choosing it.
- Bundle minimal architecture and diagram references in heavy. External architecture skills may
  enhance output but are never required for the closed loop.
- Use a suite-root lock and multi-target rollback. This adds lifecycle code but is necessary to
  prevent half-installed orchestration.

## Parallelism Boundaries

- Adaptive L1/L2 use their existing bounded lanes; D1 remains sequential.
- L3 handoff closes adaptive lanes before heavy A0 begins.
- Heavy nodes may run concurrently only in isolated worktrees or equivalent isolation, with zero
  write overlap and independent mutable resources.
- A shared workspace permits one write agent; other agents are read-only analysis or QA.
- Root runtime, lifecycle kernel, shared contracts, README files, and aggregate Flow state are
  single-owner hotspots.

## Architecture Gate

- [x] Each module has one responsibility and an explicit source owner.
- [x] The L3 workflow transition is distinct from recursive delegation.
- [x] Runtime, installation, public/private, and manual-Gate trust boundaries are explicit.
- [x] v0.1 compatibility and v0.2 migration are defined.
- [x] The HTML architecture diagram exists and passes 1440×1200 desktop visual inspection with no page overflow.
