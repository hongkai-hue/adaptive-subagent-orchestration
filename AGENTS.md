# Project guidance

This repository is the canonical source for `adaptive-subagent-orchestration`.

- Keep `SKILL.md` and `agents/openai.yaml` as the only canonical runtime sources.
- The installer may copy only those runtime files and its ownership manifest.
- Keep runtime behavior provider/model/account neutral and dependency-free.
- Do not add credentials, endpoints, private routes, private paths, or local agent configuration.
- Use Python standard library for project tests and lifecycle implementation.
- Static tests do not prove Codex runtime identity; mark unsupported claims `UNVERIFIED`.
- Update a forward fixture before changing a routing contract.
- Do not edit user `AGENTS.md`, provider config, custom agent TOML, or a real user skill directory during tests.
- Update `ROADMAP.md` after verified project changes.
- Run `./scripts/validate.sh .`, `python3 -m unittest discover -s tests -v`, `python3 -m compileall -q scripts tests`, `bash -n scripts/*.sh`, and `git diff --check` before completion.
