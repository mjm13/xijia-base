---
name: openspec-analyze
description: 在实现前做 OpenSpec 一致性闸门（AC↔tasks↔spec↔test↔DDD契约）。
---

# OpenSpec Analyze

## 必查项

1. In-Scope AC ↔ tasks 映射完整。
2. In-Scope AC ↔ delta spec 映射完整。
3. In-Scope AC ↔ tests/checks 映射完整。
4. DDD 契约完整：
   - UL 含 BC + Aliases to AVOID
   - domain-model 含 `INV-xxx`
   - context-map 含关系 Pattern
5. `Deferred/Out of Scope` 不进入完成判定。
6. 关键未知是否已闭环：
   - 若存在数据来源不明、原型差异未确认、核心交互未定义，必须有 spike 报告支撑。
   - 无 spike 证据时，判定为 `blocked`。

## 校验命令

- `python .cursor/skills/ddd-modeling/scripts/validate_domain_contracts.py --path "<change-domain-dir>"`

## Verdict

- `ready`: 所有映射与契约校验通过
- `blocked`: 任一缺口未闭合（含关键未知未被 spike 证据消解）
