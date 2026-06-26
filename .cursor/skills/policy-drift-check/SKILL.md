---
name: policy-drift-check
description: 校验流程规则/命令/入口技能是否语义一致，防止门禁字段漂移。
---

# Policy Drift Check

## 目标

针对流程规则文档做轻量巡检，确保关键门禁与状态字段在以下文件中一致：

- `.cursor/rules/00-workflow.mdc`
- `.cursor/rules/45-requirement-intake.mdc`
- `.cursor/skills/xijia-ops-pipeline/SKILL.md`
- `.cursor/skills/feature-pipeline/SKILL.md`
- `.cursor/commands/xijia-start.md`

## 同步字段登记表

| 类别 | 必须出现的字段/语义 |
| --- | --- |
| Gate | Gate-0 / Gate-1 / Gate-2 |
| Completeness | `complete|partial|reject` |
| Status 输出 | `Completeness` / `Intake Score` / `Tier` / `Tier Rationale` / `Spike` |
| Probe | `spike-probe` 引用与触发条件 |
| Deferred | `partial/reject` 需入 `docs/requirements/backlog.md` |
| Comment Sync | verify 阶段触达核心业务代码须 `xijia-comment-enhancer`；`Comment Sync` 状态字段 |
| Quality | `quality-judge` 执行与 `pass|revise` 阻断语义 |
| Code Review | verify 阶段 `requesting-code-review` 触发或合法跳过 |
| TDD/Test Gate | 绿黄路径 `test-driven-development` + `backend-test/frontend-test` 触发语义 |

## 巡检步骤（rg）

1. 检查 Gate 与完整性字段：
   - `rg "Gate-0|Gate-1|Gate-2|complete\\|partial\\|reject" .cursor/rules .cursor/skills .cursor/commands`
2. 检查状态模板字段：
   - `rg "Completeness|Intake Score|Tier Rationale|Spike|Comment Sync|Code Review|Quality Judge" .cursor/skills/xijia-ops-pipeline/SKILL.md .cursor/commands/xijia-start.md`
3. 检查 probe 与 Deferred 入池：
   - `rg "spike-probe|backlog\\.md" .cursor/rules .cursor/skills .cursor/commands docs/README.md`
4. 若任一字段缺失，输出 drift 报告并阻断“流程已同步”结论。
5. 检查注释同步门禁：
   - `rg "xijia-comment-enhancer|Comment Sync|44-comment-sync" .cursor/rules .cursor/skills .cursor/commands`
6. 检查质量评审与测试门禁：
   - `rg "quality-judge|requesting-code-review|test-driven-development|backend-test|frontend-test" .cursor/rules .cursor/skills .cursor/commands`

## 何时必须执行

- 修改 `.cursor/rules/*`、`.cursor/skills/*`、`.cursor/commands/*` 任一流程文件后
- 宣告“流程已同步”前
- 若巡检 `verdict=revise`，不得对外宣告流程门禁已完成

## 输出模板

```text
Policy Drift Report:
- checked_files:
  - ...
- missing_or_inconsistent:
  - <field>: <file/path>
- verdict: pass|revise
- required_fixes:
  - ...
```
