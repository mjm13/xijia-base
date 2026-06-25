---
name: ddd-modeling
description: 从需求中提炼机器可读 DDD 契约产物；🔴 草稿写入 change/domain，归档后提升到 docs/domain。
---

# 目标

把业务语义沉淀为可校验契约，而非散文描述，减少 AI 同义词漂移与上下文污染。

# 输出文件（🔴 草稿：docs/openspec/changes/<name>/domain/）

- `ubiquitous-language.md`（必须含 BC、锚点、Aliases to AVOID）
- `domain-model.md`（必须含每个聚合的 `INV-xxx`）
- `context-map.md`（必须标注关系 Pattern）
- `aggregate-spec.md`（聚合规格）
- `anti-corruption-layer.md`（ACL 规格）
- `bounded-context-canvas.md`

# 必做约束

1. 每个聚合至少 1 条 `INV-xxx` 不变量。
2. 每个新增术语必须给出 BC + 锚点 + 至少 1 个禁用别名（Aliases to AVOID）。
3. `aggregate-spec` 与 `anti-corruption-layer` 标注为“人写优先，LLM 仅消费”。
4. 技术 change 不调用本技能。

# 执行步骤

1. 判定 change 类型（business/hybrid 才继续）。
2. 按模板补齐 6 份契约文档。
3. 运行校验脚本：
   - `python .cursor/skills/ddd-modeling/scripts/validate_domain_contracts.py --path "<domain-dir>"`
4. 若校验失败，修正文档后重跑。

# 完成判定

- 校验脚本通过（无 ERROR）
- `INV-xxx`、BC、Aliases to AVOID、关系 Pattern 均存在
