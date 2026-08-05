# QA Gates

Run Gates from narrow to broad:

1. Baseline before changes.
2. Node unit/static/document checks.
3. Contract producer/consumer, error, and state checks.
4. Integration with real in-scope modules.
5. Security Negative for authorization, traversal, isolation, or controlled input.
6. Browser/E2E for real routes, interaction, console, network, empty/error/long states.
7. Persistence/Restart for stored state.
8. Recursive Regression through the project's default entry point.
9. Build/Artifact for distributable output.
10. Release Candidate evidence and risks.

Mark every Gate `required`, `conditional`, or `informational` before execution. Architecture,
Contract, each Implementation Node, Integration, and Recursive Regression are required for every
Flow. UI adds Browser/E2E; persistence adds Restart; auth or controlled data adds Security Negative;
distributable output adds Build/Artifact.

A required Gate cannot be skipped, faked, mocked, or replaced by `NOT_RUN`. Missing required
environment leaves the node blocked or the candidate not ready. Conditional or informational
omissions use `NOT_RUN_<REASON>` in Release Readiness.

## Evidence

Prefer a unique terminal marker plus exit code and test count:

```text
<FLOW>_<GATE>_PASS
<FLOW>_<GATE>_FAIL
<FLOW>_<GATE>_NOT_RUN_<REASON>
```

Conflicting marker and exit code is failure. Transport or agent completion is never a business
PASS. Candidate changes invalidate affected evidence.

## Anti-false-positive Rules

- Do not swallow exceptions or bypass the behavior under test.
- Fake/mock modes identify themselves and satisfy informational evidence only.
- Confirm recursive discovery includes nested new tests.
- Include at least one failure path for high-risk behavior.
- Browser QA checks console and request status, not only screenshots.
- QA identifies failure ownership and does not repair the product it certifies.

Database changes have separate Gates for plan, editing migration files, local disposable validation,
shared test, staging, and production. Empty initialization, existing-data upgrade, failure recovery,
compatibility window, and rollback are required after editing is authorized.

## Failure Routing

```text
Node failure -> implementation owner
Contract mismatch -> A0 contract review and consumer invalidation
Integration-only failure -> integration owner after isolation
Missing environment -> blocked or explicit NOT_RUN
Visual judgment -> manual Gate
Release action -> manual Gate
Third repeated failure -> reference implementation, smaller reproduction, or architecture review
```
