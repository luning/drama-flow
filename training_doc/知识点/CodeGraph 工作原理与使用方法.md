# CodeGraph 工作原理与使用方法

## 是什么

CodeGraph 是一个以 **MCP Server** 形式接入 Claude Code 的代码智能索引工具。它预先分析整个代码库，把所有符号（函数、类、路由等）和它们之间的关系（调用、引用、继承等）存入本地 SQLite 数据库，让 Claude 可以在几毫秒内定位任意代码、追踪调用链、评估改动影响范围。

MCP（Model Context Protocol）是 Anthropic 定义的标准协议，任何工具实现该协议后 Claude 就能调用它。CodeGraph 作为 MCP Server 运行在本地，不需要联网。

项目根目录出现 `.codegraph/` 目录，说明该项目已被索引。

---

## 怎么用

在 Claude Code 中直接用自然语言提问，Claude 会自动调用 CodeGraph：

```
用户登录相关的逻辑是什么？
AuthRepository 调用了哪些方法？
修改 login 函数会影响哪些地方？
```

也可以通过 CLI 直接查询：

```bash
codegraph explore "login auth token"
```

### 与 grep 的对比

| | grep/find | CodeGraph |
|---|---|---|
| 能找到间接调用关系 | 否 | 是 |
| 返回源码（带行号） | 否 | 是 |
| 返回调用方/被调用方 | 否 | 是 |
| 查询速度 | 随文件数增长 | 固定快 |

一次查询同时返回：目标符号的完整源码 + 调用链（谁调它、它调谁）+ blast-radius 摘要（改动影响范围、有无覆盖测试）。grep 一次只能看一层，CodeGraph 一次全给你。

### 提升召回效果

CodeGraph 靠关键词匹配召回代码，关键词越准越全，结果越好：

- 直接给出多个同义词："login、authenticate、JWT token 相关逻辑"
- 告诉 Claude "用尽可能多的同义词搜索"

---

## 工作原理

### 整体架构

```
代码文件
   ↓  daemon 进程监听文件变动，增量解析（约 1 秒延迟）
.codegraph/codegraph.db（SQLite 知识图谱）
   ↓  查询时
FTS 倒排索引召回候选节点
   ↓
沿关系图向外扩展调用链
   ↓
从磁盘切出源码片段，返回给 Claude
```

### 数据库结构

**`files`**：文件索引控制表。daemon 靠比对 `content_hash` 判断文件是否需要重新解析，实现增量索引。

**`nodes`**：符号节点表。每个函数、类、方法、常量、路由都是一条记录，存储名字、所在文件、起止行号、签名、可见性等。`kind` 字段区分符号类型：

```
function | method | class | constant | field | import | namespace | component | route
```

`route` 是语义增强类型，把 HTTP 路由直接建模为节点：

```
route:POST /api/auth/login  →  AuthController.java 第 27 行
```

**`edges`**：关系图表。每条记录是两个节点之间的一条有向边：

| kind | 含义 |
|---|---|
| `contains` | 文件包含符号、类包含方法 |
| `calls` | 函数调用 |
| `references` | 变量/类型引用 |
| `imports` | import 语句 |
| `instantiates` | new 实例化 |
| `extends` | 继承 |

边上附有置信度：`{"confidence": 0.85, "resolvedBy": "import"}`。Python、JavaScript 这类动态语言无法 100% 静态分析，所以用置信度标注，而不是放弃。

### FTS 与倒排索引

FTS（Full-Text Search）对 `nodes` 的 `name`、`qualified_name`、`signature`、`docstring` 字段建倒排索引。

倒排索引把"文档 → 词"反转为"词 → 文档列表"：

```
正向：节点1 → [login, email, password]
      节点2 → [authenticate, email, token]

倒排：login        → [节点1]
      authenticate → [节点2]
      email        → [节点1, 节点2]
```

查询 "login" 时直接查字典，不扫描其他节点。排序用 BM25 算法：命中词越多、词越稀有的节点排越前。

**FTS 的限制**：只做词级别精确匹配。函数叫 `verify_credentials` 但 name/signature 里没有 "login"，FTS 就找不到它。

**补救机制是图遍历**：`login` 被 FTS 召回后，CodeGraph 沿 `edges` 找到它调用的 `verify_credentials`，把后者也带进结果。

### LLM 在查询中的位置

```
你的问题："用户登录相关的逻辑"
      ↓
Claude 将问题转化为关键词
      ↓
codegraph_explore(query="login auth token JWT")
      ↓  FTS + 图遍历返回源码
Claude 阅读源码，做语义理解，组织最终回答
```

**query 里的关键词由 Claude 决定**，不是你原话的直接透传。LLM 的作用是加深理解，不是扩大召回——FTS 没召回的节点，Claude 看不见。

---

## 配置方式

在 `~/.claude.json` 中注册为 MCP Server：

```json
{
  "mcpServers": {
    "codegraph": {
      "type": "stdio",
      "command": "codegraph",
      "args": ["serve", "--mcp"]
    }
  }
}
```

`stdio` 类型：Claude Code 启动时 fork 子进程，通过 stdin/stdout 交换 JSON-RPC 消息，完全在本地运行。

**Claude 如何知道这个工具的用途**：启动时发 `tools/list` 握手，codegraph 返回工具名、参数 schema 和详细描述（由 codegraph 自身维护）。Claude 靠这段描述理解能做什么。

**Claude 如何知道什么时候用它**：`~/.claude/CLAUDE.md` 里配置了优先级规则——看到 `.codegraph/` 目录先用 CodeGraph，再用 grep/find。tools/list 告诉 Claude 能做什么，CLAUDE.md 告诉 Claude 什么时候用。
