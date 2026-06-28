---
name: xijia-ops-pipeline
description: 统一编排需求分级、OpenSpec 工作流、Superpowers 实现方法与归档回灌。用于在复杂需求下按门禁推进，避免漏步骤。
---

# Xijia Ops Pipeline

## 目标

提供统一入口，将项目规则、命令和技能编排成可执行闭环：
- 需求分级（green / green-trivial / yellow / red）
- change 类型判定（business / technical / hybrid）
- OpenSpec 产物与实现
- Superpowers 的 TDD / 调试 / 验证 / 评审
- 归档与知识回灌（change 草稿 -> docs/domain）

## 何时使用

当用户表达以下意图时使用：
- 完整推进一个需求
- 按项目标准从需求做到归档
- 希望端到端流程不漏步骤

## 输入

- 需求描述（必填）
- 可选 change 名称（kebab-case）
- 可选复杂度偏好（默认自动分级）

## 固定约束

1. 严格遵守 `.cursor/rules/00-workflow.mdc`
2. 先执行 Gate-0 完整性闸门（`complete|partial|reject`），再分级、判型、路由执行
3. 未归档领域草稿只写 `docs/openspec/changes/<name>/domain/`
4. 仅在归档后通过 `sync-knowledge` 提升到 `docs/domain/*`
5. DDD 动态更新提醒：`business/hybrid` 需求进入知识回灌前，必须先做 A/B/C/D 影响分类并按 `ADD/UPDATE/SUPERSEDE/RENAME/DEPRECATE` 执行；禁止“只追加不更新”

## 人审门禁（硬停，不得自动跳过）

- Gate-0（需求完整性闸门）：
  - 分级前必须给出 `verdict: complete|partial|reject`。
  - `partial` 只能实现可落地部分，其他必须写入 Deferred 并先获用户确认。
  - `reject` 必须 stop-and-report，列缺失清单等待用户补充。
- Gate-1（实现前批准）：
  - 完成方案/计划后必须 `stop-and-report`，等待用户明确批准。
  - 未批准前，禁止修改任何非文档代码、迁移、依赖和配置。
- Gate-2（验收签字与状态迁移）：
  - 勾选验收标准、需求状态迁移（如 inbox -> shipped）、change 归档前，必须先获得用户人工验收确认。
  - Agent 只能“提请验收”，不得自行标记完成或自动归档。
  - 若本需求存在 Deferred，必须先同步写入 `docs/requirements/backlog.md`。
  - 提请验收前必须生成“Gate-2 验收检查单”（按 AC 列步骤与预期结果）。

## 编排总览

### A.0 Gate-0 完整性闸门（必做）

- 输出 `verdict: complete|partial|reject`
- 输出 `Intake Score: 0-100`（四维评分：数据流闭环/原型对齐/验收可测/范围边界）
- 输出“数据流闭环表”（来源 → 加工 → 去向，每个 In-Scope 能力一行）；任一段空/占位/`[待确认]` 即未闭环
- `green-trivial`（纯配置/样式/文档/锁文件）可在需求文档显式声明 `本需求无数据流（green-trivial）`，跳过逐能力闭环表
- 数据流闭环门禁：存在未闭环能力时 `verdict` 不得为 `complete`，仅纳入已闭环能力或 `reject`
- 二次确认回环：缺口补充后必须**重建并复核**闭环表，用户对最终闭环表终认后才可进入分级（不得一次放行）
- 机器校验：`python .cursor/hooks/pipeline_guard.py --check-intake --req docs/requirements/inbox/<file>.md`（非零=有断点）
- `green-trivial` 机器校验：`python .cursor/hooks/pipeline_guard.py --check-intake --tier green-trivial --req docs/requirements/inbox/<file>.md`
- 如有原型，输出“需求↔原型差异表”并标记 `[待人工确认]`
- 输出“未描述细节清单”并标记 `[假设]`
- 若 `verdict=partial|reject` 且关键链路不清，必须先进入 `spike-probe`，禁止直接进入实现

### A. 入口分级（必做）

#### Tier Decision Matrix（用于生成 Tier Rationale）

在给出 Tier 前，先按下表记录命中情况、证据与置信度：

| red 触发器 | 命中(yes/no) | 证据 | 置信度(high/med/low) |
|---|---|---|---|
| 核心业务领域变更 | ... | ... | ... |
| 复杂规则/状态机/不变量 | ... | ... | ... |
| 跨限界上下文改造 | ... | ... | ... |

分级规则：

- 任一触发器 `yes + high`：直接升 `red`
- 多个触发器 `yes + med`：优先升 `red`，无法判定则先 `spike`
- 全部 `no` 或低置信：按 `green/yellow` 继续

- green：配置/文档/样式/轻量改动
  - `writing-plans`，方案直接写进 requirement 文档的「实现方案」章节（不建 `docs/plans/`）
- green-trivial：纯配置/样式/文档/锁文件，且不触达核心业务前缀、不命中 Approval Gates
  - requirement 文档必须写 `本需求无数据流（green-trivial）`
  - 保留 Gate-1/Gate-2 人审，收尾仍执行 `sync-knowledge`（轻量）
- yellow：单上下文常规功能
  - `writing-plans`，必要时配合 `brainstorming`；方案落 requirement 文档「实现方案」章节
- red：核心业务、复杂规则、跨上下文
  - 完整 OpenSpec + Superpowers 链路
- spike：链路不清先探针，代码不作为最终交付
  - 必须调用 `spike-probe` 产出探针报告（假设/实验/证据/结论/下一步）

### A.1 green / green-trivial / yellow 路由

1. 分级与判型（写入 requirement 文档「分级与判型」章节）
2. 出方案（Plan Mode）；写入 requirement 文档「实现方案」章节，不另建 `docs/plans/`
3. 触发 Gate-1，等待用户批准
4. 按触达栈建立测试约束（`backend-test` / `frontend-test`）并保持 TDD（`test-driven-development`）
5. 执行实现：新增/修改核心业务代码时，同步执行 comment-sync（见 E.0），不得留到 verify
6. verify（执行 E 子流程：verification/comment-sync guard/code-review/quality-judge）+ 文档同步 + 人工验收说明
   - 若命中 DDD C 类（仅字段语义），在 `sync-knowledge` 阶段更新 `docs/domain/data-dictionary.md`（动态合并，不是追加流水账）
7. 触发 Gate-2（验收签字后再迁移状态/归档）
8. sync-knowledge（`sync-knowledge`，`tier=green|green-trivial|yellow`）
9. 提醒用户触发 commit

### B. red 路由

1. explore（`openspec-explore`；business/hybrid 可配 `ddd-modeling`）
2. propose（`openspec-propose`，必须标注 change type）
3. analyze（`openspec-analyze`；blocked 先修 proposal/design/tasks/spec）
4. 触发 Gate-1，等待用户批准再进入实现
5. apply（`openspec-superpowers-apply`）：新增/修改核心业务代码时，同步执行 comment-sync（见 E.0），不得留到 verify
6. verify（执行 E 子流程；🔴 默认强制 `requesting-code-review` + `quality-judge`）
7. sync（`openspec-sync-specs`）
8. 触发 Gate-2（验收签字后方可 archive）
9. archive（`openspec-archive-change`）
10. sync-knowledge（`sync-knowledge`，`tier=red`）

### C. 放弃路径

用户决定中止时：
- 调用 `abandon-change`
- 丢弃 change 草稿，不污染 `docs/domain`

### D. spike 路由（链路不清）

1. 调用 `spike-probe` 执行时间盒探针（默认 0.5-1 天）
2. 输出探针报告：
   - 目标问题
   - 假设清单
   - 最小实验与证据
   - 结论（成立/不成立/部分成立）
   - 推荐去向（green/yellow/red/reject）
3. 向用户 stop-and-report，请用户确认：
   - 仅做可落地部分（partial）
   - 继续补充信息后重跑 Gate-0
   - 直接 reject 当前需求
4. 未经用户确认，不得从 spike 直接进入实现
5. 对探针结论中的 Deferred，落 `docs/requirements/backlog.md`

### E.0 apply-time comment-sync（写代码阶段必做）

1. 每次准备编辑核心业务文件前，先判定触发范围（API 端点 / Service / 业务处理单元 / 跨模块编排 / 核心业务模型）。
2. 触发时必须调用 `xijia-comment-enhancer`，并在同一次实现改动中完成：
   - 新增代码：按内部层/端点层/模型层补齐语义注释
   - 修改代码：同步更新对应语义注释，逻辑变更追加 `[修改记录]`
3. afterEdit guard 若提示核心业务文件缺语义标签，下一步必须优先补该文件注释；不得把补注释推迟到 verify。

### E. verify 子流程（测试 + guard 兜底，必做）

1. 运行 `verification-before-completion`（测试/构建/AC 证据）。
2. 运行 `python .cursor/hooks/pipeline_guard.py --check-comment-sync`，客观确认 apply-time comment-sync 未漏。
3. 若 guard 失败：回到 E.0 补齐注释，或按 `44-comment-sync.mdc` 白名单逐条说明并经用户确认；不得进入 Gate-2。
4. 若未触达核心业务代码：在 verify 输出中声明 `Comment Sync: skipped — <白名单原因> — guard: pass`。
5. 代码评审：
   - 🔴：强制调用 `requesting-code-review`
   - 🟢/🟡：命中任一条件则调用 `requesting-code-review`（跨模块改动 / 新增 API 端点 / 权限与安全策略改动 / 影响面较大）
   - 未命中条件可跳过，但必须在输出中声明 `Code Review: skipped — <原因>`
6. 执行 `quality-judge` 并输出 `pass|revise`。
7. 进入 Gate-2 前运行收尾聚合自检：`python .cursor/hooks/pipeline_guard.py --check-release --req docs/requirements/inbox/<file>.md`（聚合 comment-sync + 后端测试存在性 + 审批记录 + ADR 命中校验 + 人工门禁提醒）；客观项 exit≠0 即 blocked。
8. 任一条件命中则 **blocked**，不得进入 Gate-2：
   - 注释未完成且属于触达范围
  - `--check-release` 客观项 exit≠0（comment-sync 缺失 / 后端业务改动无测试且无豁免说明 / Gate-0&1 留痕缺失 / ADR 命中未落档）
   - `quality-judge = revise`

## 阶段进入前置校验（机器可校验，必做）

防止「会话摘要 / 抢跑跳过前序阶段」。进入下列阶段前，必须以**文件系统证据**校验前序产物存在，不得仅凭自述 `Stage` 判断：

- 🔴 进入 apply 前，必须确认 `docs/openspec/changes/<name>/` 同时存在：
  - `proposal.md`（含 In Scope / Out of Scope / Open Questions & Deferred）
  - `tasks.md`
  - `specs/**/*.md`（delta spec）
  - `business|hybrid` 还需 `domain/*.md`（`ddd-modeling` 产物）
- 硬校验命令（缺失即非零退出，必须回退补齐）：
  - `python .cursor/hooks/pipeline_guard.py --check-apply --change <name> --tier red`
- 任一核心产物缺失：视为 explore/propose/analyze 未完成，**禁止开始修改实现代码**，回退补齐后再 apply。
- 🟢/🟡 进入实现前，确认对应 requirement 文档已填「分级与判型」「实现方案」章节且已过 Gate-1。
- 注意：🔴 需求的实现方案以 OpenSpec change 产物为准，不写进 requirement「实现方案」章节（分档路由见 `docs/README.md`）。

## 会话恢复自检清单（摘要 / 续聊必做）

长会话被摘要或跨会话续聊时，**不得信任摘要里的 `Stage` 自述**，必须用证据重建阶段状态：

1. 读取当前需求文档（`docs/requirements/inbox/*.md`）确认 tier 与 change type。
2. 运行 `python .cursor/hooks/pipeline_guard.py --audit`，核对：
   - 🔴 是否存在对应 `docs/openspec/changes/<name>/` 产物
   - `tasks.md` 勾选进度
   - 是否存在对应测试文件
3. 若文件证据与摘要 `Stage` 不一致，**以文件证据为准**，回退到最早未完成阶段补齐。
4. verify 三件套（`xijia-comment-enhancer` / `requesting-code-review` / `quality-judge`）若无产出记录，一律视为未完成，不得据摘要宣称已做。

## Approval Gates（命中即暂停并请求确认）

- 破坏性数据库变更
- 新增关键外部依赖
- 删除或下线已上线能力
- 权限、密钥、安全策略变更
- 跨限界上下文大规模架构调整

## 每阶段输出模板

```markdown
## Xijia Pipeline Status

- Completeness: <complete|partial|reject>
- Intake Score: <0-100>
- Tier: <green|yellow|red>
- Tier Rationale: <red 触发器命中/未命中说明>
- Change Type: <business|technical|hybrid>
- Stage: <explore|propose|analyze|apply|verify|sync|archive|sync-knowledge|abandon>
- Spike: <not-needed|running|done>
- Comment Sync: <done + files|skipped + reason|blocked>
- Code Review: <done|skipped + reason|blocked>
- Quality Judge: <pass|revise|pending>
- Done: <what completed>
- Next: <next command/skill>
- Blockers: <none or list>
```

## 完成判定（闭环定义）

仅当满足以下全部条件，才可声明当前需求完成：

1. 任务实现与验证通过（有命令证据）
2. 核心业务代码注释同步已完成，或已在 verify 输出中说明合法跳过原因
3. `quality-judge = pass`（`revise` 必须回修后重跑 verify）
4. In Scope 的 AC 有对应验证（Deferred 除外）
5. 规格同步已完成（或明确说明跳过原因）
6. 已写入人工验收说明（可复现）
7. Gate-2 已完成（用户验收签字）
8. commit 状态已明确（已提交，或“待用户触发 commit”）

## 可选增强触发器（按需启用）

- `using-git-worktrees`：满足任一条件建议启用
  - 🔴 需求且预计实现周期 > 1 天
  - 并行推进 2 个及以上需求/分支
  - 需要在不污染当前工作区的前提下试错
- `review-security`：满足任一条件建议启用
  - 权限模型、鉴权链路、密钥/安全策略改动
  - 新增关键外部依赖或外部 API 凭据接入
  - 破坏性数据库变更（删表/删列/改类型/回填）

## 建议调用方式

- 显式调用：`使用 xijia-ops-pipeline 推进这个需求`
- red 档建议从“分级 + 判型 + explore”起步

## 自治护栏（预算与恢复）

- 命中长链自治任务时，启用 `51-autonomy-guards.mdc`
- 恢复点以 `tasks.md` 勾选与 openspec status 为准
