# Forward-test evidence template

```yaml
date: YYYY-MM-DD
codex_version: "..."
surface: app | cli
os: "..."
scenario: "..."
mode: balanced | compute-offload
expected_route: L0 | D1 | L1 | L2 | L3 | SERIAL | BLOCKED
observed_route: L0 | D1 | L1 | L2 | L3 | SERIAL | BLOCKED
handoff_version: l3-v1 | none
handoff_state: HANDOFF_BLOCKED | CANCEL_THEN_HANDOFF | HANDOFF_READY | HEAVY_FLOW_ACTIVE | HEAVY_ACCEPTED | WAITING_FOR_MANUAL_GATE | none
ownership_epoch: integer | none
adaptive_owner: active | cancelling | released | none
heavy_owner: none | pending | active
roles_requested: []
runtime_identity: VERIFIED | UNVERIFIED
owned_paths: {}
changed_paths: []
validation_commands: []
exit_codes: []
result: PASS | FAIL | BLOCKED
residual_risks: []
manual_gates: []
```

Do not include private paths, credentials, endpoints, account details, provider/model
routing, private source, or unredacted logs. A role name or local configuration is not
request-level runtime identity.
