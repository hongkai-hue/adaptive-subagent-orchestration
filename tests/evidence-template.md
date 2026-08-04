# Forward-test evidence template

```yaml
date: YYYY-MM-DD
codex_version: "..."
surface: app | cli
os: "..."
scenario: "..."
expected_route: L0 | L1 | L2 | L3 | SERIAL | BLOCKED
observed_route: L0 | L1 | L2 | L3 | SERIAL | BLOCKED
roles_requested: []
runtime_identity: VERIFIED | UNVERIFIED
owned_paths: {}
changed_paths: []
validation_commands: []
exit_codes: []
result: PASS | FAIL | BLOCKED
residual_risks: []
```

Do not include private paths, credentials, endpoints, account details, provider/model
routing, private source, or unredacted logs. A role name or local configuration is not
request-level runtime identity.
