# Integrated Heavy Goals Release Readiness

## Decision

Ready as a local v0.2.0 Release Candidate after the committed fresh-clone Gate. Public push, tag,
and GitHub Release are not authorized by this decision and remain IHG-11.

## Delivered Scope

- One repository contains canonical adaptive and self-contained heavy runtime bundles.
- Adaptive L3 closes existing lanes and transfers an exact, digest-bound `l3-v1` packet to the
  same parent-thread heavy A0.
- Lifecycle CLI preserves adaptive-only defaults and adds manifest-v2 `adaptive|heavy|all`
  installation, validation, atomic replacement/rollback, and logical uninstall.
- Bilingual README, an inspected closed-loop route visual, a public end-to-end L3 case, frozen
  contracts, fixtures, templates, changelog, runtime matrix, and Flow evidence are included.

## Node Evidence

| Node | Gate | Actual result | Evidence |
| --- | --- | --- | --- |
| IHG-01 | Architecture structure and visual inspection | PASS | Markdown/HTML tests plus 1440×1200 inspection without page overflow |
| IHG-02 | Frozen contract audit | PASS after one rework | Exact packet, fixture, manifest, CLI, lock, rollback, and migration rules |
| IHG-03/05 | Both runtime contracts | PASS | Heavy self-containment and adaptive handoff tests |
| IHG-04 | Lifecycle matrix and fault injection | PASS | v1 upgrade, exact trees, stage/activation rollback, partial suite, cleanup debt |
| IHG-06/07 | Recursive tests and public docs | PASS | 60 tests, links, SVG safety, bilingual visual manifest, privacy scan |
| IHG-09 | Managed active suite | PASS | two validated v2 manifests, source/target capabilities, byte equality |
| IHG-10 | Final candidate | PASS | `45dd582`; fresh clone source, 60 tests, compile, shell syntax, diff and clean-status Gates PASS |

## Integration And Security Evidence

- `./scripts/validate.sh .` returns a valid two-source suite.
- The recursive suite passes with both managed active runtime paths supplied for byte comparison.
- Public privacy scans reject credentials, private paths, endpoints, provider/model routes, and
  account-specific values.
- Lifecycle targets reject symlink traversal, unknown entries, checksum drift, partial-suite
  uninstall, unrecognized private directories, and source-tree custom roots.

## Browser / Visual Evidence

- Integrated architecture HTML was inspected at 1440×1200 with no page overflow.
- Updated `routing-levels.svg` was rendered at 1200 px and visually inspected; all five routes,
  the bundled L3 loop, and SERIAL/BLOCKED boundary remain legible without clipping.

## Persistence And Restart Evidence

- Flow architecture, contracts, DAG, status, questions, and readiness are persisted in the repo.
- Both managed active Skills validate from disk with manifest v2.
- Universal host rediscovery after restart remains `UNVERIFIED`; no broader runtime claim is made.

## Open Questions And Defaults

- Public push, tag, and Release remain a manual Gate.

## Residual Risks

- Codex host implicit invocation and exact request-level runtime identity remain `UNVERIFIED`.
- Heavy recovery is artifact-backed workflow discipline, not an external persistent scheduler.
- Windows lifecycle behavior is outside the current support claim.
- Public `main`, CI on the v0.2 candidate, tag, and Release remain unverified until IHG-11.

## Rollback Or Disable Path

- Adaptive v1 and the prior private heavy runtime were preserved as sibling backups during local
  activation; restore only after moving the managed v2 targets aside and revalidating the chosen
  backup.
- A valid managed suite can be previewed with `uninstall.sh --skills all --dry-run`; actual
  uninstall is a separate destructive lifecycle decision and was not performed on the active suite.

## Manual Release Steps

1. Obtain exact authorization for normal push scope; separately confirm tag and GitHub Release.
2. Publish through a fresh temporary clone without force push or internal history leakage.
3. Verify remote SHA, CI jobs, both READMEs, L3 case, both Skills, fixtures, and image assets through
   unauthenticated public URLs.
4. Create a tag or Release only if its exact scope was approved.

## Final Gate

Before local acceptance and again in a fresh clone:

```bash
./scripts/validate.sh .
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests skills/orchestrate-heavy-goals/scripts
bash -n scripts/*.sh
git diff --check
```

The local candidate and committed fresh clone pass all five Gates. IHG-10 is accepted; IHG-11
remains `waiting_for_manual_gate` and this document does not authorize public mutation.
