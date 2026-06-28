---
name: feature-pipeline
description: 端到端功能研发编排入口（DDD + OpenSpec + Superpowers）。当用户用自然语言提出「我要做 X / 帮我实现 X / 推进这个需求 / 不要漏步骤跑完整流程」时自动进入；本技能是模型可自动发现的入口，规范内容委托 xijia-ops-pipeline。
---

# Feature Pipeline（入口别名）

本技能是**模型可自动发现**的端到端编排入口。为避免双份编排漂移，**规范内容只维护在 `xijia-ops-pipeline`**（与 `/xijia:start` 命令共用同一真相源）。

## 怎么用

1. 立即加载并严格遵循 `xijia-ops-pipeline` 的完整编排（入口分级 → 判型 → 路由 → 收尾闭环、Approval Gates、完成判定、输出模板）。
2. 行为与 `/xijia:start` 一致；区别仅在触发方式：
   - `/xijia:start`：用户手动命令触发
   - `feature-pipeline`：模型按自然语言意图自动触发
3. 一切门禁、分级/判型规则、闭环定义以 `xijia-ops-pipeline` 与 `.cursor/rules/00-workflow.mdc` 为准；本文件不再单独维护步骤细节，防止漂移。

## 一句话流程（速记，细节看 xijia-ops-pipeline）

`Gate-0(需求完整性: complete|partial|reject) → 分级(🟢🟡🔴，链路不清先调用 spike-probe) → 判型(业务/技术/混合) → Gate-1(实现前必须 STOP 待用户批准) → 🔴: explore → propose → analyze → openspec-superpowers-apply(写代码即同步 xijia-comment-enhancer 注释) → verify(comment-sync guard 兜底 / requesting-code-review / quality-judge) → sync → archive → sync-knowledge；🟢🟡: Plan Mode 出方案→人审→执行(TDD + backend/frontend test + 写代码即同步注释)→verify(comment-sync guard + quality-judge)；收尾 Gate-2(人工验收签字后方可状态迁移/归档)`

> 注释同步在**写代码阶段**完成（新增即写、修改即更新），verify 仅用 `pipeline_guard.py --check-comment-sync` 兜底，详见 `44-comment-sync.mdc`。

> 实现阶段唯一入口：`openspec-superpowers-apply`（禁止裸跑 `openspec-apply-change`）。
>
> **两条默认姿态**：① 迭代切片——一个 change = 一条端到端薄切片（非整模块），proposal 必含 `In Scope / Out of Scope / Open Questions & Deferred`；② 任何档位收尾必须输出「人工验收说明」（改了哪个菜单/模块、什么功能、什么场景、怎么手动点验），且未经用户签字不得迁移状态或归档。
