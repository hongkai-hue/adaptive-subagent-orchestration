# README Visual Polish Contract

- Version: v1
- Status: frozen
- Owners: A0, A1

## Scope And Non-goals

Scope:

- Add one decorative ImageGen WebP and five deterministic SVGs under
  `docs/assets/readme/`.
- Reference the same ordered six-asset manifest from both public READMEs.
- Provide localized alt text and numbered captions.
- Extend standard-library tests for asset paths, structure, size, safety, and parity.
- Perform desktop/mobile and light/dark visual QA before public publication.

Non-goals:

- Change `SKILL.md`, `agents/openai.yaml`, lifecycle behavior, agent routing, account,
  provider, model, proxy, or any runtime configuration.
- Make speed, cost, token, quality, deterministic-trigger, or universal compatibility
  claims.
- Copy documentation assets into the installed runtime bundle.
- Replace detailed prose or the existing full architecture artifact with images.

## Inputs And Outputs

Inputs are the frozen runtime skill, OSS lifecycle contract, public cases, bilingual
READMEs, and the approved visual plan. Outputs are:

```text
docs/assets/readme/
├── hero-orchestration.webp
├── ownership-boundaries.svg
├── routing-levels.svg
├── parent-agent-sequence.svg
├── install-lifecycle.svg
└── evidence-gate-loop.svg
```

The two README consumers must reference those exact paths in that exact order.

## Data Schema

Each README image entry has this logical shape:

```text
{
  ordinal: 1..6,
  target: repository-relative ASCII path,
  alt: non-empty localized description,
  caption_prefix: "Figure N." | "图 N：",
  semantic_slot: hero | routing | ownership | parent_sequence | lifecycle | evidence
}
```

Every SVG must have a root `viewBox`, direct child `<title>` and `<desc>`, a fixed local
canvas, and only local SVG primitives. It may not contain `<script>`, `<image>`,
`<foreignObject>`, event-handler attributes, remote URLs, `data:` URLs, or external fonts.

The hero must be WebP, 1600×900, below 300 KB, without text, letters, numbers, logos,
trademarks, people, robots, provider symbols, or private data. Each SVG must be below
100 KB.

## State Transitions

```text
visual_spec -> authored -> structurally_valid -> readme_integrated
readme_integrated -> browser_verified -> release_candidate
release_candidate -> waiting_for_manual_gate -> published -> publicly_verified
```

Any asset, README, test, or caption change after a Gate invalidates affected evidence and
returns the candidate to `authored` or `readme_integrated` as appropriate.

## Errors And Failure Ownership

- Generated text, brands, privacy content, or unclear lane separation: RVP-04/ImageGen.
- Wrong SVG labels, edges, script/external content, size, or accessibility metadata:
  RVP-03/diagram authoring.
- Missing, reordered, inaccessible, or semantically divergent README references:
  RVP-06/integration.
- Test false positive, incomplete discovery, or bundle-boundary regression: RVP-05/tests.
- Overflow, low contrast, unreadable mobile labels, broken browser asset, or visual claim
  mismatch: RVP-07/QA.
- Unauthorized or failed public mutation: RVP-08/manual release owner.

Failures remain failures; no test may swallow an error, substitute a placeholder image, or
convert `NOT_RUN` into PASS.

## Authentication And Authorization

Local authoring and tests require no authentication. Assets and README content must contain
no credentials or private configuration. A push to the public GitHub repository is an
external state change and requires an explicit manual Gate immediately before execution.

## Idempotency And Concurrency

Re-running tests and rendering checks is side-effect free except for isolated screenshots.
ImageGen candidates are generated independently; only the selected final WebP is committed.
Because all agents share one worktree, A0 is the sole file writer. Read-only audits may run
concurrently. No two workers own a shared README, test, Flow, or asset path.

## Compatibility And Migration

- GitHub Markdown remains the reference renderer; standard Markdown image syntax is used.
- Assets use repository-relative lowercase kebab-case paths.
- The SVG fixed light canvas must remain readable in both GitHub themes.
- Runtime and install compatibility do not change; the existing runtime-surface limitations
  remain `UNVERIFIED` where previously documented.
- Removal rollback deletes README references and the six owned assets in a normal follow-up
  commit; public history is not rewritten.

## Examples

English consumer:

```markdown
![Routing levels from local execution to heavy-orchestration handoff.](docs/assets/readme/routing-levels.svg)

*Figure 2. Choose the smallest routing level that creates a useful independent lane.*
```

Chinese consumer:

```markdown
![从本地执行到重型编排交接的路由层级图。](docs/assets/readme/routing-levels.svg)

*图 2：只选择能够产生有价值独立车道的最小路由层级。*
```

## Contract Gate

Required Gate before implementation acceptance:

```bash
python3 -m unittest tests.test_docs.PublicDocsTests -v
```

Expected after the asset tests are added: exit `0`, all public documentation tests PASS,
and recursive discovery includes every new test.
