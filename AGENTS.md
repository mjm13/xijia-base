# AGENTS

本文件是本仓库 Agent 协作入口。默认遵循技术栈无关基线，具体技术栈细节由后续安装的栈技能提供。

## 路由

- 初始化项目：`/xijia:init` 或 skill `xijia-project-init`
- 启动需求流程：`feature-pipeline`（委托 `xijia-ops-pipeline`）
- OpenSpec 主流程：`explore -> propose -> openspec-superpowers-apply -> verify -> sync -> archive -> sync-knowledge`

## 规则索引

核心基线规则位于 `.cursor/rules/`：

- `00-workflow.mdc`
- `05-project-init.mdc`
- `06-rule-drift-guard.mdc`
- `10-openspec-ddd.mdc`
- `20-backend.mdc`
- `30-frontend.mdc`
- `40-evidence-chain.mdc`
- `41-change-boundary.mdc`
- `42-verification-output.mdc`
- `43-correction-learning.mdc`
- `44-comment-sync.mdc`

## 技能索引（节选）

- `openspec-superpowers-apply`
- `backend-test`
- `frontend-test`
- `verification-before-completion`
- `xijia-comment-enhancer`
- `xijia-git-commit`
- `xijia-manual-test-guide`

## 代码结构与运行方式（占位）

初始化阶段仅保留占位说明。实际后端/前端目录、运行命令、测试命令在对应骨架落地后增量补全。

## 项目信息（占位）

能力清单与模块追溯以 `docs/capability-map.md` 为准，按需求收尾增量维护。
