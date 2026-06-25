---
name: xijia-project-init
description: 对话驱动初始化新项目结构与文档骨架。用于全新或空仓库冷启动，不覆盖已初始化仓库；技术栈必须先确认，再自动安装对应高评分技能。
---

# Xijia Project Init

## 目标（初始化边界）

在**空仓库**里通过对话一次性完成可运行的研发骨架文档初始化，并在用户确认技术栈后自动安装对应技能。

本技能只负责（必须）：

- 初始化项目结构与文档骨架（含 `AGENTS.md`）
- 访谈并确认技术栈
- 技术栈确认后自动安装高评分技能
- 输出可追溯初始化报告（清单 + 来源 + 安装结果）

本技能不负责（禁止）：

- 实现业务代码
- 推进具体需求的 explore/propose/apply（这由 `xijia-ops-pipeline` 负责）
- 在已有项目上覆盖文档或重写已存在文件
- 在用户未确认技术栈前安装任何技能

## 触发时机

- 用户说“初始化项目”“从零搭骨架”“生成初始文档”
- 用户使用 `/xijia:init`

## 强制规则（Hard Gates）

1. 先做仓库保护检查（Guard）：
   - 若存在 `docs/` 或 `AGENTS.md`，默认停止并提示“该 init 面向空仓库”
   - 仅当用户明确允许“补齐缺失且不覆盖”时，才进入补齐模式
2. 初始化前必须完成访谈并复述确认（Manifest Confirm）
3. 技术栈必须由用户确认，模型不可擅自指定
4. 评分与安装必须透明：记录候选、评分、入选理由
5. 技能安装遵循“每个技术栈取评分最高的 2-3 个技能”
6. 安装后必须校验 `SKILL.md` frontmatter：`name` 与目录同名
7. 若 `skills` CLI 安装到 `.agents/skills/`，必须搬运到 `.cursor/skills/`
8. 产出初始化锁文件（`skills-lock.json`）时要在报告中说明用途

## 执行步骤（SOP）

### 1) 仓库保护检查（Guard）

- 检查是否已存在 `docs/`、`AGENTS.md`
- 若存在，默认中止并提示改用 `/xijia:start`
- 仅当用户明确要求“补齐模式（仅新增不覆盖）”时继续

### 2) 访谈（只问必要项）

至少收集以下字段：

- 项目名称
- 项目一句话目标
- 是否需要前端（是/否）
- 是否需要数据库（是/否）
- 首批模块（1-2 个）
- 技术栈候选（后端、前端、数据库、部署）

并补充两个决策项：

- 初始化模式：`空仓库初始化` / `补齐模式（仅新增）`
- 技能安装策略：`自动安装` / `仅生成推荐清单`

### 3) 结构预览并确认（Manifest Confirm）

先展示将创建的清单，再请求确认。默认清单：

- `AGENTS.md`
- `docs/constitution.md`
- `docs/README.md`
- `docs/decisions/0001-project-bootstrap.md`
- `docs/domain/README.md`
- `docs/requirements/requirements-template.md`
- `docs/plans/README.md`
- `docs/openspec/config.yaml`

按需创建（不在 init 预生成）：

- `docs/architecture.md`：需求收尾阶段需要沉淀架构决策时创建/更新
- `docs/capability-map.md`：需求收尾阶段命中能力追溯触发条件时创建/更新
- `docs/domain/{context-map,domain-model,ubiquitous-language}.md`：首个业务 change 收尾时创建/更新；init 阶段 `docs/domain/` 只含 `README.md`
- 不创建 `docs/domain/developing/`：🔴 领域草稿置于对应 change 文件夹 `docs/openspec/changes/<name>/domain/`

### 4) 渲染模板并写入（Scaffold）

- 使用 `templates/` 内模板生成文件
- 占位符最小集：
  - `{{project_name}}`
  - `{{project_goal}}`
  - `{{primary_modules}}`
  - `{{chosen_stack_summary}}`
  - `{{author}}`
  - `{{date}}`
- 非空仓库补齐模式下：只创建缺失文件，不覆盖已存在文件

### 5) 技术栈确认后安装技能（Skills Bootstrap）

流程：

1. 列出候选技能来源（`skills.sh`/GitHub）
2. 对每个候选计算评分（0-100）：
   - 生态适配（Cursor 可用）: 30
   - 活跃度（最近 90 天有更新）: 25
   - 社区采用（stars/download）: 20
   - 规范完整度（frontmatter + references）: 15
   - 安装稳定性（命令可重放、目录可预测）: 10
3. 每个技术栈选择 Top 2-3（去重）
4. 安装到 `.cursor/skills/`（必要时搬运 `.agents/skills/`）
5. 校验 `SKILL.md` + frontmatter 一致性
6. 生成安装报告（候选、评分、入选、失败重试命令）

默认映射（可覆盖）：

- FastAPI: `fastapi-best-practices`, `fastapi-reference`
- Vue: `vue-best-practices`
- UI/UX: `ui-ux-pro-max`

说明：基线引擎保持技术栈无关；具体测试命令、工程目录与实现细节由已安装的技术栈技能承载。

### 6) 交付报告（Init Report）

至少包含：

- 初始化模式与 Guard 结论
- 创建文件清单（新增/跳过）
- 技术栈确认摘要
- 技能评分与入选明细
- 技能安装结果（成功/失败/重试命令）
- 下一步：`/xijia:start <首个需求>`

### 7) 自检（Self-Check，进入 done 前强制执行）

自检清单：

1. `requiredFiles`：最小交付集关键文件逐项存在性检查
   - `docs/constitution.md` 必须存在（项目硬约束入口）
   - 按需创建文件不计入 init 阶段必选项：`docs/architecture.md`、`docs/capability-map.md`、`docs/domain/{context-map,domain-model,ubiquitous-language,data-dictionary}.md`
2. `frontmatterValidity`：`.cursor/skills/**/SKILL.md` 的 `name` 与目录同名
3. `entrypointAvailability`：`/xijia:start`、`/xijia:status`、`/xijia:stop` 入口文件存在且基础字段完整
4. `driftScan`：按规则漂移黑名单扫描（见 `06-rule-drift-guard.mdc`）

输出要求：

- 逐项给出 `pass/fail` 与明细
- 任一失败即 `blocked`，不得进入 `done`
- 必须附修复建议与重试路径

## 输出格式（固定）

```markdown
## Xijia Init Status

- Stage: <guard|interview|manifest-confirm|scaffold|skills-bootstrap|done>
- Mode: <empty-repo|supplement-only>
- Created: <created files>
- Skipped: <existing files kept untouched>
- Stack Confirmed: <summary>
- Skills Selected: <name + score + source>
- Skills Installed: <success/fail list>
- Next: </xijia:start ...>
- Blockers: <none or list>
```

## 失败处理

- 非空仓库：中止并提示“使用 `/xijia:start` 或进入补齐模式（仅新增不覆盖）”
- 技能安装失败：记录失败项与重试命令，不中断文档初始化结果回报
- `self-check` 失败：状态置为 `blocked`，输出失败项与修复建议，禁止宣告初始化完成
