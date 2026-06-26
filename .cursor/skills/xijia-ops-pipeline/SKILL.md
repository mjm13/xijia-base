---
name: xijia-ops-pipeline
description: 统一编排需求分级、OpenSpec 工作流、Superpowers 实现方法与归档回灌。用于在复杂需求下按门禁推进，避免漏步骤。
---

# Xijia Ops Pipeline

## 目标

提供统一入口，将项目规则、命令和技能编排成可执行闭环：
- 需求分级（green / yellow / red）
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
2. 先分级，再判型，再路由执行
3. 未归档领域草稿只写 `docs/openspec/changes/<name>/domain/`
4. 仅在归档后通过 `sync-knowledge` 提升到 `docs/domain/*`

## 人审门禁（硬停，不得自动跳过）

- Gate-1（实现前批准）：
  - 完成方案/计划后必须 `stop-and-report`，等待用户明确批准。
  - 未批准前，禁止修改任何非文档代码、迁移、依赖和配置。
- Gate-2（验收签字与状态迁移）：
  - 勾选验收标准、需求状态迁移（如 inbox -> shipped）、change 归档前，必须先获得用户人工验收确认。
  - Agent 只能“提请验收”，不得自行标记完成或自动归档。

## 编排总览

### A. 入口分级（必做）

- green：配置/文档/样式/轻量改动
  - `writing-plans`，按需落 `docs/plans/`
- yellow：单上下文常规功能
  - `writing-plans`，必要时配合 `brainstorming`
- red：核心业务、复杂规则、跨上下文
  - 完整 OpenSpec + Superpowers 链路
- spike：链路不清先探针，代码不作为最终交付

### A.1 green / yellow 路由

0. 读记忆先验：按 `50-context-engineering` 规则 5，读取相关 BC/tags 的未过期 memory 作为先验（无文件则 skip）
1. 分级与判型
2. 出方案与计划（Plan Mode）
3. 触发 Gate-1，等待用户批准
4. 执行实现
5. verify + 文档同步 + 人工验收说明
6. 触发 Gate-2（验收签字后再迁移状态/归档）
7. 提醒用户触发 commit

### B. red 路由

0. 读记忆先验：按 `50-context-engineering` 规则 5，读取相关 BC/tags 的未过期 memory 作为先验（无文件则 skip）
1. explore（`openspec-explore`；business/hybrid 可配 `ddd-modeling`）
2. propose（`openspec-propose`，必须标注 change type）
3. analyze（`openspec-analyze`；blocked 先修 proposal/design/tasks/spec）
4. 触发 Gate-1，等待用户批准再进入实现
5. apply（`openspec-superpowers-apply`）
6. verify（强制 `verification-before-completion`）
7. sync（`openspec-sync-specs`）
8. 触发 Gate-2（验收签字后方可 archive）
9. archive（`openspec-archive-change`）
10. sync-knowledge（`sync-knowledge`）

### C. 放弃路径

用户决定中止时：
- 调用 `abandon-change`
- 丢弃 change 草稿，不污染 `docs/domain`

## Approval Gates（命中即暂停并请求确认）

- 破坏性数据库变更
- 新增关键外部依赖
- 删除或下线已上线能力
- 权限、密钥、安全策略变更
- 跨限界上下文大规模架构调整

## 每阶段输出模板

```markdown
## Xijia Pipeline Status

- Tier: <green|yellow|red>
- Change Type: <business|technical|hybrid>
- Stage: <explore|propose|analyze|apply|verify|sync|archive|sync-knowledge|abandon>
- Memory Prior: <已读条目数 / none / skip>
- Done: <what completed>
- Next: <next command/skill>
- Blockers: <none or list>
```

## 完成判定（闭环定义）

仅当满足以下全部条件，才可声明当前需求完成：

1. 任务实现与验证通过（有命令证据）
2. In Scope 的 AC 有对应验证（Deferred 除外）
3. 规格同步已完成（或明确说明跳过原因）
4. 已写入人工验收说明（可复现）
5. Gate-2 已完成（用户验收签字）
6. commit 状态已明确（已提交，或“待用户触发 commit”）

## 建议调用方式

- 显式调用：`使用 xijia-ops-pipeline 推进这个需求`
- red 档建议从“分级 + 判型 + explore”起步

## 自治护栏（预算与恢复）

- 命中长链自治任务时，启用 `51-autonomy-guards.mdc`
- 恢复点以 `tasks.md` 勾选与 openspec status 为准
