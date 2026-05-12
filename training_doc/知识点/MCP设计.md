# MCP 深度设计

## 目录

1. [什么是 MCP？](#什么是-mcp)
2. [MCP 的三大能力](#mcp-的三大能力)
   - [Tools（工具）](#tools工具)
   - [Resources（资源）](#resources资源)
   - [Prompts（提示模板）](#prompts提示模板)
3. [MCP Server 项目结构](#mcp-server-项目结构)
4. [在 Claude Code 中配置与调用](#在-claude-code-中配置与调用)
   - [配置 MCP Server](#配置-mcp-server)
   - [调用效果演示](#调用效果演示)
   - [本地调试](#本地调试)
5. [四大设计原则](#四大设计原则)
   - [权限最小化](#权限最小化)
   - [返回值可解析](#返回值可解析)
   - [错误信息面向 AI](#错误信息面向-ai)
   - [幂等性与无副作用（只读 Tool）](#幂等性与无副作用只读-tool)
6. [课程案例：积分商城 MCP 复盘](#课程案例积分商城-mcp-复盘)
   - [`pointshub-mcp` Server](#pointshubmcp-server)
7. [CLI Skill vs MCP Server 选型（扩展版）](#cli-skill-vs-mcp-server-选型扩展版)
8. [企业级 MCP 体系](#企业级-mcp-体系)
   - [三层分级](#三层分级)
   - [版本管理建议](#版本管理建议)
   - [安全运营建议](#安全运营建议)

---

## 什么是 MCP？

MCP（Model Context Protocol）是 Anthropic 提出的开放标准协议，让 AI Agent 以统一接口访问外部工具和数据源——无论后端是数据库、内部 API、文件系统还是第三方服务。

调用方式：在 `settings.json` 中配置 MCP Server 后，Claude 在对话中可以像调用内置工具一样调用 MCP 暴露的 Tools，无需用户显式触发。

**MCP 与 Skill 的本质区别**：Skill 是给 Claude 的"指令书"（提示词 + 规则），Claude 读完后自己决定怎么做；MCP 是给 Claude 的"工具箱"（确定性 API），Claude 决定什么时候调、调哪个，工具本身不含推理逻辑。

**适合封装成 MCP Server 的场景**：

| 适合 | 不适合 |
|------|--------|
| 需要跨 Agent 平台复用的工具（Claude Code / Cursor / 自建 Agent 都要用）| 只在 Claude Code 内部使用的流程编排 |
| 访问外部系统（数据库、内部 API、文件存储）且需要权限管控 | 纯提示词驱动的推理任务 |
| 工具逻辑已稳定，不需要 AI 介入执行细节 | 工具逻辑本身还需要 Claude 大量推理判断 |
| 需要对 AI 的系统访问做审计 / 限流 / 权限隔离 | 一次性任务，不会重复使用 |

**何时 Skill 就够用，不需要 MCP**：

| 场景 | 推荐 |
|------|------|
| 只有开发团队用 Claude Code | Skill 够用 |
| 流程有推理步骤（根据上下文决定做什么）| Skill |
| 工具需要运营 / 客服 / PM 等非开发角色使用 | MCP 更合适 |
| 同一工具要在多个 AI 平台上使用 | MCP |
| 需要限制 AI 只能访问特定数据视图 | MCP |

---

## MCP 的三大能力

### Tools（工具）

AI 可以调用、有副作用的函数。这是 MCP 最核心的能力。

```python
@server.tool("get_user_points")
async def get_user_points(user_id: int) -> str:
    """查询指定用户的积分余额"""
    balance = await db.query_points(user_id)
    return f"用户 {user_id} 当前积分：{balance}"
```

Tool 的设计原则：
- **单一职责**：一个 Tool 只做一件事，名称即契约
- **参数最小化**：只暴露必要参数，复杂查询条件做成枚举而非自由文本
- **返回值结构化**：返回 JSON 或固定格式文本，让 Claude 能可靠解析
- **读写分离**：只读 Tool（查询）和写入 Tool（修改数据）分开，便于权限控制

### Resources（资源）

AI 可以读取但不能修改的数据，用于给 Claude 注入上下文。

```python
@server.resource("spec://pointshub/orders")
async def get_order_spec() -> str:
    """暴露订单模块的 SPEC.md 作为上下文资源"""
    return open("docs/SPEC.md").read()
```

Resources 适合将以下内容暴露给 Claude：
- 项目规格文档（SPEC.md、API 文档）
- 业务规则手册（积分规则、活动配置）
- 系统状态快照（当前环境配置、部署版本）

### Prompts（提示模板）

预定义的提示词模板，让 Claude 进入特定工作模式。

```python
@server.prompt("diagnose-points-issue")
async def diagnose_points_prompt(user_id: str) -> str:
    return f"""
    你是积分系统的诊断专家。请分析用户 {user_id} 的积分异常问题：
    1. 先调用 get_user_points 查询当前余额
    2. 再调用 get_points_history 查询最近 20 条流水
    3. 对比余额与流水合计，判断是否存在数据一致性问题
    4. 给出可能的根因和排查步骤
    """
```

Prompts 适合将高频诊断 / 分析流程固化，让非技术人员也能触发标准化的 AI 分析流程。

---

## MCP Server 项目结构

```
mcp/
  server.py          # MCP Server 主文件：注册 Tools / Resources / Prompts
  tools/
    points.py        # 积分相关 Tools（查余额、查明细）
    products.py      # 商品相关 Tools（查库存、查详情）
    orders.py        # 订单相关 Tools（查状态）
  resources/
    spec.py          # 暴露 SPEC.md 等文档资源
  db.py              # 数据库连接池（与业务后端共享连接配置）
  requirements.txt   # mcp, sqlalchemy, pymysql 等
```

**渐进式披露原则**：从最常用的 1–2 个 Tool 开始，验证集成效果后再扩展。不要一次性暴露所有数据表。

---

## 在 Claude Code 中配置与调用

### 配置 MCP Server

在项目根目录的 `.claude/settings.json` 中添加：

```json
{
  "mcpServers": {
    "pointshub": {
      "command": "python",
      "args": ["./mcp/server.py"],
      "env": {
        "DATABASE_URL": "mysql+pymysql://user:pass@localhost/pointshub"
      }
    }
  }
}
```

配置生效后，Claude 在对话中可以直接调用 MCP 暴露的 Tools，无需用户显式指令。

### 调用效果演示

**场景：运营人员查询用户积分问题**

```
用户：查一下用户 ID 为 1023 的积分余额，他投诉说积分少了

Claude：我来帮您查一下。
[调用 get_user_points(user_id=1023)]
用户 1023 当前余额：2,350 积分

[调用 get_points_history(user_id=1023, limit=10)]
最近 10 条流水：
- 2024-01-15 消费兑换 -500积分
- 2024-01-14 签到奖励 +10积分
...

根据流水记录，余额与明细一致，未发现异常扣减。
建议：核实用户是否混淆了不同账号，或查看是否有未同步的离线操作。
```

### 本地调试

```bash
# 启动 MCP Server（保持后台运行）
python mcp/server.py

# 验证 Tool 可调用（使用 MCP Inspector）
npx @modelcontextprotocol/inspector python mcp/server.py
```

---

## 四大设计原则

### 权限最小化

MCP Server 是 AI 访问生产系统的入口，必须严格控制暴露范围：

- **只读 vs 读写分离**：绝大多数场景只需只读 Tool；写入 Tool 需要额外的确认机制
- **视图而非原表**：查询 MySQL 视图（`CREATE VIEW user_points_view AS ...`），而非直接 SELECT 业务表
- **参数白名单**：Tool 参数不接受原始 SQL 片段，只接受结构化参数

```python
# 差：允许 AI 拼接任意查询
async def query_db(sql: str) -> str: ...

# 好：固定查询逻辑，只暴露参数化接口
async def get_user_points(user_id: int) -> str: ...
```

### 返回值可解析

Claude 需要根据 Tool 返回值做决策，返回值必须语义清晰：

```python
# 差：返回原始数据库 Row
return str(row)  # "(1023, 2350, 2024-01-15)"

# 好：返回结构化 JSON 或自然语言描述
return json.dumps({
    "user_id": 1023,
    "balance": 2350,
    "last_updated": "2024-01-15",
    "status": "normal"
})
```

### 错误信息面向 AI

Tool 抛出异常时，错误信息要让 Claude 能判断下一步：

```python
# 差：技术错误栈
raise Exception("mysql.connector.errors.DatabaseError: ...")

# 好：语义化错误
return {"error": "USER_NOT_FOUND", "message": f"用户 {user_id} 不存在，请确认 ID 是否正确"}
```

### 幂等性与无副作用（只读 Tool）

只读 Tool 必须保证：
- 同一参数多次调用，结果相同（无缓存不一致问题）
- 不触发任何业务逻辑（不写日志、不更新 last_access_time 等）
- 超时后可以安全重试

---

## 课程案例：积分商城 MCP 复盘

### `pointshub-mcp` Server

**目的**：将积分商城的 MySQL 数据库以受控方式暴露给 AI Agent，用于运营查询和开发调试，而无需给 AI 原始数据库权限。

**实现的 Tools**：

| Tool | 参数 | 用途 |
|------|------|------|
| `get_user_points` | `user_id: int` | 查询用户积分余额 |
| `get_points_history` | `user_id: int, limit: int = 10` | 查询积分明细流水 |
| `check_product_stock` | `product_id: int` | 查询商品库存 |
| `get_order_status` | `order_id: int` | 查询订单状态 |

**实现的 Resources**：

| Resource | 内容 |
|---------|------|
| `spec://pointshub/orders` | 订单模块 SPEC.md（AC 和业务规则）|

**设计亮点**：
- 所有 Tool 只读，不暴露任何写入接口，AI 无法通过 MCP 修改积分数据
- 连接数据库用只读账号（MySQL `GRANT SELECT ON ...`），从数据库层双重保证
- 返回值统一为 JSON，Claude 解析可靠

**可以改进的地方**：
- 目前缺少分页支持，`get_points_history` 数据量大时返回值会很长，应加 `offset` 参数
- 可以增加一个 `diagnose-points-issue` Prompt，将高频诊断流程固化，运营人员一句话触发

---

## CLI Skill vs MCP Server 选型（扩展版）

| 维度 | CLI Skill | MCP Server |
|------|-----------|------------|
| 本质 | 给 Claude 的"指令书" | 给 Claude 的"工具箱" |
| 适用场景 | 确定性流程编排，本地工具调用 | 外部系统集成，跨平台生态对接 |
| 部署方式 | 项目目录内，随代码版本管理 | 独立进程，需要单独部署维护 |
| 调用方式 | `/skill-name` 显式触发 | Tool Call，对用户透明 |
| 推理介入程度 | 高（Claude 决策执行细节）| 低（确定性 API，Claude 只决定调用时机）|
| 权限管控 | 通过 `settings.json` 的 allow 列表 | 通过 MCP Server 内部逻辑精确管控 |
| 跨平台复用 | 仅 Claude Code | Claude Code / Cursor / 自建 Agent 均可用 |
| 适合团队 | 小团队，快速迭代，规范还在形成中 | 中大型团队，已有稳定内部系统需要接入 |

**选型口诀**：
- 流程编排、本地工具、Claude Code 独用 → Skill
- 系统集成、权限管控、跨平台复用 → MCP
- 两者不互斥，复杂场景可以组合：Skill 编排高层流程，调用 MCP Tool 完成具体的数据访问

---

## 企业级 MCP 体系

### 三层分级

| 层级 | 适用范围 | 示例 |
|------|---------|------|
| **个人 MCP** | 个人数据库 / 个人工具 | 连接本地开发数据库的调试 Server |
| **项目 MCP** | 当前项目的业务系统 | 积分商城的 `pointshub-mcp` |
| **企业 MCP** | 跨项目通用系统 | 连接 ERP / CRM / 日志系统的统一 Server |

### 版本管理建议

- 企业级 MCP Server 作为独立 Git 仓库维护，语义化版本号（semver）
- Tool 接口变更（参数或返回值结构变化）视为 Breaking change，升大版本
- MCP Server 的 API 变更要同步通知所有接入方（因为多个 Agent 平台可能依赖同一 Server）

### 安全运营建议

- MCP Server 单独部署，不与业务后端共用进程（隔离故障影响）
- 生产环境 MCP 只读账号 + IP 白名单
- 记录每次 Tool 调用的 `user_id`、时间戳、参数（可审计）
- 敏感字段（手机号、身份证）在 MCP 返回值中脱敏处理
