# Project guidance

This repository is the canonical source for the Adaptive Subagent Orchestration suite.

- Keep root `SKILL.md` and `agents/openai.yaml` as the canonical adaptive runtime sources.
- Keep `skills/orchestrate-heavy-goals/**` as the canonical heavy runtime source.
- The lifecycle may copy only files declared by the selected runtime bundle and its ownership manifest; never copy docs, tests, local policy, or private configuration.
- Keep runtime behavior provider/model/account neutral and dependency-free.
- Do not add credentials, endpoints, private routes, private paths, or local agent configuration.
- Use Python standard library for project tests and lifecycle implementation.
- Static tests do not prove Codex runtime identity; mark unsupported claims `UNVERIFIED`.
- Update a forward fixture before changing a routing or L3 handoff contract.
- Do not edit user `AGENTS.md`, provider config, custom agent TOML, or a real user skill directory during tests.
- Update `ROADMAP.md` after verified project changes.
- Run `./scripts/validate.sh .`, `python3 -m unittest discover -s tests -v`, `python3 -m compileall -q scripts tests`, `bash -n scripts/*.sh`, and `git diff --check` before completion.
