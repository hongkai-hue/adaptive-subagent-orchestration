# Case: Independent write lanes

This case demonstrates when L2 is appropriate. It is a routing contract example, not a speed or token-saving guarantee.

## Situation

A task is expected to take more than twenty minutes and contains two independently testable changes:

- `alpha/` contains a calculation change with its own tests.
- `beta/` contains a text-formatting change with its own tests.

The two scopes have no shared file, generated output, migration, release step, or sensitive input. The parent thread owns integration and the final Gate.

## Route

Use two `worker` lanes in L2. The owner matrix remains stable for the whole run:

| Scope | Owner | Lane | Gate |
| --- | --- | --- | --- |
| `alpha/` | Worker A | L2-alpha | `alpha` tests and changed-path check |
| `beta/` | Worker B | L2-beta | `beta` tests and changed-path check |
| Integration and final candidate | Parent | Main thread | Full project Gate |

Each lane receives a complete packet with Goal, Done when, exact scope, first checkpoint, and required structured result. A lane must stop before writing if the packet is incomplete or its owner conflicts with the matrix.

## Acceptance

The parent accepts a lane only when its result reports `Status: PASS`, changed paths stay within its scope, and its evidence names the commands or relevant lines. After both lanes return, the parent rechecks the candidate and runs the final Gate. Any candidate change invalidates earlier evidence and requires a new Gate.

If the scopes begin to overlap, a dependency appears, or context cannot be minimized, stop the split and continue serially. Transport completion alone is not a business pass.
