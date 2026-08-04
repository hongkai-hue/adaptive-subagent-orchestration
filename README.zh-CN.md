# Adaptive Subagent Orchestration

这个 skill 把中等规模的 Codex 任务路由到最小且有价值的车道集合，为每个可写路径固定一个全程 owner，并要求主线程用证据完成最终 Gate。本仓库是 skill、UI 元数据、生命周期脚本、测试和公开文档的 canonical source；它不是调度器，也不替代 Codex runtime。

**当前支持状态：** v0.1.0 已发布。Public 仓库、GitHub Actions 矩阵、公网 fresh-clone 生命周期 Gate、版本 tag 与 GitHub Release 均已通过验证。标准库契约测试覆盖静态规则、生命周期和若干前向用例；脱敏前向记录覆盖代表性的路由和结果回收。完整的 App／CLI 与操作系统覆盖、隐式触发和请求级 runtime identity 仍是未验证状态，详见 [运行面矩阵](docs/runtime-surface-matrix.md)。

## 它解决什么

| 不使用这个 skill | 使用这个 skill |
| --- | --- |
| 临时决定是否委派。 | 先按 L0-L3 标准选择路由和交接边界。 |
| 多个写入者边改边争 owner。 | 一个可写路径在整个运行中只有一个 owner。 |
| 把 transport 完成当成任务成功。 | 要求结构化结果、changed paths、验证命令、证据和 residual risk。 |
| 候选发生变化后继续沿用旧证据。 | 旧 PASS 失效，重新运行最终 Gate。 |
| 没有新诊断就重复重试。 | 原 owner 在原范围内最多进行一次带具体 Delta 的 focused retry。 |

竞争车道必须有互不重叠的写入范围和独立 Gate，才能进入 L2。共享热点、严格依赖、无法剥离的敏感上下文、迁移或发布工作留在主线程串行处理。跨模块契约、波次、恢复或发布准备工作交给 L3 的 heavy orchestration。

## 路由级别

| 级别 | 适用场景 | agent 数量 | 结果 |
| --- | --- | ---: | --- |
| **L0** | 单个小任务或有序任务没有有价值的独立车道。 | 0 | 主线程执行并运行最终 Gate。 |
| **L1** | 两个独立的只读调查能够明显降低不确定性。 | 1-2 个 `explorer` | 每条车道返回路径、行号、命令输出或明确阻塞。 |
| **L2** | 两个或更多实现车道拥有不相交范围和独立 Gate。 | 1-3 个 `worker`／`default` | 主线程集成、复核 owner 并运行最终 Gate。 |
| **L3** | 工作跨模块、需要冻结契约，或需要波次、恢复、发布准备。 | 本 skill 为 0 | 交给 `orchestrate-heavy-goals`，不要叠加两个 orchestrator。 |

每个 dispatch batch 最多使用 1-3 个 subagent。容量、owner、隐私和依赖检查仍可能把任务降为 `SERIAL` 或 `BLOCKED`。

## 显式调用

在 Codex 任务中直接调用：

```text
Use $adaptive-subagent-orchestration to assess this task, create only worthwhile independent lanes, and integrate verified results.
```

UI 元数据只表示允许隐式触发，不保证 Codex 一定选择这个 skill。推荐显式调用。可以把可选规则手工复制到项目或用户的 `AGENTS.md`，安装脚本不会自动修改这些文件，模板见 [templates/AGENTS-routing.md](templates/AGENTS-routing.md)。

## 安全安装

运行包没有第三方 runtime 依赖，也不会配置或读取 account、provider、model、proxy、API key 或 token。skill discovery 和 subagent 能力由 Codex 提供；脚本只管理两个 runtime 文件和 ownership manifest。

先预览用户级安装：

```bash
./scripts/install.sh --target user --dry-run
```

安装到用户级或当前仓库：

```bash
./scripts/install.sh --target user
./scripts/install.sh --target repo
```

自定义位置必须是绝对路径，最后一级目录必须正好是 `adaptive-subagent-orchestration`：

```bash
./scripts/install.sh --target /absolute/path/adaptive-subagent-orchestration --dry-run
./scripts/install.sh --target /absolute/path/adaptive-subagent-orchestration
```

默认用户目标是 `$HOME/.agents/skills/adaptive-subagent-orchestration`；仓库目标是当前工作目录下的 `.agents/skills/adaptive-subagent-orchestration`。已有目标不会被静默覆盖，检查后再使用 `--replace`：

```bash
./scripts/install.sh --target user --replace
```

替换前会校验现有 manifest，先在 staging 中复制和校验新包，再把旧目录改名为带时间戳的 sibling backup，最后校验新目标。替换失败会保留 backup 并报告路径。manifest 只拥有 `SKILL.md` 与 `agents/openai.yaml`。

校验源目录或已安装目录：

```bash
./scripts/validate.sh .
./scripts/validate.sh "$HOME/.agents/skills/adaptive-subagent-orchestration"
```

卸载支持 dry-run 并采用 fail-closed 行为。只有 manifest 拥有且 checksum 未变化的文件才会删除；owned 文件被修改、manifest 损坏、出现 symlink escape 或发生 lock 冲突时会拒绝删除并保留目标：

```bash
./scripts/uninstall.sh --target user --dry-run
./scripts/uninstall.sh --target user
```

旧的私有安装不会自动迁移。只有明确想操作时才使用自定义绝对路径；不要把目标指向 source checkout。

## 案例

- [独立写入车道](docs/cases/independent-write-lanes.md)：展示不相交 owner 和独立 Gate 的 L2 拆分。
- [共享热点串行](docs/cases/shared-hotspot-serial.md)：展示两个写入者触碰同一文件时为什么留在主线程。

案例是契约示例，不是性能承诺。token 预算、冲突、任务耗时和 runtime 调度取决于宿主和具体任务。

## 支持边界与限制

- **Account／provider／model 中立：** 本仓库不读取、写入或推断这些配置；静态元数据不构成请求级 runtime identity。
- **隐式调用：** `allow_implicit_invocation` 只表示具备资格，Codex 仍可能不触发；可靠路径是显式调用 `$adaptive-subagent-orchestration`。
- **Runtime identity：** 除非脱敏的请求级记录直接证明，否则 exact provider、model、account 和 reasoning identity 都是 `UNVERIFIED`，不能从角色名或本地配置推断。
- **冲突和 token：** skill 可以识别共享 owner、记录 token 或上下文限制，但不能锁定文件、保证 token 可用，也不保证速度、成本或质量提升。
- **Runtime 边界：** subagent 的创建、等待和关闭由 Codex 完成；transport completed 不等于业务 `PASS`，主线程必须检查结构化结果，并在候选变化后重跑 Gate。
- **平台状态：** [运行面矩阵](docs/runtime-surface-matrix.md) 区分静态／前向证据与尚未验证的 App、CLI、OS 覆盖；Windows 不在 v0.1 支持声明内。

## 开发与验证

canonical source 在本仓库。安装后的 runtime bundle 只包含 `SKILL.md`、`agents/openai.yaml` 和 `.install-manifest.json`；测试与文档不会复制到运行目录。

```bash
python3 -m unittest discover -s tests -v
./scripts/validate.sh .
python3 -m compileall -q scripts
git diff --check
```

贡献、漏洞报告和行为规范见 [CONTRIBUTING.md](CONTRIBUTING.md)、[SECURITY.md](SECURITY.md) 与 [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)。项目采用 Apache-2.0，并发布在 `https://github.com/hongkai-hue/adaptive-subagent-orchestration`。

## 目录说明

- [`SKILL.md`](SKILL.md)：英文 runtime 路由契约。
- [`agents/openai.yaml`](agents/openai.yaml)：发现和调用元数据。
- [`scripts/`](scripts/)：安装、校验和卸载入口。
- [`docs/contracts/oss-launch-contract.md`](docs/contracts/oss-launch-contract.md)：v1 生命周期边界。
- [`docs/architecture/oss-launch-architecture.md`](docs/architecture/oss-launch-architecture.md)：模块 owner 和信任边界。
- [`docs/runtime-surface-matrix.md`](docs/runtime-surface-matrix.md)：当前证据和限制。
- [`tests/forward-test-record.md`](tests/forward-test-record.md)：脱敏前向证据记录。
