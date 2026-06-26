---
name: sync-knowledge
description: 归档后知识回灌（spec/change -> docs/domain + ADR + capability map + memory）
---

# 目标

在 change 归档后，把稳定知识回灌到长期文档，并完成契约一致性与文档卫生检查。

# 执行步骤

1. 读取归档 change 的 design/tasks/specs。
2. 判定 change type，业务/混合语义从 `docs/openspec/changes/<name>/domain/*` 提升到 `docs/domain/*`。
3. 运行 DDD 契约校验：
   - `python .cursor/skills/ddd-modeling/scripts/validate_domain_contracts.py --path "docs/domain"`
4. 执行沉淀三问（规则/决策/数据语义）并更新去向（domain/ADR/data-dictionary）。
5. 更新 `docs/capability-map.md` 与 `AGENTS.md`（命中触发条件时）。
6. 轻量代码↔文档漂移检查（delta spec vs domain/capability-map）。
7. checkpoint 写回 episodic memory（xijia-memory；若 `docs/memory/` 缺失则先 ensure scaffold，见 xijia-memory）。
   - 7a. 蒸馏提议：扫描 `confidence >= 0.8` 且语义稳定的 memory 条目，**提议**蒸馏到 ADR/`docs/domain`（人确认后执行，不自动改长期真相源）。
   - 7b. 剪枝归档：运行 `python .cursor/skills/xijia-memory/scripts/memory_prune.py`，将过期条目移到 `docs/memory/decisions.archive.jsonl` 并报告归档数（无文件则 SKIP）。
8. 运行 docs 卫生评分：
   - `python .cursor/skills/xijia-docs-score/scripts/score_docs.py`
9. 需求状态迁移到 shipped 并修复引用路径。
10. 提醒：commit 由用户触发，未 commit 不得进入下一需求。

# 约束

- 未归档内容不得写入 `docs/domain/*`
- 回灌优先增量，不整页重写

