# Integrated Heavy Goals Status

Last verified: 2026-08-05

| Node | State | Owner | Evidence | Attempts | Lease / agent | Blocker / next action |
| --- | --- | --- | --- | ---: | --- | --- |
| IHG-00 | accepted | A0 | `main@aa684f2`; source valid; 36/36 tests PASS; project rules updated | 1 | none | none |
| IHG-01 | accepted | A0 | architecture audit PASS; HTML inspected at 1440×1200 with no page overflow | 1 | A0 | none |
| IHG-02 | accepted | A0 | two audits closed schema, state, ownership, allowlist, capability, partial-suite, lock, rollback, fixture, and CLI defaults | 2 | A0 | none |
| IHG-03 | accepted | A0 | self-contained Heavy Skill, 7 references, metadata, and safe scaffold; contract/scaffold tests PASS | 1 | A0 | none |
| IHG-04 | accepted | A0 | manifest v2, selectors, exact trees, v1 reader, atomic rollback, partial-suite and cleanup-debt tests PASS | 1 | A0 | none |
| IHG-05 | accepted | A0 | adaptive runtime contains exact `l3-v1` identity, owner release, capability and fail-closed handoff | 1 | A0 | none |
| IHG-06 | accepted | A0 | schema-v3 adaptive fixtures, 8-case L3 fixture, 60-test recursive suite PASS | 1 | A0 | none |
| IHG-07 | accepted | A0 | bilingual README, closed-loop SVG, public L3 case, templates, changelog, links and privacy tests PASS | 1 | A0 | none |
| IHG-08 | accepted | A0/QA | this Flow produced architecture, contracts, DAG, status and readiness; SVG visually inspected; final local Gate PASS | 1 | A0 | none |
| IHG-09 | accepted | A0 | both managed local runtimes validate as v2; adaptive/heavy capabilities and byte equality tests PASS; prior runtimes preserved as backups | 1 | A0 | none |
| IHG-10 | accepted | A0 | `45dd582`; fresh clone source validation, 60 tests, compile, shell syntax, diff check and clean status PASS | 1 | A0 | none |
| IHG-11 | accepted | user/A0 | public `main` and `v0.2.0` point to `35f620e`; CI run `30972450660` has 3/3 jobs PASS; Release and public HTTP checks PASS | 2 | A0 | none |

## State Rules

`not_started / in_progress / blocked / ready_for_review / accepted / needs_rework / waiting_for_manual_gate / cancelled`

## Active Worker Registry

| Agent ID | Node | Base revision | Scope | Started | Lease expires | State |
| --- | --- | --- | --- | --- | --- | --- |

## Latest Recovery Check

- Worktree inspected: yes; clean at baseline
- Accepted Gates rerun: source-suite validation, 60-test recursive suite with both active runtimes, compile, shell syntax, diff check, fresh public clone, three-job CI, main/tag/release/public HTTP checks
- Drift found: the first published test candidate exposed a Linux-only test-path defect; fixed by `35f620e`, then all required Gates passed
