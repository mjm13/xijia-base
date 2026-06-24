---
name: xijia-ops-pipeline
description: 统一编排需求分级、OpenSpec 工作流、Superpowers 实现方法和归档回灌。用于用户希望一键推进端到端研发、减少漏步骤、强制闭环时。
disable-model-invocation: true
---

# Xijia Ops Pipeline

## 目标

提供一个统一入口，将本项目的规则、命令与技能串成可执行闭环：

- 需求分级（green/yellow/red）
- change 类型判定（business/technical/hybrid）
- OpenSpec 产物与实现
- Superpowers 的 TDD/调试/验证/评审
- 归档与知识回灌（change 草稿 -> docs/domain）

## 何时使用

当用户表达以下意图时使用：

- “完整推进这个需求”
- “按项目标准从需求做到归档”
- “不要漏步骤，帮我跑完整流程”
- “xijia 流程来一遍”

## 输入

- 需求描述（必填）
- 可选 change 名称（kebab-case）
- 可选复杂度偏好（默认自动分级）

## 固定约束

1. 严格遵守 `.cursor/rules/00-workflow.mdc`
2. 先分级再选流程（green/yellow/red）
3. 先判 change type 再 propose（business/technical/hybrid）
4. 未归档领域草稿只写 `docs/openspec/changes/<name>/domain/`
5. 仅在归档后通过 `sync-knowledge` 提升到 `docs/domain/*`

## 编排总览

### A. 入口分级（必须）

先按复杂度分档：

- **green**：配置/文案/样式/简单独立改动  
  -> 调用 `writing-plans`，计划可落 `docs/plans/`，通常不进 OpenSpec
- **yellow**：单上下文常规功能  
  -> `writing-plans` + 可选 `brainstorming`，必要时再升 red
- **red**：核心业务、复杂规则、跨上下文  
  -> 进入完整 OpenSpec + Superpowers 流程（B 段）
- **🧪 spike（探针，正交于复杂度）**：链路严重不清/可行性未知时先探路  
  -> 走 green 的轻量节奏，发现落 `docs/plans/<spike-name>.md`；spike 代码不得当成果交付，产出喂正式 change 重做

如果拿不准：先低档，复杂度上升再升级。

**迭代切片（默认姿态）**：需求无法一次描述完时，一个 change = 一条端到端薄切片（非整模块），命名切片化；proposal 必含 `In Scope / Out of Scope / Open Questions & Deferred` 三段，想不清的链路显式 park。

### B. Red 档完整链路

1. **探索**
   - 调用 `openspec-explore`
   - 若为 business/hybrid：调用 `ddd-modeling`，写 `docs/openspec/changes/<name>/domain/`

2. **提案**
   - 调用 `openspec-propose`（或 `/opsx:propose`）
   - 强制写入 change type：`business|technical|hybrid`

3. **实现**
   - 必须调用 `openspec-superpowers-apply`
   - 实现期强制技能链：
     - `test-driven-development`
     - `systematic-debugging`（失败时）
     - `verification-before-completion`
     - `requesting-code-review`

4. **规格同步**
   - 调用 `openspec-sync-specs`（或 `/opsx:sync`）

5. **归档**
   - 调用 `openspec-archive-change`（或 `/opsx:archive`）

6. **知识回灌**
   - 调用 `sync-knowledge`
   - 将已落地内容从 change 草稿 `docs/openspec/changes/<name>/domain/*` 提升到 `docs/domain/*`

### C. 放弃路径

当用户决定中止：

- 调用 `abandon-change`
- 丢弃 change 草稿（随 change 一并放弃，`docs/domain` 不受影响）
- 不执行 sync

## Approval Gates（命中即暂停）

出现以下任一项必须请求用户确认：

- 破坏性数据库变更
- 新增关键外部依赖
- 删除/下线已上线能力
- 权限、密钥、安全策略变更
- 跨限界上下文大调整

## 每阶段输出模板

```markdown
## Xijia Pipeline Status

- Tier: <green|yellow|red>
- Change Type: <business|technical|hybrid>
- Stage: <explore|propose|apply|verify|sync|archive|sync-knowledge|abandon>
- Done: <what completed>
- Next: <next command/skill>
- Blockers: <none or list>
```

## 完成判定（闭环定义）

仅当满足以下**全部**条件才可宣告**当前需求**完成，并进入下一需求：

1. 任务实现与验证通过（有命令证据）
2. 本切片 In Scope 的 AC 均有通过测试（`Deferred` AC 除外）
3. specs 已同步（或明确确认跳过并说明原因）
4. change 已归档
5. `sync-knowledge` 已执行（🔴）；🟢/🟡 等价文档已更新
6. `docs/domain` 与 change 草稿状态一致，无悬挂条目
7. **已写入「人工验收说明」**：追加到需求文件 `# 验收记录` 段（🟢/🟡 只有计划文档时追加到 `docs/plans/`），并在摘要复述
8. **git commit 已成功**：本需求相关代码与已同步文档均已提交；**以 commit 为最终操作**

> 🟢/🟡 不走 OpenSpec，但第 7–8 条同样必须满足。

**进入下一需求前**：运行 `git status`，不得存在上一需求的未提交改动；若有，先完成 commit 再继续。

## 建议调用方式

- 显式调用：`使用 xijia-ops-pipeline 推进这个需求`
- 对 red 档：优先从“分级 + 判型 + explore”开始，不直接写代码

