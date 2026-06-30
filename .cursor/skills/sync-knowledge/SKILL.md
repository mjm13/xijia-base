---
name: sync-knowledge
description: 全档位知识回灌（spec/change -> docs/domain + ADR + capability map）
---

# 目标

将本次需求的稳定结论回灌到长期文档，并由 `tier` 决定具体沉淀范围。所有档位（green/yellow/red）收尾都要执行本技能。回灌必须支持动态更新（update/supersede/rename），禁止无异议累加。

# 输入

- `tier`: `green | green-trivial | yellow | red`
- 对应需求文档路径（`docs/requirements/**`）
- （red）对应 change 名称（`docs/openspec/changes/<name>/`）

# 按 tier 执行范围

| 步骤 | green/green-trivial/yellow | red |
|---|---|---|
| 读取 change 产物（design/tasks/specs） | 跳过 | 执行 |
| domain 语义提升到 `docs/domain/*` | 跳过 | 执行 |
| DDD 契约校验 | 跳过 | 执行 |
| 沉淀四问 -> ADR / data-dictionary / requirement / 语言边界 | 执行 | 执行 |
| 更新 `docs/capability-map.md` / `AGENTS.md` | 按需 | 按需 |
| docs 卫生评分 | 执行 | 执行 |
| 需求状态迁移到 shipped | 执行 | 执行 |
| commit 提醒 | 执行 | 执行 |

# 执行步骤

1. 读取需求文档，确认本次变更结论与验收记录。
2. 先校验 requirement「分级与判型」中的 Gate-0/1/2 审批记录是否可追溯（状态/审批人/日期）；缺失先补齐再继续。
3. 从 requirement「实现记录」提取本次“复用过的经验文档”清单（`docs/pitfalls/*.md`、`docs/patterns/*.md`）；若为空则记 `Experience Reuse: none`。
4. 在收尾回顾中提炼本次新增经验：
   - 可复用做法写入 `docs/patterns/*.md`
   - 本次踩坑与规避写入 `docs/pitfalls/*.md`
   - 采用“AI 提议 + 人工确认”模式，未确认不得作为稳定经验沉淀。
5. 若 `tier=red`：读取归档 change 的 design/tasks/specs。
6. 若 `tier=red` 且 change type 为 business/hybrid：将 `docs/openspec/changes/<name>/domain/*` 提升到 `docs/domain/*`。
7. 若 `tier=red`：运行 DDD 契约校验：
   - `python .cursor/skills/ddd-modeling/scripts/validate_domain_contracts.py --path "docs/domain"`
8. 执行动态合并协议（先 diff 再写）：
   - 判定口径必须复用 `ddd-modeling` 中“专业 DDD 判定提示词”（严格版/轻量版），不得临时改写分类标准。
   - 读取 `docs/domain/*` 现状与 change 草稿逐条对比。
   - 每个术语/聚合/INV/关系先分类：`ADD | UPDATE | SUPERSEDE | RENAME | DEPRECATE`。
   - `UPDATE`：就地更新定义，并追加「修订记录：日期 + change-id」。
   - `SUPERSEDE`：旧 INV 标注被新 INV 替代，不静默删除。
   - `RENAME`：旧名进入 `Aliases to AVOID`，避免后续漂移。
   - 防累加：写入前按锚点/别名查重；已存在概念必须走 `UPDATE/SUPERSEDE/RENAME`。
9. 冲突停审（强制）：
   - 同词异义、术语重定义、BC 边界不一致时必须 stop-and-report，列待确认清单，用户确认后再写入。
10. 执行沉淀四问并落目标文档：
   - 规则/不变量 -> `domain-model.md`（INV，ADD/SUPERSEDE）
   - 关键决策/权衡 -> `docs/decisions/*.md`
   - 数据语义（字段/枚举/状态）-> `data-dictionary.md`
   - 语言/边界变化（新术语、新 BC、同词异义）-> `ubiquitous-language.md` + `context-map.md`
11. BC 注册表比对：
   - 以 `context-map.md` 的 Bounded Context 列表判定“新建 vs 更新”；
   - 若不存在则按本次迭代增量创建（仅写本次涉及 BC，不回填历史）。
12. green/yellow 路由补充：
   - 命中 C 类（仅字段语义）时，允许只更新 `docs/domain/data-dictionary.md`，同样遵循动态合并协议 + 人工确认。
13. ADR 强制触点：若命中任一 Approval Gate 类权衡（新增关键外部依赖、权限/安全策略变更、跨上下文架构权衡），必须新增 `docs/decisions/*.md` 后才能宣告收尾完成（由 `pipeline_guard.py --check-release --req <requirement-file>` 机器兜底）。
14. 按需更新 `docs/capability-map.md` 与 `AGENTS.md`（命中其一即更新）：
   - dev/build/test/deploy 命令新增或变更；
   - 顶层目录/模块职责或关键入口发生变化；
   - 新增关键外部依赖或技术栈版本变化；
   - 安全边界变化（密钥策略、禁改目录、高风险操作门禁）；
   - 提交/PR 约定变化。
   - drift 防护：`AGENTS.md` 不得引用已删除脚本/命令；收尾时必须逐条核对并修正失效引用。
15. 执行轻量代码↔文档漂移检查（delta spec vs domain/capability-map）；若 guard 给出 drift 提醒，需在验收记录写处置结论。
16. 对第 3 步识别出的每篇“复用过的经验文档”追加判定事件（一篇一条）：
   - `python .cursor/skills/xijia-docs-score/scripts/score_docs.py --judge-doc <doc-path> --judge-session <chat-or-requirement-id> --judge-verdict useful|neutral|misleading --judge-reason "<reason>"`
17. 运行 docs 卫生评分：
   - `python .cursor/skills/xijia-docs-score/scripts/score_docs.py`
18. 迁移需求状态到 shipped 并修复引用路径（仅在 Gate-2 已签字后执行）。
19. 提醒：commit 由用户触发，未 commit 不得进入下一需求。

# 约束

- 所有档位都必须执行 `sync-knowledge`。
- 未归档内容不得写入 `docs/domain/*`（仅 red 且已归档可提升）。
- 回灌优先增量，不整页重写。
- AI 只可提议定义，不得在无人确认下铸造新术语/BC/INV 最终语义。

