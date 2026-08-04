# Compute Offload Release Readiness

## Decision

Local Release Candidate ready. Public publication remains blocked on the explicit manual push
Gate; this document is not a push authorization.

## Delivered Scope

- Opt-in `compute-offload` mode with `balanced` as the backward-compatible default.
- D1 admission for one bounded worker, sequential discovery, and optional read-only review.
- Fixed routing precedence: L3, safety outcomes, mode, then eligible route.
- Schema-v2 fixtures, bilingual docs, public case, five-level route graphic, and host template.
- Local policy activation and managed active-skill installation with recoverable legacy backup.

## Node Evidence

| Node | Gate | Actual result | Evidence |
| --- | --- | --- | --- |
| CO-01 | Architecture structure and visual inspection | PASS | Markdown boundaries present; HTML inspected at 1440×1200 without page overflow |
| CO-02 | Frozen contract audit | PASS | mode precedence, D1 thresholds, safety, sequencing, review, compatibility fixed |
| CO-03 | Fixture and test contract | PASS | schema v2, 25 cases, focused tests PASS |
| CO-04 | Runtime contract | PASS | source bundle valid; neutral runtime and metadata assertions PASS |
| CO-05 | Docs and cases | PASS | bilingual links, local assets, D1 case, privacy assertions PASS |
| CO-06 | Integrated candidate | PASS | 36/36 recursive tests, compile, shell syntax, and diff check PASS |
| CO-07 | Local activation | PASS | policy present; active bundle valid, manifested, and byte-equal to canonical runtime |

## Integration And Security Evidence

- Public-candidate privacy scan rejects credentials, private routes, private source paths, and
  provider/model assignments.
- The runtime and public docs remain account/provider/model neutral.
- No authentication, proxy, desktop parent route, or role configuration was modified.
- Static role configuration matches the requested host route, but request-level identity remains
  `UNVERIFIED`.

## Browser / Visual Evidence

- Interactive compute-offload architecture rendered at 1440×1200 without page overflow.
- Updated routing SVG was rendered and visually inspected; five cards and the safety rail are
  readable without cross-card text overflow.

## Persistence And Restart Evidence

- Active runtime has a valid ownership manifest and passes installed-bundle validation.
- Canonical and active runtime files compare byte-for-byte equal.
- Host policy contains the explicit compute-offload rule.
- Application restart and request-level D1 observation are not part of the static Gate.

## Open Questions And Defaults

- Q-CO-003 remains open: public `main` push requires explicit user authorization.
- `balanced` remains the public default; local host policy selects compute-offload for eligible
  daily implementation work.

## Residual Risks

- A host may not invoke the skill implicitly; explicit invocation remains the reliable route.
- Static role configuration does not prove which request path a future runtime call uses.
- D1 delegates model reasoning and tool control; build and test commands still use host resources.
- More delegation can add inference cost and latency when admission is misclassified.

## Rollback Or Disable Path

- Remove or narrow the compute-offload paragraph in the user-level routing policy.
- Validate the preserved legacy sibling backup before any manual restoration.
- Use the lifecycle uninstall only for the managed active target and only after a dry run; never
  delete a backup as part of rollback.

## Manual Release Steps

1. Receive explicit authorization for Q-CO-003.
2. Create a new temporary clone of the public repository.
3. Copy only the accepted public candidate, run the full Gate, commit, and use a normal push.
4. Verify the remote commit, GitHub Actions, README rendering, and public asset links.

## Final Gate

```text
./scripts/validate.sh .                                      PASS
python3 -m unittest discover -s tests -v                     PASS (36 tests)
python3 -m compileall -q scripts tests                       PASS
bash -n scripts/*.sh                                         PASS
git diff --check                                             PASS
```

Release readiness: `READY_FOR_MANUAL_PUSH_GATE`.
