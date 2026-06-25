---
name: openspec-analyze
description: 在实现前做 OpenSpec 产物一致性闸门检查（AC↔tasks↔spec↔test）。
---

# OpenSpec Analyze

## 目标

在 `propose -> apply` 之间执行一次一致性检查，避免“有 spec 无任务”或“有任务无验收/测试”。

## 检查范围

对当前 change 的以下文件建立追溯表：

- `proposal.md`：`In Scope` / `Out of Scope` / `Open Questions & Deferred`
- `design.md`：关键约束与技术方案
- `tasks.md`：可执行任务清单
- `specs/**/spec.md`：Requirement / Acceptance Criteria

## 必查项

1. 每条 `In Scope` AC 都能映射到至少一条任务（`tasks.md`）。
2. 每条 `In Scope` AC 都能在 delta `spec.md` 找到对应 Requirement/AC。
3. 每条 `In Scope` AC 都有验证路径（自动化测试或可执行检查）。
4. 标记为 `Deferred`/`Out of Scope` 的项不得混入当前任务完成判定。
5. 若发现冲突（spec 与 design/tasks 不一致），先修产物再实现。

## 输出格式

```markdown
## OpenSpec Analyze

- Change: <name>
- Verdict: <ready | blocked>
- Coverage:
  - In-Scope AC: <N>
  - Mapped to tasks: <N/N>
  - Mapped to specs: <N/N>
  - Mapped to tests/checks: <N/N>
- Blocking Gaps:
  - AC-xxx -> missing in tasks/spec/test ...
- Next:
  - ready: use `openspec-superpowers-apply`
  - blocked: update artifacts then re-run `/opsx:analyze`
```
