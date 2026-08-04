# Runtime Surface Matrix

Last reviewed: 2026-08-04. This matrix separates repository and lifecycle evidence from claims that require a request-level Codex runtime observation. `VERIFIED` means the linked sanitized record or test directly covers the behavior; `PARTIAL` means only a narrower behavior is covered; `UNVERIFIED` means no public request-level evidence is available; `OUT OF SCOPE` is deliberately not a v0.1 promise.

| Surface or claim | Status | Evidence and boundary |
| --- | --- | --- |
| Canonical `SKILL.md` and UI metadata shape | VERIFIED | `tests/test_contract.py` and source validation cover the public text contract. |
| Install, replace, backup, validate, and fail-closed uninstall | VERIFIED | `tests/test_install.py` covers lifecycle paths; scripts manage only manifest-owned runtime files. |
| Explicit `$adaptive-subagent-orchestration` invocation | PARTIAL | Runtime guidance and UI metadata define the invocation; the forward record covers representative desktop routing, not every host. |
| L0 main-thread routing | VERIFIED | Sanitized forward record includes an L0 single-file scenario. |
| L1 read-only role selection | VERIFIED | Sanitized forward record includes two independent `explorer` results. |
| L2 disjoint write lanes and parent integration | VERIFIED | Sanitized forward record includes independent worker scopes and a passing final Gate. |
| Shared-hotspot serial routing | VERIFIED | Sanitized forward record and [serial case](cases/shared-hotspot-serial.md) cover the single-owner boundary. |
| L3 heavy-orchestration handoff | VERIFIED | Sanitized forward record covers a cross-module contract handoff; this skill does not implement L3. |
| Structured result retrieval and changed-path evidence | VERIFIED | Forward record covers `PASS`, `BLOCKED`, changed paths, and final Gate checks. |
| Candidate change invalidates old evidence | VERIFIED | Forward record records a changed candidate hash followed by a rerun. |
| Implicit invocation | UNVERIFIED | `allow_implicit_invocation` is eligibility metadata, not deterministic triggering. |
| Exact account, provider, model, or reasoning identity | UNVERIFIED | No sanitized request-level identity is published; static configuration is not proof. |
| Codex App / desktop surface | PARTIAL | Representative desktop route selection is recorded; full installation and identity coverage are not. |
| Codex CLI surface | UNVERIFIED | No public request-level CLI run record is included in this candidate. |
| macOS runtime | UNVERIFIED | Package paths are portable, but no public OS-specific runtime record is used as a universal claim. |
| Linux runtime | UNVERIFIED | Package paths are portable, but no public OS-specific runtime record is used as a universal claim. |
| Windows runtime | OUT OF SCOPE | No native Windows lifecycle implementation or Gate is claimed for v0.1. |
| Plugin, connector, or remote service behavior | OUT OF SCOPE | The skill has no MCP, app, connector, or network dependency. |

The source repository and installed bundle are different surfaces. A passing static or lifecycle test cannot prove that every Codex host discovers, triggers, schedules, or identifies the skill in the same way. Update this matrix only when new sanitized evidence is recorded; do not infer runtime identity from local configuration.
