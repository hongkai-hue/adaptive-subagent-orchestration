# README Visual Polish Release Readiness

## Decision

Public release verified. RVP-00 through RVP-08 are accepted; runtime behavior, tag, and existing
GitHub Release remain unchanged.

## Delivered Scope

- One selected 1600×900 decorative WebP and five deterministic explanatory SVGs.
- The same ordered six-asset narrative in `README.md` and `README.zh-CN.md`, with localized
  alt text, captions, and architecture deep links.
- Standard-library checks for manifest parity, captions, local-only references, WebP
  dimensions/size, SVG accessibility/safety/size, links, architecture, and privacy.
- A visual architecture, frozen v1 contract, recoverable DAG/status state, and this release
  evidence record. Runtime skill, metadata, lifecycle scripts, and installed bundle are
  unchanged.

## Node Evidence

| Node | Gate | Actual result | Evidence |
| --- | --- | --- | --- |
| RVP-00 | Baseline | PASS | `main@fad59ae`; source validation and 29/29 baseline tests passed |
| RVP-01 | Architecture | PASS | Markdown contract complete; self-contained HTML inspected at 1440×1200 |
| RVP-02 | Frozen contract | PASS | v1 exact six-asset, README, test, and safety contract recorded |
| RVP-03 | Deterministic SVGs | PASS | Five XML-safe local SVGs, each 4,674–5,773 bytes, inspected after browser render |
| RVP-04 | ImageGen hero | PASS | Candidate C selected; WebP is 1600×900 and 18,430 bytes; no text, brand, person, or private content |
| RVP-05 | Asset tests | PASS | Focused documentation suite 11/11; no third-party test dependency introduced |
| RVP-06 | Bilingual integration | PASS | Exact manifest/order, six captions per language, local links, and privacy checks passed |
| RVP-07 | Browser + regression QA | PASS | GFM previews and full local Gate passed; independent read-only QA accepted the candidate |
| RVP-08 | Manual public push | PASS | User authorized a fresh-clone normal push; content commit `04487d8`, CI run `30895434940`, both READMEs, six assets, and live rendering passed |

## Integration And Security Evidence

Commands run against the integrated candidate:

```text
./scripts/validate.sh .                                      PASS
python3 -m unittest discover -s tests -v                    PASS (33/33)
python3 -m compileall -q scripts tests                      PASS
bash -n scripts/*.sh                                        PASS
git diff --check                                             PASS
```

The optional system `quick_validate.py` was also attempted, but the host lacks its undeclared
`PyYAML` import. No global dependency was installed. The repository's own source validator and
standard-library contract suite passed and remain the release Gates.

Privacy tests scan the public Markdown, HTML, and SVG surface for credentials, private routes,
and local-user paths. SVG tests reject scripts, `foreignObject`, embedded raster images, event
handlers, and remote references. Every README image target is local.

Public release evidence:

```text
public content commit                                      04487d8
GitHub Actions CI run 30895434940                          PASS (3/3 jobs)
public README.md and README.zh-CN.md                       HTTP 200
six unauthenticated WebP/SVG asset URLs                    HTTP 200
live GitHub README image count                             6/6 complete
```

## Browser / Visual Evidence

- GitHub's GFM render endpoint produced the review HTML for the English README.
- Desktop light and dark wrappers were inspected at 1440 px; all six assets rendered with
  readable hierarchy and fixed light canvases on both themes.
- Playwright inspected actual 390×844 light and dark viewports. In each theme,
  `clientWidth == scrollWidth == 390`; all six images completed and rendered at 358 px without
  page overflow or clipping.
- Individual 358 px mobile captures confirmed that the main route, ownership split, parent
  sequence, lifecycle branches, and evidence invalidation loop remain distinguishable. Detailed
  semantics are also present in localized alt text, captions, and adjacent prose.
- The interactive architecture HTML was inspected at 1440×1200. Its report container and export
  controls render without altering runtime assets.
- The actual unauthenticated GitHub repository page was inspected at 1440 px after publication:
  `clientWidth == scrollWidth == 1440`, and all six README images completed with the expected alt
  text and intrinsic dimensions.

The browser screenshots are transient QA artifacts and are not part of the public repository.

## ImageGen Provenance

Built-in ImageGen was used only for the decorative hero. Three candidates were generated
independently; candidate C was selected. The final generation prompt was:

```text
Use case: stylized concept for an open-source GitHub README hero. Create an abstract technical
flow sculpture with exactly one parent, two isolated lanes, evidence tokens, and one merge.
Use a clean soft-gray 16:9 canvas and matte 3D forms. No text, text-like lines, letters, numbers,
checkmarks, documents, UI, logos, people, robots, brains, clouds, or code.
```

The selected PNG was visually inspected and converted locally to WebP; no generated source text
or provider identity appears in the committed asset.

## Persistence And Restart Evidence

`NOT_RUN_NO_PERSISTENT_SERVICE`. This change contains documentation, static assets, tests, and
Flow evidence only. It does not alter a running service, installed skill bundle, account, model,
provider, proxy, token, or lifecycle state.

## Open Questions And Defaults

- Q-RVP-001 is answered: candidate C is the accepted hero.
- Q-RVP-002 is answered: the user explicitly authorized a fresh-clone normal push to the existing
  public `main`; no broader publication authority was used.

## Residual Risks

- Fine SVG labels are intentionally compact on a 390 px screen. The main path is visible; alt
  text, captions, and prose carry the full accessible explanation.
- The decorative hero was human-reviewed rather than OCR-scanned. It contains no visible text or
  privacy-bearing detail, and deterministic diagrams carry all normative meaning.

## Rollback Or Disable Path

Use a normal follow-up revert of public content commit `04487d8`; do not force-push or rewrite
history. Removing the six README image blocks and new documentation/assets restores the previous
presentation without changing runtime behavior.

## Completed Release Steps

1. Cloned current public `main@ce6c6c1` into a fresh temporary directory without attaching the
   internal repository history.
2. Preserved the public ROADMAP update, transferred only the accepted candidate, reran the full
   Gate, and committed with the configured GitHub noreply author.
3. Performed a normal push of content commit `04487d8`; no force push, tag/Release change, or
   external promotion occurred.
4. Verified GitHub Actions run `30895434940`, the public English/Chinese README, all six
   unauthenticated asset URLs, and the actual GitHub render.

## Final Gate

RVP-00 through RVP-08 are accepted. The six-image bilingual README enhancement is online and
verified; this Flow is complete.
