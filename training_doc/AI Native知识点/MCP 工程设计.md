# MCP 工程设计 - 把外部系统变成 AI 可信赖的工具箱

## 什么是 MCP？

MCP（Model Context Protocol）是 Anthropic 提出的开放标准协议，本质是 **JSON-RPC 2.0 消息格式 + stdio 传输层**。它让 AI 能以统一接口调用外部工具和数据源。

---

## MCP 的三种原语

协议定义了三种 Server 可暴露的内容类型，称为**原语（primitives）**。

| 原语 | 谁控制调用时机 | 协议方法 |
|------|--------------|---------|
| **Tools** | 模型 | `tools/list` → `tools/call` |
| **Resources** | 宿主程序 | `resources/list` → `resources/read` (支持 `subscribe` 推送变更) |
| **Prompts** | 用户 | `prompts/list` → `prompts/get` |

---

## 设计初衷：LLM 作为传统程序的推理组件

三种原语的划分，不是为 Agent 设计的。MCP 最初面向的是**非 Agent 的宿主程序**——LLM 只是流程中负责推理的一环，宿主控制全局：

| 角色 | 谁做 | MCP 原语 |
|------|------|---------|
| 提供上下文 | 宿主（本来就知道用户是谁、在看什么） | Resources |
| 选择流程 | 用户（知道自己要干什么） | Prompts |
| 执行操作 | 模型提议，宿主确认后执行 | Tools |

### 真实场景：客服工单系统的 AI 辅助回复

工单系统（如 Intercom）的客服点击"智能回复"：

**① Resources — 宿主把已有数据直接喂给模型**

```
resources/read "customer://ticket-5542"     → 客户姓名、套餐、MRR
resources/read "customer://ticket-5542/chat" → 完整聊天记录
resources/read "knowledge://faq-billing"     → 计费 FAQ
```

宿主不等待模型来问——"查这个工单的数据"是它发起请求前就确定的。

**② Prompts — 用户从模板中选择操作类型**

```
prompts/list → ["回复客户", "升级主管", "推荐FAQ"]
客服选"回复客户"
prompts/get "reply-customer" →
  "你是客服{agent}。回复{客户}({套餐},${MRR}/月)。
   语气{tone}。参考FAQ: {faq}。对话: {chat}"
```

宿主拿 ① 的数据填入模板占位符，拼成最终 prompt 发给 LLM。

**③ Tools — 模型建议操作，人工确认后执行**

```
LLM 返回: "您好…建议发放 FIX50 优惠券安抚客户"
         [tool_suggestion: apply_coupon(customer=5542, coupon="FIX50")]

宿主弹出确认框 → 客服点确认
tools/call "apply_coupon" → ✅ 优惠券已发放
```

LLM 只是流水线中的推理组件，不是自主 Agent。

---

## Agent 场景：为什么通常只用 Tool

当宿主换成 Claude Code 这样的 Agent 时，编排职责被 LLM 自身接管：

```
传统宿主              Agent 的替代
────────────────     ──────────────────
读 Resources          → Agent 内核管理上下文（文件、git 等）
选 Prompts           → system prompt + slash 命令 + skill
调 Tools（模型建议）   → ⚠ 仍需要 MCP——外部系统 Agent 无法内建
```

Resources 和 Prompts 的编排角色已被 Agent 自身替代。**只有 Tool 在 Agent 场景下不可替代**——外部数据库、内部 API、第三方服务无法"内建"。

因此，MCP 在实践中几乎等同于 **Tool 调用协议**。

---

## Skill vs MCP：选型指南

| 维度 | Skill | MCP |
|------|-------|-----|
| 本质 | 注入 Claude 系统提示的**指令** | 外部进程暴露的**函数** |
| 作用 | 改变**怎么想**（工作流、规则） | 增加**能做什么**（查数据、调接口） |
| 是否引入新工具 | 否（只引导使用已有工具） | 是（提供新的可调用函数） |
| 跨平台 | 仅 Claude Code | Claude Code / Cursor / 自建 Agent |
| 适合 | 流程编排、规范固化、本地工具 | 外部系统集成、权限管控、跨平台复用 |

两者可组合：Skill 编排流程，调用 MCP Tool 完成数据访问。

---

## MCP Server 设计原则

### 1. Tool 描述比代码重要

模型只能通过 `description` 和 `inputSchema` 判断是否调用某个 Tool，描述要写明**干什么、何时用、参数含义**。

```python
# 差
@server.tool("query")  # 模型不知道什么时候该调
async def query(sql: str) -> str: ...

# 好
@server.tool("get_user_points")
async def get_user_points(user_id: int) -> str:
    """查询用户积分余额。当用户询问积分、余额时调用。"""
```

### 2. 返回值要让模型能消化

模型根据返回值做下一步决策——它不能消化原始数据库行，也不能从技术栈里推断原因。

```python
# 差：模型看不懂
return "(1023, 2350, 2024-01-15)"
raise Exception("mysql.connector.errors.DatabaseError: ...")

# 好：结构化 JSON + 语义化错误码
return json.dumps({"user_id": 1023, "balance": 2350, "status": "normal"})
return json.dumps({"error": "USER_NOT_FOUND", "message": "用户不存在，请确认 ID"})
```

语义化错误码（`USER_NOT_FOUND`、`INSUFFICIENT_PERMISSION`）让模型能判断下一步该追问用户还是尝试其他工具。

### 3. 接口防误用

MCP 是 AI 访问外部系统的入口，暴露得越少越安全：

- **不接受原始 SQL**，只接受结构化参数
- **数据库用只读账号**兜底
- **读 Tool 和写 Tool 分开**，写操作需确认机制
- **敏感字段脱敏**，不暴露手机号等个人数据

```python
# 差：整个数据库暴露给 AI
@server.tool("query_db")
async def query_db(sql: str) -> str: ...

# 好：固定查询逻辑，参数化接口
@server.tool("get_order_status")
async def get_order_status(order_id: int) -> str: ...
```

---

## 实战案例：积分商城 MCP

将积分商城的 MySQL 数据库以受控方式暴露给运营和开发，让 AI 可查积分、订单、库存，不给原始数据库权限。

```
src/mcp/
  server.py
  tools/
    points.py     # 查余额、查明细
    products.py   # 查库存
    orders.py     # 查订单状态
  db.py           # 只读连接
```

项目根目录 `.mcp.json`：

```json
{
  "mcpServers": {
    "pointshub": {
      "type": "stdio",
      "command": "python",
      "args": ["./src/mcp/server.py"],
      "env": { "DATABASE_URL": "mysql+pymysql://readonly:pass@localhost/pointshub" }
    }
  }
}
```

| Tool | 参数 | 用途 |
|------|------|------|
| `get_user_points` | `user_id: int` | 查询积分余额 |
| `get_points_history` | `user_id: int, limit: int = 10` | 查询积分流水 |
| `check_product_stock` | `product_id: int` | 查询商品库存 |
| `get_order_status` | `order_id: int` | 查询订单状态 |

调用效果：

```
用户：查一下用户 1023 的积分，他投诉积分少了

→ get_user_points(1023)          → 余额 2,350
→ get_points_history(1023, 10)   → 签到 +10, 兑换 -500 …

余额与明细一致，未发现异常。建议核实是否混淆账号。
```

---

## 企业级 MCP

| 层级 | 范围 | 示例 |
|------|------|------|
| 个人 | 个人工具 | 本地开发库调试 Server |
| 项目 | 项目业务系统 | 积分商城 `pointshub-mcp` |
| 企业 | 跨项目通用系统 | 连接 ERP / CRM 的统一 Server |

企业级 MCP 独立仓库维护，接口变更视为 Breaking change，需通知所有接入方。
