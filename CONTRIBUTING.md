# Contributing

Thanks for helping improve `adaptive-subagent-orchestration`. Keep changes small, portable, and tied to the frozen public boundary.

## Before editing

Read [SKILL.md](SKILL.md), the [architecture](docs/architecture/oss-launch-architecture.md), and the [v1 contract](docs/contracts/oss-launch-contract.md). Preserve the ownership rule: every writable path has one owner for the full run, and shared integration files stay with the parent thread.

## Changes and tests

- Keep runtime files dependency-free and account/provider-neutral. Do not add credentials, tokens, private routes, absolute maintainer paths, or local runtime configuration.
- Update the relevant forward case or documentation when a public contract changes. Do not edit the runtime package to solve an unrelated documentation issue.
- Run `python3 -m unittest discover -s tests -v`, `./scripts/validate.sh .`, `python3 -m compileall -q scripts`, and `git diff --check` before opening a pull request.
- Keep examples reproducible from a fresh checkout. Use relative links for repository files and describe unverified runtime claims as `UNVERIFIED`.

## Pull requests

Explain the user-facing outcome, changed paths, tests and residual risks. Keep unrelated formatting and generated assets out of the change. A maintainer will decide whether a contract or release gate needs an explicit update.
