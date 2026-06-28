---
name: xijia-git-commit
description: 生成可追溯的 Git 提交信息——自动关联需求/bug 并总结本次修改范围与内容。当准备执行 git commit、整理提交信息，或用户要求“提交/commit 代码”时使用。
---

# Git 提交（关联需求 + 范围总结）

## 目标

每次提交都可追溯：自动关联对应**需求 / bug**，在 message 中清晰总结本次**修改范围与内容**，并遵守 `.cursor/rules/00-workflow.mdc`「需求收尾门禁」与内置 Git 安全协议。

## 触发

- 准备执行 `git commit` 之前
- 用户说「提交」「commit 一下」「帮我提交代码」
- 一个需求/切片完成、进入收尾的最终操作时

## 执行步骤

1. **收集变更证据**（并行）：`git status`、`git diff --staged`（无暂存则 `git diff`）、`git log --oneline -5`（对齐本仓提交风格）。

2. **自动关联需求 / bug**：
   - 先看当前分支名 `change/<name>` → 映射到 `docs/requirements/**/*<name>*.md`。
   - 分支无线索时，在 `docs/requirements/inbox/` 找 `status: in-change`（或进行中）的需求。
   - 推断出**唯一**目标 → 直接关联；命中**多个或零个** → 才向用户确认。

3. **总结范围与内容**：按改动的文件/目录归类，提炼「改了什么 + 为什么」，**不逐行复述 diff**。

4. **生成 message**（见模板），类型用约定式：`feat` / `fix` / `refactor` / `chore` / `docs` / `test`。

5. **提交前门禁自检**（来自 `00-workflow.mdc`）：
   - 不含疑似密钥文件（`.env`、`credentials.*` 等），命中则警告并暂停。
   - 一个需求 ideally 一个 commit；同需求多切片可多个 commit。
   - requirement 文档 `分级与判型` 中 Gate-2 必须已回填审批人/日期（未签字不得作为“已完成提交”对外口径）。
   - 不更新 git config、不加 `--no-verify`、不擅自 `push`、不对已推送提交 `--amend`。

6. **提交并复核**：暂存相关文件，传入 message 执行 `git commit`，提交后用 `git log -1 --format=%B` 确认消息（尤其中文）未损坏，再 `git status` 确认成功。

## Commit Message 模板

```
<type>(<scope>): <一句话：做了什么，聚焦为什么>

- <范围/内容要点 1>
- <范围/内容要点 2>

Refs: docs/requirements/inbox/<req-file>.md
```

- **bug 修复**：用 `fix(<scope>): ...`，关联脚注写 `Fixes: <bug 来源/编号>`。
- **无对应需求**（纯工程杂项）：可省略 `Refs`，但正文要说明动机。
- 关联路径必须指向**真实存在**的需求文件，写入前先确认路径，避免死链。

## 约束

- message 聚焦「为什么」，不复制 diff、不堆砌技术名词。
- 命中 Approval Gate（破坏性 DB 变更 / 密钥 / 下线已上线能力 / 权限策略变更等）先暂停请求确认，见 `00-workflow.mdc`。
- 是否 `push` 由用户决定；仅在用户明确要求时执行。
- 本技能只负责「生成消息并提交」；需求状态迁移、文档同步等收尾动作仍按 `00-workflow.mdc` 收尾顺序执行。
- **Windows PowerShell 中文编码**：message 含中文时**禁止**用 `@"..."@ | git commit -F -` 或 `-m "中文"`（默认 ASCII 管道会把中文转成 `?` 损坏消息）。应先将消息写入 **UTF-8 文件**，再 `git commit -F <文件>`，提交后核验 `git log -1 --format=%B`；`git log` 输出末尾若有零星乱码，多为控制台按宽度截断多字节字符的显示问题，以提交头摘要行能否正确显示为准。
