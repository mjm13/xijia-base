---
name: openspec-superpowers-apply
description: OpenSpec apply 与 Superpowers 强制联动实现入口（含 quality-judge 门禁）。
---

# OpenSpec + Superpowers Apply

将 OpenSpec 的任务编排与 Superpowers 的实现方法绑定为单一入口。

## 强制技能链

1. `openspec-apply-change`
2. `test-driven-development`
3. `systematic-debugging`（失败时）
4. `verification-before-completion`
5. `requesting-code-review`
6. `quality-judge`（新增，最终门禁）

## 执行步骤（简版）

1. 读取 change 上下文（proposal/design/tasks/spec）。
2. 建立 AC↔Test 追溯表；In-Scope AC 必须映射测试。
3. 按任务循环：TDD -> 实现 -> 验证 -> 勾选。
4. 全任务完成后执行：
   - code-review
   - quality-judge（输出 `pass|revise`）
   - 人工验收说明
   - sync -> archive -> sync-knowledge
5. commit 由用户触发；未 commit 不得进入下一需求。

## 质量门禁

- `quality-judge = revise` 时，必须回到任务修正，禁止宣告完成。
- 仅当 judge 为 `pass` 且验证证据完整，才能进入收尾。
