# Open-source lane research

Last verified: 2026-08-04

## Verdict

The lane is crowded but still differentiable. Publish only as a focused adaptive
contract for medium Codex tasks; do not present the project as the first subagent
planner or expand it into a general orchestration framework.

## Closest projects

| Project | Verified positioning | Relationship to this project |
| --- | --- | --- |
| [Codex native subagents](https://developers.openai.com/codex/subagents) | Codex supplies spawn, routing, wait, close, role configuration, and current host behavior | Platform dependency; it does not define this repository's L0-L3 and evidence contract |
| [parallel-subagent-planner](https://github.com/manhua-man/codex-parallel-subagent-planner) | Chooses task/project planning modes, bounded lanes, dependency waves, ownership, and optional model/reasoning guidance | Most direct overlap; this project must stay smaller, provider-neutral, and evidence-gated |
| [codex-team-mode](https://github.com/oil-oil/codex-team-mode) | Value-based routing across Explorer/Executor/Reviewer profiles with custom agent onboarding | Strong adjacent workflow; this project does not install or require model-specific agent profiles |
| [codex-sol-luna](https://github.com/yehyakin/codex-sol-luna) | Bounded Sol/Luna model routing with lifecycle scripts and tests | Useful lifecycle reference; this project keeps model/provider routing out of scope |
| [Superpowers](https://github.com/obra/superpowers) | Broad multi-host development methodology and skills framework | Wider SDLC layer; this project focuses on one mid-task routing decision and its evidence |

## Defensible differentiation

- Route explicitly among L0, L1, L2, and a handoff to L3 heavy orchestration.
- Keep a single file owner for the full run, not only for one dispatch wave.
- Require a structured `PASS | BLOCKED` result with changed paths, verification,
  evidence, failure class, blocker, and residual risk.
- Invalidate accepted evidence when the final candidate changes.
- Allow one focused retry by the original owner, in the original scope, only with a
  concrete Delta.
- Treat transport completion, role selection, and local configuration as insufficient
  proof of task success or runtime identity.
- Keep forward fixtures and contract tests in the Python standard library.

## Mechanisms worth learning from

- Safe lifecycle, uninstall, and repair patterns from `codex-sol-luna`.
- Compact lane artifacts and held-lane reasons from `parallel-subagent-planner`.
- Explicit coordination-cost and independent-review reasoning from `codex-team-mode`.
- Broad workflow composition boundaries and contributor experience from Superpowers.

The repository must not copy upstream prose, prompts, images, agent profiles, or model
assignments. Mechanisms are re-expressed through this project's frozen contract.

## Claims to avoid

- "First" or "only" Codex subagent planner.
- Deterministic automatic triggering.
- Guaranteed speed, cost, or token improvements.
- Runtime model/provider identity inferred from TOML or role names.
- Cross-platform support not exercised by a recorded Gate.
- General project-scale DAG ownership; that belongs to the L3 handoff.

## P0 gate

Result: **differentiate and publish**.

Re-run this search before a later major repositioning. Normal patch and minor releases do
not need to repeat the full lane search unless a direct competitor materially changes the
project's unique contract.
