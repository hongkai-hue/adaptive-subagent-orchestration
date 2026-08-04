# Case: Shared hotspot stays serial

This case demonstrates why two apparently parallel writes can be unsafe. It is a routing contract example, not a claim about runtime performance.

## Situation

Two requested changes both modify `config/core.toml`. One change adjusts a default and the other changes a related section. The file is a shared hotspot, so the changes can overwrite one another or make either test observe an intermediate state.

## Route

Keep the work on the main thread as `SERIAL`; create no write lanes. The parent holds the only owner for `config/core.toml`, orders the edits, and runs the final Gate after the complete file is coherent.

| Scope | Owner | Route | Reason |
| --- | --- | --- | --- |
| `config/core.toml` | Parent | `SERIAL` | Shared writable path; one owner is required. |
| Read-only context, if safe to separate | Optional `explorer` | L1 only | Investigation must not receive sensitive context or write. |

The parent should explain the conflict, record the intended order, and verify the final changed path. It must not delegate a writer merely to reduce wall-clock time. If the task grows into a cross-module contract or multi-wave recovery problem, hand it to L3 heavy orchestration instead of running a second router.

## Acceptance

The expected outcome is a main-thread result with a final Gate, not two agent reports. A request to parallelize the shared file is a safety failure and should be returned as `BLOCKED` or routed to `SERIAL` before any write occurs.
