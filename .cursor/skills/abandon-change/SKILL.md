---
name: abandon-change
description: 放弃未完成功能的对称收尾流程
---

# 目标

当一个 change 决定停止推进时，安全退出并保持文档与规格一致性。

# 输入

- change 名称
- 放弃原因

# 执行步骤

1. 确认该 change 尚未完成归档流程
2. 丢弃对应 worktree/分支中的未合并代码
3. 不执行 `/opsx:sync`，避免污染主 specs
4. 将 change 移入 `docs/openspec/changes/archive/<date>-<name>-dropped/`
5. 回滚本 change 引入但未落地的领域条目（`developing`）
6. 将需求 `status` 标记为 `dropped`，记录原因，并用 `git mv` 移到 `docs/requirements/dropped/`（目录不存在则创建）；移动后 Grep 修正引用该路径的文档，避免死链

# 约束

- 若 change 已上线或已归档，应改用“下线能力”标准流程（REMOVED requirements）
- 遇到删除已上线能力时必须触发人工确认
- 需求文档物理位置须与 `status` 一致（见 `00-workflow.mdc` 文档状态模型）
