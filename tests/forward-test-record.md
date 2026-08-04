# Sanitized forward-test record

Date: 2026-08-04
Status: representative local evidence; not a universal runtime guarantee

## Evidence levels

- Static contract evidence checks skill text, UI metadata, fixtures, and privacy rules.
- Lifecycle evidence checks install, replace, backup, validation, and uninstall in
  isolated temporary directories.
- Forward evidence observes route selection, roles, changed paths, result packets, and
  the parent final Gate in isolated tasks.

Static or lifecycle PASS does not prove that every Codex release, surface, account,
provider, model, permission mode, or reasoning setting behaves identically. Runtime
identity in this public record is `UNVERIFIED`.

## Contract regression

Run:

```bash
python3 -m unittest discover -s tests -v
```

The forward fixture covers L0, L1, L2, L3, `SERIAL`, and `BLOCKED`, including shared
ownership, candidate invalidation, transport boundaries, retry-without-Delta, recursive
delegation rejection, sensitive context, migration/release, and live-capacity batching.

## Representative local forward observations

| Scenario | Observed result | Evidence status |
| --- | --- | --- |
| L0 single-file task | Parent selected L0 and created no subagent | VERIFIED for the recorded desktop run |
| Shared hotspot | Parallel writers were rejected; the parent retained one owner | VERIFIED for the recorded desktop run |
| L3 cross-module contract | The lightweight workflow handed off to heavy orchestration | VERIFIED for the recorded desktop run |
| L1 read-only audit | Two explorers returned structured results with `Changed: none` | VERIFIED for the recorded desktop run |
| L2 disjoint implementation | Two workers changed only their independent files | VERIFIED for the recorded desktop run |
| L2 parent final Gate | The parent reran the complete two-test Gate and it passed | VERIFIED for the recorded desktop run |
| Incomplete lane packet | The agent returned `BLOCKED` before writing | VERIFIED for the recorded desktop run |
| Candidate evidence invalidation | A candidate change invalidated the prior hash and caused a new Gate | VERIFIED for the recorded desktop run |
| Agent lifecycle | Valid results were accepted before completed agents were closed | VERIFIED for the recorded desktop run |

## Runtime surface boundary

| Claim | Status | Reason |
| --- | --- | --- |
| Representative desktop route selection | PARTIAL | Only the recorded scenarios were observed |
| Subagent role selection and result retrieval | PARTIAL | Roles and structured results were observed in recorded scenarios |
| Exact account/provider/model/reasoning identity | UNVERIFIED | No sanitized request-level identity is included |
| CLI runtime | UNVERIFIED | No public request-level CLI run is included |
| Implicit invocation | UNVERIFIED | Eligibility metadata does not prove deterministic triggering |

Use [evidence-template.md](evidence-template.md) for future runs. Do not add private
paths, credentials, endpoints, account details, local routing configuration, or private
project output to a public record.
