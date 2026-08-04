# Adaptive Subagent Orchestration OSS Launch Release Readiness

Last verified: 2026-08-04

## Decision

**The public Release Candidate is verified and release packaging is in progress.** The
clean Public repository, GitHub Actions matrix, and fresh-clone lifecycle Gate have
passed. The approval covers the `v0.1.0` tag and GitHub Release. External promotion is
still outside this Flow.

The public candidate must use a new clean history. The existing internal root commit
contains earlier maintainer paths and local runtime-route evidence, and its author email
is not a GitHub noreply address. It must not be pushed to the public repository.

## Delivered Scope

- Provider/model/account-neutral English runtime skill and UI metadata.
- L0-L3 routing, full-run file ownership, structured results, evidence invalidation,
  transport boundaries, and one focused retry with Delta.
- Safe install, replace, backup, validate, and uninstall lifecycle with manifest
  checksums and target locking.
- Bilingual README, governance, public cases, runtime matrix, architecture, frozen v1
  contract, and sanitized forward evidence.
- Standard-library contract/lifecycle/docs/privacy tests and macOS/Linux CI definition.
- Apache-2.0 license approved for publication.

## Node Evidence

| Node | Gate | Actual result | Evidence |
| --- | --- | --- | --- |
| OSS-00 Baseline | Original recursive tests, compile, diff | 12/12 PASS; exits 0 | Flow status and initial revision `8c76b63` |
| OSS-01 P0 | Current adjacent-project review | Crowded but differentiable | `docs/open-source-research.md` |
| OSS-02 Audit | Architecture/security risk audit | Five P0 blockers mapped to owners/Gates | Architecture and contract |
| OSS-03 Architecture | HTML structure/render and docs tests | 2/2 PASS; Chrome render inspected | `docs/architecture/oss-launch-architecture.*` |
| OSS-04 Runtime | Runtime contract tests and skill validator | 12/12 PASS; `Skill is valid!` | `SKILL.md`, `agents/openai.yaml`, contract tests |
| OSS-05 Lifecycle | Isolated lifecycle suite | 10/10 PASS; shell syntax PASS | `scripts/`, `tests/test_install.py` |
| OSS-06 Docs | Bilingual docs/governance/cases | Scope/privacy/diff Gate PASS | README files, governance, cases, matrix |
| OSS-07 Integration | Recursive regression and build/static Gates | 29/29 PASS; source, compile, shell, YAML, license, privacy, diff PASS | full candidate |
| OSS-08 QA | Independent read-only QA and fresh-copy lifecycle | 29/29 independent PASS; clean post-test status; fresh-copy install/replace/backup/uninstall PASS | QA result and A0 fresh-copy terminal marker |

## Integration And Security Evidence

Required commands on the final candidate:

```bash
./scripts/validate.sh .
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts tests
bash -n scripts/install.sh scripts/uninstall.sh scripts/validate.sh
git diff --check
```

Results: all exit `0`; recursive discovery runs 29 tests. The privacy Gate checks current
tracked and untracked text files for maintainer paths, credential shapes, private route
names, endpoints, and model/provider assignments. Regex-fixture source files are excluded
from self-matching but their runtime artifacts remain covered by focused tests.

Security-negative lifecycle cases cover invalid/relative/wrong-name targets, symlink
target/parent rejection, target lock conflicts, existing install conflict, and modified
owned-file uninstall rejection with preservation.

## Browser / Visual Evidence

`docs/architecture/oss-launch-architecture.html` was rendered in headless Chrome at
1440×1200. The diagram visibly contains the source repository, contract/CI, lifecycle,
installed bundle, parent Codex, L0-L3 router, bounded agents, manual gate, and GitHub
Release boundary without overlapping components that obscure the flow.

No product UI is shipped, so browser/E2E is informational beyond the architecture
artifact.

## Persistence And Restart Evidence

No service or database persistence exists. The relevant persistence surface is the
filesystem lifecycle: a fresh isolated copy installed, validated, replaced with exactly
one sibling backup, and uninstalled successfully. Therefore application restart testing
is `NOT_RUN_NO_PERSISTENT_SERVICE`.

## Open Questions And Defaults

- OSS-09 approved: `hongkai-hue/adaptive-subagent-orchestration`, Public, Apache-2.0,
  and a new one-commit clean public history using a GitHub noreply author.
- Non-blocking language default: English canonical runtime with full Chinese README.
- Support claim default: advertise only the static, lifecycle, and representative
  forward evidence currently recorded; keep CLI/full App/OS/runtime identity unverified.

## Residual Risks

- A natural-language skill cannot enforce OS-level file locks or deterministic host
  behavior.
- Implicit invocation and exact runtime identity remain unverified.
- GitHub Actions passed on macOS with Python 3.12 and Ubuntu with Python 3.9 and 3.12.
- Windows lifecycle support is outside v0.1.
- Existing internal Git history is private-only and must not be attached to the public
  remote.
- External promotion is outside this Flow and needs a separate authorization.

## Rollback Or Disable Path

- Before publication: keep the internal repository and do not create a remote.
- After publication: fix with a normal follow-up commit and patch release; do not
  force-push or rewrite public history without explicit authorization.
- Installed users can run `./scripts/uninstall.sh --target user --dry-run`, then the
  non-dry-run command. Modified owned files are preserved and reported.
- Replacement keeps the previous installed bundle as a sibling backup.

## Manual Release Steps

With OSS-09 explicitly approved:

1. Create an isolated clean export of the accepted candidate without internal `.git`.
2. Initialize `main` with the approved GitHub noreply author and one release commit.
3. Re-run all required Gates in that clean repository.
4. Create the authorized public GitHub repository and push `main`.
5. Verify repository visibility, default branch, About/topics, license recognition, and
   GitHub Actions.
6. Fresh-clone the public URL and rerun source validation, 29 tests, compile, shell,
   install, installed validation, replace/backup, and uninstall.
7. Update pre-release wording only after the public candidate and CI pass.
8. Commit the release-state wording, tag `v0.1.0`, and create the GitHub Release.
9. Verify the Release and public README from unauthenticated URLs.

## Final Gate

The local and public Release Candidate Gates are accepted. The overall online goal remains
in progress until OSS-11 completes.
