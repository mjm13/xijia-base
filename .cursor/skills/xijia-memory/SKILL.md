---
name: xijia-memory
description: 结构化写回研发记忆（episodic），在 checkpoint 记录决策/结果/置信度/时效。
---

# xijia-memory

## 目标

把跨会话可复用的决策沉淀为结构化记忆，避免重复踩坑。

## 存储

- `docs/memory/decisions.jsonl`

**base 模板仓不包含此文件**；由 `xijia-project-init` 在目标项目 init 时 scaffold 创建。

## 初始化前提（ensure scaffold）

写回前检查：

1. `docs/memory/` 目录存在；不存在则创建。
2. `docs/memory/decisions.jsonl` 存在；不存在则创建空文件。
3. 若项目尚未 init 且无 `AGENTS.md`，提示用户先执行 `/xijia:init`，不得静默写入。

补齐模式（`supplement-only`）下允许按需创建上述 scaffold。

## 记录结构

```json
{"ts":"...","source":"...","decision":"...","result":"...","confidence":0.0,"staleness":"30d","tags":["domain","contract"]}
```

- `ts`：ISO 时间戳；`staleness`：相对有效期（如 `30d`/`90d`），缺省视为永不过期。
- `tags`：用于按 BC/主题检索，建议至少 1 个与 BC 或 capability 对齐的标签。

## 写入规则

1. 只写提炼后的决策，不写原始长对话。
2. 每条必须包含 `ts/source/confidence`。
3. 在任务完成、收尾、用户纠正后写回。
4. 写前按下文「初始化前提」ensure scaffold。

## 读取 / 消费

memory 是双向能力，写入必须配套消费，否则等于未写。

1. 触发时机：任务起点、`explore`、`propose` 前（见 `50-context-engineering` 规则 5）。
2. 过滤方式：按当前 BC/`tags` 匹配，并剔除已过期（`ts + staleness < now`）条目。
3. 使用边界：memory 仅作**先验线索**，不作既定事实；结论仍须经证据链（入口/契约/执行点/数据落点）验证。
4. 文件不存在则 SKIP，不报错。

## 蒸馏

把稳定的过程记忆提升为长期真相源（由 `sync-knowledge` 收尾驱动）。

1. 判据：`confidence >= 0.8` 且语义稳定（多次任务复用、未被推翻）。
2. 动作：**提议**写入 ADR/`docs/domain`，人确认后执行；不自动改长期真相源。
3. 蒸馏后该 memory 条目可在下次剪枝时归档。

## 剪枝 / 自动归档（auto_archive）

防止 `decisions.jsonl` 无限膨胀，过期条目归档但信息不丢失。

1. 语义：过期条目从 `decisions.jsonl` **移动**到 `docs/memory/decisions.archive.jsonl`，绝不物理删除。
2. 判据：`ts + staleness < now`；无 `staleness` 的条目永久保留在主文件。
3. 触发：`sync-knowledge` 收尾运行 `memory_prune.py`。
4. `decisions.archive.jsonl` 只追加，按需首次创建，不进 init manifest。

## 校验与剪枝脚本

- 校验：`python .cursor/skills/xijia-memory/scripts/memory_lint.py`
- 剪枝：`python .cursor/skills/xijia-memory/scripts/memory_prune.py`
- 两者在未 init 的项目（无 `decisions.jsonl`）均 SKIP，不视为失败
