# README Visual Polish Architecture

## Context And Constraints

This Flow adds a visual explanation layer to the two public READMEs without changing the
runtime skill, its routing behavior, or the installed bundle. The repository has one
maintainer, a small standard-library test suite, and a published `v0.1.0` release. Visual
assets are documentation artifacts, not executable runtime inputs.

Constraints:

- English and Chinese READMEs must consume the same six assets in the same order.
- Essential rules must remain text-accessible when images are unavailable.
- Generated raster art may establish mood but cannot carry contract labels or claims.
- Deterministic SVGs must have no scripts, remote resources, embedded raster data, or
  private configuration.
- The installed bundle remains exactly `SKILL.md`, `agents/openai.yaml`, and its manifest.
- Implementation may use local authoring tools, but CI and runtime gain no dependency.
- Public push remains a manual Gate even after the local Release Candidate passes.

## Quality Attributes

1. **Accurate**: every diagram statement traces to the frozen runtime or lifecycle contract.
2. **Accessible**: assets have titles/descriptions; both READMEs provide localized alt text
   and captions; prose remains sufficient without images.
3. **Portable**: relative repository paths work in GitHub and common Markdown renderers.
4. **Safe**: assets contain no account, provider, model, endpoint, credential, or local path.
5. **Lightweight**: the hero is below 300 KB and each SVG is below 100 KB.
6. **Maintainable**: five semantic diagrams are reviewable text diffs; one generated image
   is intentionally decorative.

## Module Responsibilities

| Module | Unique responsibility | Changes when |
| --- | --- | --- |
| Contract sources | Define routing, ownership, result, lifecycle, and evidence truth | Runtime/lifecycle contract changes |
| ImageGen hero | Establish the parent/two-lane/merge mental model without text | Visual direction changes |
| Deterministic SVG set | Explain five contract questions with exact labels and arrows | A represented contract changes |
| Bilingual README integration | Place shared assets with localized alt text and captions | Public narrative changes |
| Documentation tests | Enforce manifest parity, safe SVG structure, paths, size, and captions | Asset contract changes |
| Browser visual QA | Verify desktop/mobile and light/dark rendering | Rendering or asset layout changes |
| GitHub publication | Make accepted assets visible on public `main` after a manual Gate | Maintainer authorizes push |

## Data Flow And Trust Boundaries

1. Frozen public contracts provide labels and allowed claims.
2. ImageGen produces three local raster candidates; A0 selects one and converts it to a
   project WebP. Generated pixels are untrusted until visual privacy and composition review.
3. A0 authors five SVGs directly from contract sources. SVG text is trusted only after
   structural, link, and contract review.
4. Both READMEs reference one ordered asset manifest and supply localized accessibility text.
5. Standard-library tests validate the repository representation; browser screenshots
   validate rendering properties that static tests cannot prove.
6. A local Release Candidate stops at a manual Gate. Only an explicitly approved push may
   cross into the public GitHub repository.

Trust boundaries:

| Boundary | Untrusted input | Control |
| --- | --- | --- |
| ImageGen output → repository | Hallucinated text, brands, misleading topology | Three candidates, human selection, visual inspection, no-text prompt |
| SVG source → README | Wrong labels, scripts, external resources, unreadable density | Contract audit, XML tests, allowlisted elements/resources, browser QA |
| README → installed bundle | Documentation assets accidentally copied into runtime | Existing manifest/lifecycle tests |
| Local candidate → public GitHub | Wrong account, premature or unverified publication | Manual push Gate, CI, unauthenticated public verification |

## Failure Design And Recovery

| Failure | Required behavior | Recovery |
| --- | --- | --- |
| Generated hero contains text, branding, or unclear lanes | Reject candidate; do not edit around a misleading base | Select another candidate or one targeted regeneration |
| SVG contradicts contract | Mark owning diagram node `needs_rework` | Correct labels/edges, rerun SVG and contract Gates |
| Asset missing, oversized, or externally linked | Documentation tests fail | Restore local asset or reduce it without changing semantics |
| English/Chinese asset order diverges | Integration Gate fails | Reconcile the shared manifest and localized captions |
| Mobile or dark-theme rendering is unreadable | Browser Gate fails | Simplify diagram, increase contrast/type size, rerender |
| Candidate changes after a PASS | Previous evidence becomes stale | Rerun affected tests and final visual Gate |
| Public CI or raw asset verification fails | Do not claim completion | Fix locally, push a normal follow-up only after the Gate is approved |

## Deployment Units

There are three deployment units with intentionally different boundaries:

1. **Source documentation**: README files, six visual assets, tests, and Flow evidence.
2. **Installed runtime bundle**: unchanged two-file skill plus ownership manifest; no images.
3. **Public GitHub `main`**: source documentation after local QA, explicit authorization, and
   online CI/public URL verification.

## Decisions And Tradeoffs

- Use one generated hero and five deterministic SVGs: visual warmth without delegating
  precise contract text to a probabilistic renderer.
- Reuse one asset set across languages: lower drift and smaller repository, with localized
  alt text/captions preserving accessibility.
- Use a fixed light SVG canvas: predictable contrast in GitHub light and dark themes at the
  cost of not visually blending into every theme.
- Keep essential statements in prose: more repetition, but images never become the only
  accessible source of truth.
- Extend standard-library tests rather than add image libraries to CI: structural safety is
  reproducible; pixel-level and contrast quality remain an explicit browser Gate.

## Parallelism Boundaries

Read-only contract and README/test audits may run in parallel. All repository writes remain
owned by A0 because the available agents share one worktree. The hero, SVGs, tests, and
README integration are hard-dependent on the frozen visual contract. `README.md`,
`README.zh-CN.md`, `tests/test_docs.py`, `ROADMAP.md`, Flow status, and release evidence are
shared integration surfaces and therefore A0-only.

Public push is strictly sequential after local regression and browser QA, and it remains a
manual Gate.

## Architecture Gate

- [x] Each module has one clear responsibility.
- [x] Every cross-module interface is identified.
- [x] Parallel and hard-dependent work is explicit.
- [x] The architecture diagram HTML has been generated and inspected at 1440×1200.
