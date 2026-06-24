---
name: frontend-test
description: 为前端 Vue3 + TypeScript 代码生成并验证测试。在实现任何前端逻辑/组件前调用，确保每条 AC 有可运行的测试或明确验证命令作为验收门禁。
---

# 目标

以 **红-绿-重构** 循环驱动本项目前端实现：先写测试（RED），看它失败，再写最小实现（GREEN），最后清理（REFACTOR）。**禁止先写实现再补测试。**

与 `openspec-superpowers-apply` 联动：每条 AC 必须有对应测试或明确的可运行验证命令，否则不得勾选任务。

---

# 项目测试基础设施（固定约束）

| 项 | 值 |
| --- | --- |
| 测试框架 | Vitest（`vitest run`） |
| 运行环境 | `environment: 'node'`（见 `frontend/vite.config.ts`） |
| 路径别名 | `@` → `frontend/src`（vite resolve.alias） |
| 测试命名 | 与被测文件同名加 `.test.ts`，**就近放置**（如 `permissions.ts` ↔ `permissions.test.ts`） |
| 运行命令 | `npm run test`（= `vitest run`） |
| 类型检查 | `npm run typecheck`（= `vue-tsc -b`） |
| 构建验证 | `npm run build`（= `vite build`） |

> 全部命令在 `frontend/` 目录下执行。

---

# 当前能力边界（重要）

当前 `environment: 'node'`，**只支持纯逻辑/工具/store/api 单元测试**，不支持组件渲染（无 DOM）。

- ✅ 适用：纯函数、权限判断、storage 工具、pinia store 逻辑、api 客户端参数与解析、mock 数据结构。
- ❌ 不适用：`mount()` 组件、DOM 断言、用户交互（点击/输入）。

**如需组件测试**（命中 Approval Gate：新增依赖，须先请用户确认）：
- 新增 devDependencies：`jsdom`（或 `happy-dom`）、`@vue/test-utils`
- `vite.config.ts` 的 `test.environment` 改为 `'jsdom'`
- 确认后再写 `mount()` 类测试

不要擅自加包改环境。组件交互在依赖到位前，用 e2e/手动验证步骤替代，并在 AC↔Test 表标注。

---

# 分层选型决策树

```
Q1: 被测对象是否需要渲染 DOM / 触发用户交互？
├── 否（纯逻辑/工具/store/api）→ Vitest 单元测试（当前环境直接可跑）
└── 是（组件渲染/交互）→ 需先加 jsdom + @vue/test-utils（Approval Gate）
                          依赖到位前：改为 e2e 或明确手动验证步骤
```

| 场景 | 方式 | 示例 |
| --- | --- | --- |
| 纯函数 / 权限判断 | `import` 后直接断言 | `permissions.test.ts` |
| storage / 浏览器 API | `vi.stubGlobal` 注入桩 | `auth-utils.test.ts` |
| api 客户端 | mock `fetch` / 注入桩，断言参数与解析 | `system.test.ts` |
| pinia store | 实例化 store，断言 action/状态 | — |
| 组件渲染/交互 | `@vue/test-utils` + jsdom（需先加依赖） | — |

---

# TDD 执行步骤

## STEP 1 — 写测试（RED）

1. 读取 AC，每条 AC 对应一个或多个 `it()`
2. 测试就近放置，命名 `<被测>.test.ts`
3. `it` 描述用行为语义：`it('denies access when permission missing', ...)`
4. 写完运行一次确认 RED：

```powershell
cd frontend; npm run test
```

预期：模块不存在（编译失败）或断言失败——任一即合格 RED。若直接 GREEN → 测试写错，重写。

## STEP 2 — 写实现（GREEN）

- 只写让测试通过的最小代码
- 禁止加未被测试覆盖的"备用"分支
- 完成后跑测试 + 类型检查：

```powershell
cd frontend; npm run test; npm run typecheck
```

全绿且无类型错误才算 GREEN。

## STEP 3 — 重构（REFACTOR）

- 消除重复、改善命名，再跑一次保持 GREEN。

---

# 典型模板

## 纯逻辑

```ts
import { describe, expect, it } from 'vitest'
import { canAccessPath } from '@/config/permissions'

describe('permissions', () => {
  it('denies access when permission missing', () => {
    expect(canAccessPath(new Set(['home:read']), '/identity/org')).toBe(false)
  })
})
```

## 浏览器 API（stub 全局）

```ts
import { beforeEach, describe, expect, it, vi } from 'vitest'

describe('auth-utils', () => {
  beforeEach(() => {
    vi.stubGlobal('localStorage', createStorage())
  })
  it('returns null when token missing', () => {
    expect(loadAuthFromStorage()).toBeNull()
  })
})
```

## api 客户端（mock fetch）

```ts
import { afterEach, describe, expect, it, vi } from 'vitest'

describe('system api', () => {
  afterEach(() => vi.restoreAllMocks())

  it('calls system info endpoint and unwraps data', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ code: 0, data: { release: 'v1' } }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const info = await getSystemInfo()

    expect(fetchMock).toHaveBeenCalledOnce()
    expect(info.release).toBe('v1')
  })
})
```

---

# 验收门禁（与 openspec-superpowers-apply 联动）

每个 AC 勾选前必须满足：

- [ ] 有对应测试方法（命名/描述可追溯到 AC），或纯视觉 AC 有明确手动/e2e 验证步骤
- [ ] 见过该测试 RED（失败输出）
- [ ] `npm run test` 全绿
- [ ] `npm run typecheck` 无类型错误
- [ ] 涉及构建产物时 `npm run build` 通过

---

# 禁止行为

- 先写实现再补测试（哪怕"就这一次"）
- 为通过测试擅自改 `vite.config.ts` 测试环境或加依赖（组件测试依赖需走 Approval Gate）
- 用 `it.skip` / `describe.skip` 跳过失败测试而不修复
- 在 `environment: 'node'` 下写 `mount()` 组件测试（DOM 不存在，必然失败）

---

# 常见错误速查

| 错误 | 原因 | 修法 |
| --- | --- | --- |
| `document is not defined` / `window is not defined` | node 环境无 DOM | 纯逻辑测试不应触碰 DOM；组件测试需切 jsdom（加依赖） |
| `Cannot find module '@/...'` | 别名未解析 | 确认从 `frontend/` 运行；vite alias `@`→`src` 已配 |
| `localStorage is not defined` | node 环境无 storage | 用 `vi.stubGlobal('localStorage', ...)` 注入桩 |
| 测试直接 GREEN（未见 RED） | 测试在测桩而非真实逻辑 | 删实现重看 RED，确认断言指向被测代码 |
| 类型报错但测试过 | 只跑了 vitest 未跑 typecheck | 补跑 `npm run typecheck` |
