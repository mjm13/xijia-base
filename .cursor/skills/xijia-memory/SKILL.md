---
name: xijia-memory
description: 结构化写回研发记忆（episodic），在 checkpoint 记录决策/结果/置信度/时效。
---

# xijia-memory

## 目标

把跨会话可复用的决策沉淀为结构化记忆，避免重复踩坑。

## 存储

- `docs/memory/decisions.jsonl`

## 记录结构

```json
{"ts":"...","source":"...","decision":"...","result":"...","confidence":0.0,"staleness":"30d","tags":["domain","contract"]}
```

## 规则

1. 只写提炼后的决策，不写原始长对话。
2. 每条必须包含 `ts/source/confidence`。
3. 在任务完成、收尾、用户纠正后写回。
4. 语义稳定后再蒸馏到 ADR/domain。
