---
name: xijia-docs-score
description: 统计 docs 文档在真实研发中的使用价值，输出高价值/低价值/从未使用文档，并给出修订或删除候选。
---

# xijia-docs-score

## 目标

建立文档自净闭环：不是统计“是否被读过”，而是评估“是否支持了真实研发决策”。

## 数据文件

- 使用事件：`scripts/.generated/docs_usage.jsonl`
- 判定事件：`scripts/.generated/docs_judgments.jsonl`
- 聚合结果：`scripts/.generated/docs_score.json`
- 报告输出：`.cursor/skills/xijia-docs-score/reports/文档评分报告.md`

## 评分口径

- `score = useful - misleading`
- `neutral` 仅记录，不加减分
- `used_count == 0` 归类“从未被用”（仅候选，不自动删除）

## 建议流程

1. 运行聚合：
   - `python .cursor/skills/xijia-docs-score/scripts/score_docs.py`
2. 查看候选：
   - `--top 20`
   - `--never-used`
   - `--useless-candidates`
   - `--negative-candidates`
3. 追加判定（每次需求收尾后）：
   - `--judge-doc ... --judge-session ... --judge-verdict useful|neutral|misleading --judge-reason "..."`
4. 重新生成报告并人工复核后再决定修订/删除。

## 判定三问（推荐）

1. 该文档是否支撑了具体开发决策（模块/接口/表/流程）？
2. 不看该文档，是否仍会做出同样决策？
3. 该文档是否导致错误路径并被证伪？

判定映射：

- useful：是 / 否 / 否
- neutral：否 / 是 / 否
- misleading：第三问为是

## 约束

- 只输出“修订/删除候选”，不自动删除文件。
- 结论必须可追溯到 usage + judgment 记录。
