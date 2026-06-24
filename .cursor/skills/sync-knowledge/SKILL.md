---
name: sync-knowledge
description: 归档后知识回灌（spec/change -> docs/domain + ADR + capability map）
---

# 目标

在 change 完成归档后，将增量知识沉淀到长期文档，形成迭代闭环。

# 输入

- change 名称
- 该 change 的 design、tasks、delta specs

# 执行步骤

1. 读取已归档 change 的设计与 specs 变更
2. 判定 change type；仅将业务 / 混合 change 的**业务语义**从 change 文件夹 `docs/openspec/changes/<name>/domain/*` 提升到 `docs/domain/*`（目标文件不存在则创建）
2.5. **沉淀三问硬门禁（不可跳过，即使本 change 主体是 UI / 壳层）**：逐条核对本 change 的 delta spec 与实现是否引入——①新的业务规则 / 不变量（如「ADMIN 角色不可改」「角色权限变更需重新登录生效」「OrgNode 禁止成环」）；②非显而易见的决策原因；③数据库字段业务语义 / 状态机 / 约束理由。**任一为「是」即必须回灌 `docs/domain`（或 ADR / data-dictionary），UI/壳层判型只豁免框架与布局实现，不豁免其中的业务不变量。** 若 change 草稿为空但门禁命中，说明 propose 阶段漏写草稿，此时直接补写 `docs/domain` 并在收尾摘要中标注「补录」。门禁结论（命中/未命中 + 去向）必须在收尾摘要中显式说明，不得静默跳过。
3. 提升完成后，change 文件夹内的领域草稿随 change 归档一并离场；只保留已确认事实在 `docs/domain/`
4. 更新 `docs/domain/` 的 context map、domain model、ubiquitous language（仅保留已确认事实）
5. 检查数据库业务语义：新增/变更表、字段含义、状态机、约束理由时，更新 `docs/domain/data-dictionary.md`；如只需要关系级 ER 图，仅画表间业务关系，不复制 DDL
6. 检查能力追溯索引：当 change 新增、下线、重命名业务模块，变更前端 `moduleKey`，或新增模块相关业务表时，更新 `docs/capability-map.md`
6.5. 检查 `AGENTS.md`（活文档）：当本 change 引入/变更可运行结构（后端/前端骨架、目录布局）、运行/测试/构建命令，或业务模块增减时，更新 `AGENTS.md` 的「代码结构与运行方式 / 项目信息」；路由与流水线区块保持不动
7. 如有架构或流程决策，新增 ADR
8. 若发现设计与实现偏差，记录待修正事项
9. 将对应需求 `status` 置 `shipped`，并用 `git mv` 移到 `docs/requirements/shipped/`；移动后 Grep 修正引用该路径的文档，避免 dead 链
10. **提醒**：`sync-knowledge` 之后还必须 **git commit**（本需求最终操作），见 `00-workflow.mdc`「需求收尾门禁」；未 commit 不得开始下一需求

# 约束

- 未归档 change 的内容不得写入 `docs/domain/*`
- 回灌优先做增量修改，避免重写整份文档
- 技术 / UI 壳层 change 不写入 `docs/domain/context-map.md`、`domain-model.md` 或 `ubiquitous-language.md`；`platform-shell`、布局、Design Token、AuthStore、框架类名、拦截器、具体鉴权库 API 等内容应写入 ADR、`docs/architecture.md`、OpenSpec 技术 spec 或 `docs/capability-map.md`
- `docs/capability-map.md` 只记录模块级指针，不复制子菜单、路由明细或表结构；真相分别在前端路由/菜单、OpenSpec specs 与迁移脚本
- 需求文档物理位置须与 `status` 一致（见 `00-workflow.mdc` 文档状态模型）
