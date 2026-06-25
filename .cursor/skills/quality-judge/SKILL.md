---
name: quality-judge
description: 独立质量评审门禁（LLM-as-judge），对照 spec/AC/INV 产出 pass|revise。
---

# Quality Judge

## 目标

在实现完成后，由独立评审代理给出 `pass|revise` 判定，避免实现者自评偏差。

## 输入

- change 名称
- proposal/design/tasks/spec
- AC↔Test 追溯表
- DDD 不变量（INV-xxx）

## 评审维度（rubric）

1. AC 覆盖完整性
2. INV-xxx 不变量是否被实现与验证
3. 变更边界是否符合 scope
4. 风险披露是否充分（未执行项/人工验证项）
5. 规范一致性（EARS、术语、BC 边界）

## 输出

```markdown
## Quality Judge Verdict

- Verdict: <pass|revise>
- Reasons:
  - ...
- Required Fixes:
  - ...
- Residual Risks:
  - ...
```

## 约束

- 评审者与实现者角色分离。
- `revise` 状态不得宣告完成。
