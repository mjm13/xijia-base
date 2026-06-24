---
name: backend-test
description: 为后端 Spring Boot 代码生成并验证测试。在实现任何业务 Controller/Service 前调用，确保每个 AC 有可运行的测试作为验收门禁。
---

# 目标

以 **红-绿-重构** 循环驱动本项目后端实现：先写测试（RED），看它失败，再写最小实现（GREEN），最后清理（REFACTOR）。**禁止先写实现代码再补测试。**

---

# 项目测试基础设施（固定约束，不可绕过）

| 项 | 值 |
| --- | --- |
| 框架 | JUnit 5 + Spring Boot Test + Mockito（均由 `spring-boot-starter-test` 引入） |
| 测试数据库 | H2 in-memory，`MODE=MySQL`（`application-test.yml`） |
| Flyway（测试） | `classpath:db/migration-test`（H2 专用，与生产 `db/migration` 分离） |
| Flyway（生产/dev） | `classpath:db/migration`（MySQL） |
| 集成测试 profile | `@ActiveProfiles("test")`，启动类 `TysfrzApplication` |
| 运行前置 | `JAVA_HOME` 必须指向 **JDK 21**；本机示例路径：`C:\Users\mjm13\.jdks\ms-21.0.10` |
| 运行命令 | `mvn -f backend/pom.xml test`（Reactor 根 POM；确保 `JAVA_HOME` 已指向 JDK 21） |
| 测试类命名 | `<被测类>Test`，不加 `IT` 后缀 |

---

# 分层选型决策树

```
Q1: 测试是否触及数据库（读/写任何表）？
├── 是 → @SpringBootTest + @AutoConfigureMockMvc（可选）
│         + @ActiveProfiles("test")
│         + 真实 H2 + Flyway migration-test
│         + 真实 Service / Mapper / Repository（禁止 @MockBean Mapper）
│         + 数据：Flyway 种子 → 不足则在测试内 TestDataSupport / @BeforeEach 插入
└── 否 → Q2: 是否纯领域计算（如 DataScopeResolver）？
           ├── 是 → 纯 JUnit，构造内存数据结构
           └── 否 → @WebMvcTest（仅 Ping/CORS 等无 DB 横切）
                     + @Import(GlobalExceptionHandler, CorsConfig)
                     + @ActiveProfiles("dev")
                     + @MockBean 仅用于隔离非被测 Controller 的 Service
```

**何时用哪种：**

| 场景 | 注解 | 数据 |
| --- | --- | --- |
| 含 DB 的 Controller/Service 验收 | `@SpringBootTest` | 真实 H2 + 测试内补数据 |
| 鉴权/权限/DataScope 链路 | `@SpringBootTest` | Flyway V3 种子 + org_node 最小集 |
| 纯领域规则（无 DB） | 纯 JUnit | 内存构造 |
| 仅 HTTP 格式/CORS（无 DB） | `@WebMvcTest` | 无 DB |

> **真实数据规则（强制）**：凡涉及持久化的测试，必须让数据经 Flyway 或真实 Mapper 写入 H2。禁止 `@MockBean` Mapper/Repository 返回假数据。缺数据时在测试类内创建符合业务不变量的记录（部门 code 存在于 org_node、ACTIVE 状态、BCrypt 密码等）。辅助类：`com.xj.tysfrz.testsupport.TestDataSupport`。

---

# TDD 执行步骤

## STEP 1 — 写测试（RED）

1. 读取 AC（验收标准），每条 AC 对应一个或多个 `@Test` 方法
2. 按分层决策树选注解
3. 测试方法命名：`<场景>_should<预期结果>`，例如：
   - `getInfo_shouldReturnRelease()`
   - `createUser_whenEmailBlank_shouldReturnBizError()`
4. 写完测试，**运行一次确认 RED**：

```powershell
# 若 JAVA_HOME 未指向 JDK 21，先设置（本机示例路径，见上方测试基础设施表）：
# $env:JAVA_HOME = 'C:\Users\mjm13\.jdks\ms-21.0.10'
mvn -f backend/pom.xml test
```

预期：编译失败（类不存在）或断言失败——**任意一种都算合格的 RED**。  
如果测试直接 GREEN → 测试写错了，重写。

## STEP 2 — 写实现（GREEN）

- 只写让测试通过的最小代码
- 禁止在实现阶段加"备用"逻辑或未被测试覆盖的分支
- 实现完成后运行测试确认 GREEN：

```powershell
mvn -f backend/pom.xml test
```

所有测试必须通过，**输出中不得有编译警告或 Spring 上下文错误**。

## STEP 3 — 重构（REFACTOR）

- 消除重复代码、改善命名
- 重构完再跑一次测试，保持 GREEN

---

# 典型模板

## 集成测试（真实 DB + 测试内补数据）

```java
@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class UserAdminFlowTest {

    @Autowired MockMvc mockMvc;
    @Autowired PlatformUserMapper userMapper;
    @Autowired PasswordEncoder passwordEncoder;

    @BeforeEach
    void seedCaseUser() {
        // Flyway 种子不足时，在测试内插入符合规则的业务数据
        TestDataSupport.insertActiveUser(
                userMapper, passwordEncoder,
                "case_user", "Passw0rd!", "CAT-party", DataScope.OWN_DEPT);
    }

    @Test
    void createUser_whenDuplicateUsername_shouldFail() throws Exception {
        // ... 使用真实 DB 状态断言
    }
}
```

---

# 验收门禁（与 openspec-superpowers-apply 联动）

每个 AC 勾选前必须满足：

- [ ] 有对应测试方法（命名可追溯到 AC）
- [ ] 看到该测试 RED（失败日志截图或输出）
- [ ] `mvn test` 全绿，无 `ERROR`、无 Spring 上下文失败
- [ ] 测试不依赖外部 MySQL（只用 H2 + Flyway migration-test）
- [ ] DB 相关测试使用真实持久化；缺数据已在测试内插入，未 Mock Mapper

---

# Flyway 双轨（与生产分离）

| 轨道 | 目录 | profile |
| --- | --- | --- |
| 生产/开发 | `xj-tysfrz-business/src/main/resources/db/migration/` | dev, prod |
| 测试 | `xj-tysfrz-business/src/test/resources/db/migration-test/` | test |

- 测试迁移：H2 兼容语法 + 最小业务种子（版本号与生产对齐）
- 新增生产表结构时，**同步**新增测试侧同版本脚本
- 详见各目录下 `README.md`

# 禁止行为

- **先写实现再补测试**（哪怕"就这一次"）
- 为通过测试修改 H2/Flyway 配置文件（测试应适配基础设施，不是反过来）
- 在 `@SpringBootTest` 集成测试中对 Mapper/Repository 使用 `@MockBean` 伪造 DB 数据
- 使用 `@Disabled` 跳过失败测试而不修复
- 在 `application-test.yml` 里设置 `spring.flyway.enabled=false`（破坏 DB 迁移验证）

---

# 常见错误速查

| 错误 | 原因 | 修法 |
| --- | --- | --- |
| `NoSuchBeanDefinitionException: XxxService` | `@WebMvcTest` 没有 `@MockBean` Service | 加 `@MockBean XxxService` |
| `Flyway: Found non-empty schema without schema history table` | H2 模式问题 | 确认 `application-test.yml` 有 `baseline-on-migrate: true` |
| `H2 does not support ... function` | 迁移脚本用了 MySQL 专有函数 | 改写为 H2 兼容 SQL 或用条件迁移 |
| `java.lang.UnsupportedClassVersionError` | JDK 不是 21 | 确认 `JAVA_HOME` 指向 JDK 21（本机示例 `C:\Users\mjm13\.jdks\ms-21.0.10`） |
| 测试直接 GREEN（未见 RED） | 测试写错，可能在测 Mock 而非真实逻辑 | 删除实现代码，重新看 RED |
