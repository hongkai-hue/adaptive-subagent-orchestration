# Architecture Baseline

Use this bundled baseline before freezing a heavy Flow contract.

## Required Sections

```text
Context And Constraints
Quality Attributes
Module Responsibilities
Data Flow And Trust Boundaries
Failure Design And Recovery
Deployment Units
Decisions And Tradeoffs
Parallelism Boundaries
Architecture Gate
```

## Method

1. Record real constraints: current scale, team, lifespan, authorization, existing stack, and
   actual change vectors. Design for plausible growth, not an imagined platform.
2. Group modules by business capability and change reason. Every module has one primary
   responsibility and one owner.
3. Trace input → transformation → state → output. Mark trust boundaries and sensitive data.
4. Identify shared hotspots, contracts, failure ownership, recovery, and deployment units.
5. Explain why each boundary exists. Prefer a modular monolith unless independent deployment,
   compliance, ownership, or scale provides evidence for a stronger boundary.
6. State which work may run in parallel and which work has a hard dependency.

## Complexity Gate

Before adding a non-trivial pattern, answer yes to all:

- Has the simpler design been considered and shown insufficient?
- Is the complexity required by current evidence?
- Can the current maintainers operate and debug it?
- Will it still be understandable in six months?
- Can its removal or replacement boundary be explained?

## Required Evidence

The Architecture Gate checks that module responsibilities are non-overlapping, every cross-module
interface is named, data and failures have owners, deployment units match operating reality, and
parallel nodes do not share writable state. Architecture is not accepted until its diagram is
generated, opened, and checked for missing flows and visual overflow.
