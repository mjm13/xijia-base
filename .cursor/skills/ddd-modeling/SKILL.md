---
name: ddd-modeling
description: 从需求中提炼 DDD 产物并沉淀到 docs/domain/developing
---

# 目标

在 explore/propose 前后，将**业务 change** 或**混合 change 中的业务部分**转化为可追踪的领域建模文档。

# 何时调用

| change 类型 | 是否调用本 skill |
| --- | --- |
| **业务 change** | 必须 |
| **混合 change** | 必须（仅建模业务部分） |
| **技术 change** | **跳过**——工程骨架、日志、Actuator 等横切能力不属于限界上下文 |

技术 change 示例：`springboot-backend-skeleton` 不调用本 skill；若后端对接已有 `identity-access`，仅在归档后由 `sync-knowledge` 更新该条目描述，不新建 `logging` / `api-foundation` 等 context。

# 输入

- 需求文档路径或需求描述文本
- change 类型（业务 / 混合；技术 change 不应进入本 skill）

# 输出文件（开发中）

- `docs/domain/developing/context-map.md`
- `docs/domain/developing/ubiquitous-language.md`
- `docs/domain/developing/domain-model.md`

# 执行步骤

1. 确认 change 为业务或混合类型；若为技术 change，停止并改用 ADR
2. 提取核心业务能力与候选限界上下文（禁止把横切基建当作新 context）
3. 梳理关键术语并写入 `developing` 术语表
4. 识别聚合根、实体、值对象、领域事件
5. 在 context map 中标注上下游关系
6. 输出需要用户确认的高风险假设（如跨上下文一致性规则）

# 约束

- 不直接修改应用代码
- 术语命名与 OpenSpec capability 尽量一一对应
- 禁止为纯技术 capability（如 `logging`、`health-monitoring`、`project-structure`）创建限界上下文
- 未归档 change 只能写入 `docs/domain/developing/*`，不得写入 `docs/domain/established/*`
