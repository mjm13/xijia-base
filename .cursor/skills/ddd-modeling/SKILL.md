---
name: ddd-modeling
description: 从需求中提炼 DDD 产物，🔴 草稿写入对应 OpenSpec change 文件夹，归档后提升到 docs/domain（侧重沉淀代码看不出的业务知识，供后续 AI 自主研发复用）
---

# 目标

在 explore/propose 前后，把**业务 change** 或**混合 change 的业务部分**转化为可追踪的领域建模文档。

核心意图：**沉淀代码无法表达的业务知识**——业务规则与不变量、状态流转、决策理由、领域事件语义、跨上下文契约——使后续 AI（与人）脱离代码也能理解业务全貌并据此自主研发。

# 领域知识存放位置（重要）

- `docs/domain/*` 是已发布事实，**AI 读取现状 / 已有功能时只读这里**，不读任何 change 草稿
- 🔴 开发中草稿写入 change 文件夹 `docs/openspec/changes/<name>/domain/`；归档后由 `sync-knowledge` 提升到 `docs/domain/`，草稿随 change 离场
- 🟢 / 🟡 无 OpenSpec change：人确认后直接写 `docs/domain/`（不经过草稿）

# 读者与质量基线（写给未来的 AI 与人）

- 自包含：术语与规则不依赖“看代码才懂”的隐含上下文
- 显式优先：规则用 `GIVEN/WHEN/THEN` 写清，每条可追溯到 AC / 测试
- 不抄实现：代码即文档；这里只记代码看不出的 What/Why，不复制类名、框架、SQL
- 增量追加：活文档逐切片生长，新增条目标注来源切片，不覆盖历史
- 锚点可跳转：术语/模型尽量标注对应 capability / 模块 key，便于关联代码与 `capability-map.md`

# 何时调用

| change 类型 | 是否调用本 skill |
| --- | --- |
| **业务 change** | 必须 |
| **混合 change** | 必须（仅建模业务部分） |
| **技术 change** | **跳过**——工程骨架、日志、健康监测等横切能力不属于限界上下文 |

技术 change 示例：`backend-skeleton` 不调用本 skill；若后端对接已有业务上下文，仅在归档后由 `sync-knowledge` 更新该条目描述，不新建 `logging` / `api-foundation` 等 context。

# 输入

- 需求文档路径或需求描述文本
- change 类型（业务 / 混合；技术 change 不应进入本 skill）

# 沉淀什么（代码外知识清单 — 必查，命中即写）

逐项核对本 change 是否引入，命中即写：

1. 业务规则 / 不变量（如“截止后不可撤回”“扣费不退款”“角色变更需重新登录生效”）
2. 状态机 / 生命周期（有哪些状态、合法转移、触发条件、终态）
3. 领域事件（事件名 + 触发条件 + 业务含义 + 下游影响）
4. 跨上下文一致性规则与契约（谁是上游、同步/最终一致、翻译语义）
5. 决策理由（为何这样建模/取舍）→ 同步提示写 ADR
6. 边界与反例（易混淆术语、非法输入、明确不做什么）

# 输出文件（🔴 开发中草稿，置于 change 文件夹 `docs/openspec/changes/<name>/domain/`）

- `ubiquitous-language.md`：术语 = 业务定义 + 所属上下文 + 边界/易混淆 + 对应 capability/模块（锚点）
- `domain-model.md`：按聚合组织 → 聚合根/实体/值对象 + **每个聚合的不变量** + 生命周期/状态机 + 关键命令 + 领域事件
- `context-map.md`：限界上下文 + 上下游关系 + 集成模式与契约（业务语义，不写框架/防腐层实现）
- 字段级业务语义 / 状态机 / 约束理由 → 指向 `docs/domain/data-dictionary.md`（归档时由 `sync-knowledge` 落库）

> 🟢 / 🟡 无 OpenSpec change 时不建草稿，收尾人确认后直接写 `docs/domain/*`。

# 执行步骤

1. 确认 change 为业务或混合类型；若为技术 change，停止并改用 ADR
2. 提取核心业务能力与候选限界上下文（禁止把横切基建当作新 context）
3. 过“代码外知识清单”，逐条命中逐条记
4. 术语写入 change 草稿术语表，附业务定义与锚点
5. 建模聚合：标注不变量、状态机、关键命令、领域事件
6. 在 context map 中标注上下游、集成模式与契约语义
7. 输出需用户确认的高风险假设（跨上下文一致性、不可逆操作、权限/资金规则）

# 完成判定（草稿条目可用性）

- 每条不变量能对应一条 AC / 可测断言
- 每个状态机有合法转移与终态，无悬空状态
- 每个领域事件写明触发与下游影响
- 高风险假设已显式 park 或经用户确认

# 约束

- 不直接修改应用代码
- 术语命名与 OpenSpec capability 尽量一一对应
- 禁止为纯技术 capability（如 `logging`、`health-monitoring`、`project-structure`）创建限界上下文
- 未归档 change 的领域草稿只能写入 `docs/openspec/changes/<name>/domain/`，不得写入 `docs/domain/*`
- 增量追加，不覆盖历史条目
