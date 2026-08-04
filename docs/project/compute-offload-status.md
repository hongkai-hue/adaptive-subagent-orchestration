# Compute Offload Status

Last verified: 2026-08-04T23:31:00+08:00

| Node | State | Owner | Evidence | Attempts | Lease / agent | Blocker / next action |
| --- | --- | --- | --- | ---: | --- | --- |
| CO-00 | accepted | A0 | `main@14a75c8`; source valid; 33/33 recursive tests PASS | 1 | none | none |
| CO-01 | accepted | A0 | architecture Markdown complete; HTML inspected at 1440×1200 with no page overflow | 1 | A0 | none |
| CO-02 | accepted | A0 | compute-offload contract v1 frozen after read-only audit; order, D1, sequencing, review, safety, migration fixed | 1 | A0 | none |
| CO-03 | accepted | A0 | schema v2; 25 fixtures; focused contract/docs tests PASS | 1 | A0 | none |
| CO-04 | accepted | A0 | balanced + D1 runtime, sequential discovery/review, neutral metadata; source validation PASS | 1 | A0 | none |
| CO-05 | accepted | A0 | bilingual guidance, five-level routing graphic, D1 case, evidence/matrix/template updates | 1 | A0 | none |
| CO-06 | accepted | A0/QA | source valid; 36/36 recursive tests, compile, shell syntax, and diff check PASS | 1 | A0 | none |
| CO-07 | accepted | A0 | user policy updated; legacy bundle preserved as sibling backup; managed active bundle validated and byte-matched | 1 | none | none |
| CO-08 | waiting_for_manual_gate | user/A0 | public target recorded | 0 | none | exact push confirmation after local RC |

## State Rules

`not_started / in_progress / blocked / ready_for_review / accepted / needs_rework / waiting_for_manual_gate / cancelled`

## Active Worker Registry

| Agent ID | Node | Base revision | Scope | Started | Lease expires | State |
| --- | --- | --- | --- | --- | --- | --- |
| `/root/co_contract_audit2` | CO-03/04/05 | `14a75c8` | read-only routing, fixtures, docs, compatibility | 2026-08-04 | closed | PASS; schema, safety, review, and compatibility deltas returned |
| `/root/co_local_route_audit2` | CO-07 | `14a75c8` | read-only local policy/install/role boundary | 2026-08-04 | closed | PASS; active drift, migration, and static-identity limits returned |

## Latest Recovery Check

- Worktree inspected: yes; clean at baseline
- Accepted Gates rerun: source validation, 36-test recursive suite, Python compile, shell syntax, diff check
- Local activation: managed bundle manifest valid; runtime files match canonical source; three role routes statically match the requested local configuration
- Runtime identity: still `UNVERIFIED` without request-level evidence
- Drift found: legacy active bundle had no ownership manifest; preserved as a recoverable sibling backup before fresh installation
