---
name: openspec-superpowers-apply
description: >-
  OpenSpec apply 与 Superpowers 强制联动实现入口。读取 change 的 tasks/design/specs
  跟踪进度（WHAT），并用 TDD、调试、验证、评审技能驱动编码（HOW）。在用户说
  开始实现、继续实现 change 任务、或显式调用本技能时使用；禁止仅用 openspec-apply-change
  裸跑而不加载 Superpowers。本技能是本项目实现阶段的唯一推荐入口。
---

# OpenSpec + Superpowers Apply

将 OpenSpec 的 **任务编排** 与 Superpowers 的 **实现方法论** 绑定为单一入口。

- OpenSpec：管 **做什么**（tasks、进度、勾选）
- Superpowers：管 **怎么做**（TDD、调试、验证、评审）

**禁止**：只调用 `openspec-apply-change` 直接写代码，不加载 Superpowers 技能。

## 真相源裁决：测试 > Spec

Spec/design 无裁判机制，测试有 pass/fail。冲突时：

- 任务完成由**测试/验证裁决**，不由 Spec 自洽裁决
- 测试暴露 Spec 错误 → **暂停**，先改 `design.md`/spec，再继续（不静默跳过）
- Spec 只锁 What（边界/不变量/AC），不锁 How（选型/实现/结构）
- 每条 AC 应有对应测试；AC 无对应测试不得勾选该任务

---

## 何时使用

- 用户说「开始实现」「继续实现」或显式调用 `openspec-superpowers-apply`
- 编排流水线（`xijia-ops-pipeline` / `feature-pipeline`）进入实现阶段
- change 的 artifacts 已齐全，tasks 有待办项

**不要单独使用** `openspec-apply-change`；本技能是其包装层。

---

## 强制技能绑定（每步必须执行）

| 阶段 | 必须加载的技能 | 作用 |
|------|----------------|------|
| 开工前 | `openspec-apply-change` | 选 change、读 context、列任务 |
| 写代码前 | `test-driven-development` | 能测的先测，再写实现 |
| 遇错/失败 | `systematic-debugging` | 有证据再修，禁止猜修 |
| 勾选任务前 | `verification-before-completion` | 跑命令、看输出，再标完成 |
| 全部任务后 | `requesting-code-review` | 对照 design/specs 评审 |

多任务并行时，可额外使用 `subagent-driven-development` 或 `executing-plans`。

---

## 执行步骤

### 0. 开工门禁

1. 确认 change 名称（未提供则从上下文推断或 `openspec list --json`）
2. 宣布：`Using change: <name> via openspec-superpowers-apply`
3. 检查 `00-workflow.mdc` 的 Approval Gates；命中则暂停等用户确认

### 1. OpenSpec 上下文（WHAT）

按 `openspec-apply-change` 执行步骤 1–5：

```bash
openspec status --change "<name>" --json
openspec instructions apply --change "<name>" --json
```

读取 `contextFiles` 中的 proposal、design、tasks、specs。

输出当前进度：`N/M tasks complete`，列出待办。

### 1.5 建立 AC↔Test 追溯表（右端 Eval 硬门）

从 spec 的验收标准（AC，即 `#### Scenario` / WHEN-THEN）逐条建立映射：

| AC | 对应测试 | 状态 |
| --- | --- | --- |
| AC-1 余额不足返回 40003 | `OrderTest#insufficientBalance` | 待写 |

规则：
- **门禁只约束「本切片 In Scope 的 AC」**；proposal 中标注 `Out of Scope` / `Deferred` 的 AC 不阻塞本切片完成
- 本切片每条 AC 必须有对应测试（前端视觉类用 e2e/snapshot 或明确手动验证步骤）
- AC 无对应测试 → **不得勾选**相关任务
- AC 与实现冲突 → 测试为准；若 AC 本身错 → 暂停改 spec

### 2. 实现循环（HOW + WHAT）

对每个 **未完成** 任务，严格按序：

```
A. 宣布：Working on task X/Y: <描述>
B. 加载 test-driven-development
   - 判断本任务是否可写测试；能测则先写失败测试
   - UI/脚手架类任务：至少定义可运行验证命令（build/dev/smoke）
C. 实现最小改动
D. 若失败 → 加载 systematic-debugging，禁止无证据改代码
E. 加载 verification-before-completion
   - 运行相关命令（如 npm test / npm run build / mvn test）
   - 必须引用实际输出，再勾选 tasks.md：- [ ] → - [x]
F. 进入下一任务
```

**勾选门禁**：未通过步骤 E 的证据，不得勾选任务。

### 3. 阶段完成

当所有任务勾选完毕：

1. **AC↔Test 闸门**：步骤 1.5 的追溯表必须每条 AC 都有「通过」的测试，否则视为未完成
2. 加载 `requesting-code-review`（或 code-reviewer 子代理）
3. 对照 design.md 与 delta specs 做符合性检查
4. **沉淀检查**：对照 `00-workflow.mdc` 沉淀三问，把业务规则/决策/数据语义写入 `docs/domain` / ADR / 数据字典
5. **写入「人工验收说明」**：追加到对应需求文件的 `# 验收记录` 段（`docs/requirements/inbox/<req>.md`，多切片追加不覆盖），并在收尾摘要中复述。必须点名改了哪个菜单/模块（moduleKey）、什么功能、什么场景、怎么手动点验，并如实列出 `Out of Scope / Deferred`（模板见 `00-workflow.mdc`）
6. **文档同步**：`/opsx:sync` → `/opsx:archive` → `sync-knowledge`（🔴）；需求 `status: shipped` 与目录一致
7. **git commit（最终操作）**：提交本需求全部代码与已同步文档；确认 `git status` 干净后再输出完成摘要
8. 输出 session 摘要（见下方模板）；**禁止**在未 commit 时建议「开始下一需求」

### 4. 暂停条件

以下情况停止并报告，不擅自继续：

- 任务描述不清
- 实现暴露 design 缺陷
- 命中 Approval Gate
- 验证命令失败且调试未收敛
- 用户中断

---

## 输出模板

### 进行中

```markdown
## Implementing: <change-name> (openspec-superpowers-apply)

**Progress:** X/Y tasks complete
**Current:** task X — <description>
**Superpowers:** TDD → implement → verify (evidence below)

<verification command output>
```

### 完成

```markdown
## Implementation Complete: <change-name>

**Progress:** Y/Y tasks complete
**Verified:** <commands run>
**Review:** <brief review summary>

### 人工验收说明（Acceptance Note）
- 涉及菜单 / 模块：<moduleKey + 路径，或「后端 API / 无界面」>
- 改了什么功能：<一句话>
- 验收场景：1. GIVEN ... WHEN ... THEN ...
- 手动验证步骤：<点哪里、看到什么 / 接口示例与预期响应>
- 自动化覆盖：<测试名/命令>；需人工点验：<...>
- 本次范围外 / Deferred：<对齐 proposal 的 Open Questions>
- **Git：** `<commit hash>` — `<commit message 摘要>`

**Next:** 仅当 commit 成功后，才可启动下一需求；无待办 change 时流程结束
```

---

## 与编排流水线的关系

编排真相源是 `xijia-ops-pipeline`（`feature-pipeline` 为其模型可发现的薄别名）。其 Red 档「实现」步骤应写：

> 调用 **openspec-superpowers-apply**（本项目实现阶段唯一入口）

本技能是端到端流水线中「实现阶段」的唯一推荐入口。

---

## Guardrails

- 不得跳过 `test-driven-development` 直接堆代码（纯配置/脚手架任务可用可运行验证替代测试）
- 不得在未运行验证命令的情况下勾选 tasks
- 不得在 AC↔Test 追溯表存在「无对应测试的 In Scope AC」时声称完成（`Deferred` AC 除外）
- 不得在未做 code-review 的情况下声称 change 实现完成
- 不得在未把「人工验收说明」（菜单/模块、功能、场景、手动验证步骤）写入需求文件 `# 验收记录` 段的情况下收尾
- **不得在未 git commit 的情况下宣告需求完成或开始下一需求**（见 `00-workflow.mdc`「需求收尾门禁」）
- 保持改动最小，单任务单提交语义（一次对话内可多个任务，但每个任务独立验证）
- 验证失败时不得标记任务完成
