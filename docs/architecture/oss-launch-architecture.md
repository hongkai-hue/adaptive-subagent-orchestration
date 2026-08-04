# Adaptive Subagent Orchestration OSS Launch Architecture

## Context And Constraints

`adaptive-subagent-orchestration` is a small Codex workflow skill, not a standalone
scheduler. It helps the parent Codex agent choose between local execution, read-only
delegation, isolated write lanes, and a handoff to heavy orchestration.

The open-source package must remain useful without the maintainer's local model,
provider, proxy, account, or agent configuration. Its runtime has no network access of
its own and no third-party dependency. The repository adds documentation, tests, and
distribution tooling, but the installed skill contains only the runtime artifacts.

Constraints:

- Team: one maintainer initially; contributors can work through pull requests.
- Scale: one skill package, tens of contract fixtures, and a small test suite.
- Lifespan: maintained public project with semantic releases.
- Supported v0.1 surfaces: Codex app and CLI on tested macOS/Linux environments.
- Runtime dependency: Codex must provide skill discovery and subagent capabilities.
- Safety: installation cannot edit account, provider, model, proxy, agent TOML, or
  global `AGENTS.md` settings.
- Publication: remote repository creation, push, tag, release, and promotion remain
  explicit manual gates.

## Quality Attributes

1. **Portable**: no absolute maintainer path or private runtime route is required.
2. **Bounded**: the skill owns routing policy, not Codex's orchestration runtime.
3. **Fail-closed**: ambiguous ownership, unsafe paths, or modified installed files
   block destructive update/uninstall behavior.
4. **Reproducible**: public claims map to standard-library tests or a documented
   forward-test evidence record.
5. **Minimal**: installed files are `SKILL.md`, `agents/openai.yaml`, and an ownership
   manifest only.
6. **Recoverable**: replacement creates a sibling backup and uninstall preserves
   user-modified files.

## Module Responsibilities

| Module | Unique responsibility | Changes when |
| --- | --- | --- |
| Runtime skill | Define L0-L3 routing, lane ownership, result packets, evidence, and retry limits | Codex workflow policy changes |
| UI metadata | Describe discovery, explicit invocation, and implicit-trigger eligibility | Product-facing naming or trigger wording changes |
| Lifecycle scripts | Install, replace, validate, and uninstall only owned runtime files | Distribution or target layout changes |
| Contract suite | Verify skill invariants, fixtures, privacy boundaries, and lifecycle behavior | A public contract changes |
| Evidence and docs | Explain supported surfaces, limitations, cases, and reproducible results | User guidance or verified runtime evidence changes |
| CI and release | Re-run required Gates and publish a traceable release candidate | Supported matrix or release policy changes |

The modules stay in one repository. Splitting them into services or packages would add
coordination cost without an operational benefit.

## Data Flow And Trust Boundaries

### Authoring and distribution flow

1. A maintainer edits canonical runtime files in the repository.
2. Contract tests and validation reject malformed, non-portable, or sensitive content.
3. The lifecycle script copies the runtime subset into an explicit user, repository,
   or custom target and writes checksums to the ownership manifest.
4. Codex discovers the installed skill and loads metadata before the full body.
5. A user invokes the skill explicitly, or Codex selects it when applicable guidance
   and the skill description match the task.
6. Codex—not this repository—spawns, waits for, and closes subagents.
7. The parent agent validates lane results and reports the final outcome.

### Trust boundaries

| Boundary | Trusted input | Untrusted or external input | Control |
| --- | --- | --- | --- |
| Public repository | Reviewed tracked files | Contributions and downloaded checkout | CI, review, secret/path scan |
| Installer to filesystem | Repository runtime subset and explicit target | Existing target, symlinks, modified files | canonical path checks, dry-run, manifest, checksums, backup |
| Installed skill to Codex | Skill text and UI metadata | Codex version, available roles, task context | documented compatibility and fail-closed lane rules |
| Parent to subagent | Minimal task-local context | Agent output and changed paths | single owner, structured result, parent re-verification |
| Local candidate to GitHub | Accepted release candidate | Remote account, repository settings, public history | manual publication gate and fresh-clone QA |

Secrets, private provider routes, and account configuration never cross into the public
repository or the installed skill package.

## Failure Design And Recovery

| Failure | Required behavior | Recovery |
| --- | --- | --- |
| Target already exists | Exit without mutation unless `--replace` is explicit | Inspect or rerun with `--replace` |
| Target or parent is a symlink escape | Block before copying | Choose a real, explicit target |
| Validation fails in staging | Leave current install unchanged | Fix source and retry |
| Replacement fails after backup | Restore or preserve the timestamped backup and report exact paths | Manual restore command |
| Installed owned file was modified | Uninstall refuses to delete it | Review diff and remove manually if desired |
| Codex does not trigger implicitly | No claim of deterministic auto-triggering | Invoke `$adaptive-subagent-orchestration` explicitly or add the optional AGENTS rule |
| Requested lanes cannot be isolated | Do not parallelize writes | Use L0/SERIAL or a read-only explorer |
| Runtime identity cannot be observed | Do not infer model/provider from local config | Record `UNVERIFIED` |
| CI or fresh-clone Gate fails | Release candidate remains not ready | Fix owning node and rerun invalidated Gates |

## Deployment Units

There are two deployment units:

1. **Source repository**: runtime files, scripts, tests, cases, governance, CI, and
   release records.
2. **Installed skill bundle**: `SKILL.md`, `agents/openai.yaml`, and
   `.install-manifest.json` under one `adaptive-subagent-orchestration` directory.

The source repository is not copied wholesale into a user's skill directory.

## Decisions And Tradeoffs

- Choose a single repository over a plugin for v0.1 because the workflow has no MCP,
  app, or connector dependency. Plugin packaging can be evaluated after adoption.
- Choose Bash lifecycle scripts for the tested macOS/Linux scope and keep runtime
  dependency-free. Windows remains unverified until a native path is implemented and
  tested.
- Choose an explicit ownership manifest over blind recursive copy/delete so updates
  are auditable and uninstall can preserve user changes.
- Keep the public `SKILL.md` in English and provide a full Chinese README rather than
  duplicating runtime instructions in two languages.
- Keep runtime evidence separate from static contract tests. Static PASS never proves
  a provider, model, reasoning effort, or every Codex surface.
- Accept that a natural-language skill cannot guarantee deterministic orchestration;
  gain portability and low operational overhead.

## Parallelism Boundaries

After this architecture and the distribution contract are frozen, the runtime package,
lifecycle tooling, and public documentation can be implemented in parallel if each has
exclusive files. Shared integration files—`ROADMAP.md`, `tests/test_contract.py`, CI,
release readiness, and the final Git state—remain owned by A0.

Publication is strictly sequential after integration QA and the manual release gate.

## Architecture Gate

- [x] Each module has one clear responsibility.
- [x] Every cross-module interface is identified.
- [x] Parallel and hard-dependent work is explicit.
- [x] The architecture diagram HTML has been generated and inspected in headless Chrome.

Gate command after the diagram is added:

```bash
python3 -m unittest tests.test_docs.ArchitectureDocsTests -v
```
