# Agent 自证正确 - 用可观测性与可测试性打通对象层反馈

## 目录

1. [两个支柱](#两个支柱)
2. [支柱一：可观测性——发生了什么](#支柱一可观测性发生了什么)
   - [日志（Logs）](#日志logs)
   - [指标（Metrics）](#指标metrics)
   - [追踪（Traces）](#追踪traces)
   - [不同场景下的实践](#不同场景下的实践)
3. [支柱二：可测试性——能否可靠验证](#支柱二可测试性能否可靠验证)
   - [测试边界：系统的接缝在哪里](#测试边界系统的接缝在哪里)
   - [测试稳定性：为什么 E2E 会抖动](#测试稳定性为什么-e2e-会抖动)
   - [降级策略：E2E 跑不起来时怎么办](#降级策略e2e-跑不起来时怎么办)
   - [测试范围地图：把边界写成文档](#测试范围地图把边界写成文档)
4. [避免人工搬运信息的设计模式](#避免人工搬运信息的设计模式)
5. [日志产出规范](#日志产出规范)
6. [反模式与检查清单](#反模式与检查清单)
7. [成熟度阶梯](#成熟度阶梯)

---

> 对象层反馈解决一个问题：**Agent 改了代码之后，它能不能自己知道对不对**——不需要人来粘贴日志、描述现象、手动联调确认。这依赖两样东西：系统能表达自身状态（可观测性），行为能被可靠验证（可测试性）。

---

## 两个支柱

```
对象层反馈
│
├── 支柱一：可观测性（Observability）
│   系统能否表达自身状态？
│   ├── 日志：发生了什么事件
│   ├── 指标：系统健康度趋势
│   └── 追踪：请求走了哪条路
│
└── 支柱二：可测试性（Testability）
    行为能否被可靠验证？
    ├── 测试边界：最小可独立测试的接缝在哪
    ├── 测试稳定性：同一测试能否稳定复现
    └── 覆盖范围：哪些行为已被验证，哪些靠人工
```

两者失效的症状相同：人被迫成为信息中转站。可观测性差，Agent 读不懂现象；可测试性差，Agent 改完无法自证正确——结果都是闭环断掉。

---

## 支柱一：可观测性——发生了什么

### 日志（Logs）

日志记录离散事件，回答"什么时候发生了什么"。

| 维度 | 低可观测性 | 高可观测性 |
|------|-----------|-----------|
| 内容 | `"error occurred"` | `"Drama not found: drama_id=999, user_id=42"` |
| 结构 | 纯文本，难以机器解析 | 结构化 JSON，含 timestamp/level/module |
| 完整性 | 吞掉异常（`except: pass`） | 完整 stack trace 输出到 stderr |
| 上下文 | 只有错误码 | 含请求参数、用户 ID、操作路径 |

### 指标（Metrics）

指标是时序聚合数据，回答"系统整体健康度如何"。关注点在应用本身，而不是 Agent 的行为：

- API 错误率、P99 响应时间
- 数据库慢查询频次
- 外部依赖（七牛云签名、第三方登录）的成功率
- 关键业务漏斗（登录成功率、播放启动成功率）

### 追踪（Traces）

追踪记录请求在系统内的完整调用链，回答"这个请求经历了哪些步骤、在哪里慢了/出错了"。即使不引入分布式追踪系统，用 `correlation_id` 把同一次请求的日志串联起来，效果已经够用：

```python
import contextvars
from uuid import uuid4

request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id")

@app.middleware("http")
async def inject_request_id(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid4()))
    request_id.set(rid)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response

# 所有日志自动附带 request_id，Agent 可以 grep 一个 ID 看完整链路
def log(event: str, **kwargs):
    print(json.dumps({"request_id": request_id.get(None), "event": event, **kwargs}))
```

### 不同场景下的实践

#### 后端 API：结构化日志

每条日志必须能单独被机器解析，不依赖上下文才能理解。

```python
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, module: str):
        self.module = module

    def info(self, event: str, **kwargs):
        self._log("INFO", event, **kwargs)

    def error(self, event: str, exc: Exception = None, **kwargs):
        payload = {"exc_type": type(exc).__name__, "exc_msg": str(exc)} if exc else {}
        self._log("ERROR", event, **payload, **kwargs)

    def _log(self, level: str, event: str, **kwargs):
        record = {
            "ts": datetime.utcnow().isoformat(),
            "level": level,
            "module": self.module,
            "event": event,
            **kwargs
        }
        print(json.dumps(record, ensure_ascii=False), flush=True)

logger = StructuredLogger("drama_service")

# ✅ 包含足够上下文，Agent 可自行定位
logger.info("fetch_drama", drama_id=42, user_id=7, cache_hit=False)
logger.error("drama_not_found", drama_id=999, exc=e)
```

API 错误响应同样需要结构化——它是 Agent 读到的最直接的失败信号：

```python
# ✅ Agent 可读
raise HTTPException(status_code=404, detail={
    "error_code": "DRAMA_NOT_FOUND",
    "drama_id": drama_id,
    "message": f"Drama {drama_id} does not exist or has been removed",
})

# ❌ Agent 无法定位
raise HTTPException(status_code=500, detail="Internal Server Error")
```

#### Android 客户端：分层日志

Android 日志散布在 UI 层、ViewModel、Repository、网络层，追踪问题需要跨层关联。统一日志入口可以保证格式一致、方便过滤。

```kotlin
object AppLogger {
    private const val TAG_PREFIX = "DramaFlow"

    fun d(module: String, event: String, vararg pairs: Pair<String, Any?>) {
        if (BuildConfig.DEBUG) Log.d("$TAG_PREFIX/$module", buildMessage(event, pairs))
    }

    fun e(module: String, event: String, throwable: Throwable? = null, vararg pairs: Pair<String, Any?>) {
        Log.e("$TAG_PREFIX/$module", buildMessage(event, pairs), throwable)
        throwable?.let { FirebaseCrashlytics.getInstance().recordException(it) }
    }

    private fun buildMessage(event: String, pairs: Array<out Pair<String, Any?>>): String =
        "[$event] ${pairs.joinToString(" ") { "${it.first}=${it.second}" }}"
}

// 播放器状态机：每次转换都记录，便于还原问题时序
override fun onPlaybackStateChanged(state: Int) {
    val stateName = when(state) {
        Player.STATE_IDLE -> "IDLE"
        Player.STATE_BUFFERING -> "BUFFERING"
        Player.STATE_READY -> "READY"
        Player.STATE_ENDED -> "ENDED"
        else -> "UNKNOWN($state)"
    }
    AppLogger.d("Player", "state_changed", "from" to previousState, "to" to stateName)
    previousState = stateName
}
```

#### H5/前端：全局错误捕获

前端错误发生在用户设备上，没有服务器日志，Agent 无法直接访问——必须主动上报。

```typescript
// main.ts
app.config.errorHandler = (err, instance, info) => {
  reportError({
    component: instance?.$options.name,
    lifecycle: info,
    route: router.currentRoute.value.path,
    error: String(err),
    stack: err instanceof Error ? err.stack : undefined,
  })
}

// axios 拦截器：网络错误统一上报
axiosInstance.interceptors.response.use(
  response => response,
  error => {
    reportError({
      event: 'api_error',
      url: error.config?.url,
      status: error.response?.status,
      body: error.response?.data,
    })
    return Promise.reject(error)
  }
)
```

只埋**状态转换和失败节点**，不要埋每个点击：

```typescript
trackEvent('drama_play_start', { drama_id: id, episode })
trackEvent('drama_play_error', { drama_id: id, error_code: code })
trackEvent('token_refresh_failed')
```

---

## 支柱二：可测试性——能否可靠验证

### 测试边界：系统的接缝在哪里

**接缝（Seam）**：系统中可以在不修改主体代码的情况下替换行为的地方。接缝是测试的立足点。

多模块系统跑 E2E 很难，根本原因往往是接缝不清晰——模块之间耦合太紧，无法单独启动某一层来验证。

```
耦合紧（接缝少）：
  Android App → 真实 API → 真实数据库 → 真实七牛云

接缝清晰：
  Android App
    └── [接缝：Repository 接口]
          ├── FakeRepository（测 ViewModel 逻辑）
          ├── MockWebServer（测网络层）
          └── 真实 API（E2E）
```

**DramaFlow 的主要接缝**：

| 接缝位置 | 可替换的内容 | 对应测试层级 |
|---------|------------|------------|
| Android Repository 接口 | FakeRepository | ViewModel 单元测试 |
| Android 网络层 | MockWebServer（OkHttp） | Repository 集成测试 |
| FastAPI 应用 | TestClient（httpx） | API 行为测试（pytest） |
| 数据库层 | SQLite in-memory | Service 层单元测试 |
| JSBridge | Mock window.DramaFlowBridge | H5 组件测试 |
| 七牛云签名 | 固定测试 URL | 播放器逻辑测试 |

### 测试稳定性：为什么 E2E 会抖动

```
环境依赖
├── 外部服务不可用（七牛云、第三方登录）
├── 设备/模拟器状态不一致（已登录 vs 未登录）
└── 端口冲突、进程残留

时序问题
├── 动画未完成就断言（Espresso 常见）
└── 网络请求未返回就断言

状态污染
├── 上一个测试的数据影响当前测试
└── 共享全局状态（单例、静态变量）

测试设计问题
├── 断言不精确（等待"任意元素"而非"特定元素"）
└── 测试之间有隐式顺序依赖
```

提升稳定性的设计原则：

- **每个测试自带数据，自己清理**——不依赖其他测试产生的副作用
- **隔离外部依赖**——能 mock 的外部服务不要真的调用
- **等行为不等时间**——用条件等待而不是 `sleep(2000)`

```python
# pytest：每个测试用独立事务，结束后回滚
@pytest.fixture
def db_session():
    session = SessionLocal()
    session.begin_nested()   # savepoint
    yield session
    session.rollback()
    session.close()
```

### 降级策略：E2E 跑不起来时怎么办

E2E 覆盖最全，但成本最高、最脆。不可行时向内退一层，找最近的稳定接缝——而不是放弃测试。

```
1. E2E（全链路）
   适用：核心用户旅程，如"登录 → 首页 → 播放"
   障碍：需要启动所有服务，依赖真实设备/网络

   ↓ 降级

2. API 行为测试（pytest + TestClient）
   适用：业务逻辑、数据流转、权限控制
   优点：纯 Python 环境，无需 Android 或 H5

   ↓ 降级

3. 模块隔离测试（单层，依赖替换）
   适用：ViewModel 逻辑、Service 计算、Store 状态
   优点：毫秒级执行，无环境依赖

   ↓ 降级

4. 手动验收（明确记录，不假装已自动化）
   适用：真机特有行为、视频播放质量
   要求：在测试范围地图中标注为"手动"，写清复现步骤
```

降级不是失败，但必须**有意识**——知道自己在哪一层，知道这一层覆盖不到什么。最危险的状态是既没有 E2E，又误以为 API 测试覆盖了一切。

### 测试范围地图：把边界写成文档

显式记录每个功能可以在哪一层被验证、是否稳定、哪些只能手动。Agent 选验证策略时会优先查阅，而不是盲目尝试 E2E 后因环境问题失败。

维护在 `SPEC.md` 或单独的 `TEST-MAP.md`：

```markdown
| 功能 | API 自动化 | 端到端 | 手动场景 |
|------|-----------|--------|---------|
| 用户登录 | ✅ pytest | ⚠️ 脆 | 真机首次安装 |
| 首页剧集列表 | ✅ pytest | ✅ Cypress | — |
| 视频播放 | ❌ | ❌ | ✅ 码率切换、缓冲行为 |
| 续看进度保存 | ✅ pytest | ✅ Cypress | — |
| Token 刷新 | ✅ pytest | ⚠️ 需构造过期 token | — |
| JSBridge 通信 | ❌ | ❌ | ✅ H5 → App 跳转 |

⚠️ = 可以跑，但不纳入 CI
```

---

## 避免人工搬运信息的设计模式

### 错误自带上下文

```python
# ❌ 人需要去查数据库
raise HTTPException(status_code=404, detail="Not found")

# ✅ 错误消息直接包含足够信息
raise HTTPException(status_code=404, detail={
    "error_code": "DRAMA_NOT_FOUND",
    "drama_id": drama_id,
    "message": f"Drama {drama_id} does not exist or has been removed",
})
```

### 测试失败信息自带请求上下文

```python
def assert_success(response, expected_status=200):
    assert response.status_code == expected_status, (
        f"Expected {expected_status}, got {response.status_code}\n"
        f"URL: {response.url}\n"
        f"Request: {response.request.body}\n"
        f"Response: {response.json()}"
    )
```

### 状态快照文件

周期性写入系统状态，让 Agent 可以直接读取而不需要人来描述当前情况：

```python
async def write_health_snapshot():
    snapshot = {
        "ts": datetime.utcnow().isoformat(),
        "db_connection": await check_db(),
        "active_sessions": len(session_store),
        "recent_errors": error_ring_buffer.to_list(),
    }
    Path(".health_snapshot.json").write_text(json.dumps(snapshot, indent=2))
```

---

## 日志产出规范

### 必须记录的事件

| 场景 | 必须记录的事件 | 关键字段 |
|------|--------------|---------|
| API 请求 | 每次请求的完成 | method, path, status, duration_ms |
| 认证 | 登录、登出、token 刷新成功/失败 | user_id, reason（失败时） |
| 业务关键路径 | 购买、播放开始 | user_id, drama_id |
| 异常 | 所有未捕获异常 | exc_type, exc_msg, stack_trace |
| 状态机转换 | 播放器状态变化、登录态变化 | from, to, trigger |
| 外部调用 | 第三方 API、CDN 签名 | service, endpoint, duration_ms, success |

### 禁止记录的信息

```
❌ 用户密码（明文或加密）
❌ access_token / refresh_token 完整值
❌ 身份证号、信用卡号等 PII
❌ 七牛云 secretKey

✅ 需要时只记录脱敏版本
logger.info("token_refreshed", user_id=42, token_prefix=token[:8] + "...")
```

### 日志级别约定

| 级别 | 使用场景 |
|------|---------|
| DEBUG | 开发调试，默认关闭（缓存命中/未命中、SQL 参数） |
| INFO | 正常业务的关键节点（登录、播放开始） |
| WARNING | 非预期但不影响功能（token 即将过期、降级触发） |
| ERROR | 功能受损，需要关注（数据库连接失败、第三方超时） |
| CRITICAL | 系统级故障，需立即响应（数据库不可用） |

### 日志格式（后端）

```json
{
  "ts": "2026-05-21T10:23:45.123Z",
  "level": "ERROR",
  "module": "drama_service",
  "event": "drama_not_found",
  "request_id": "req-abc123",
  "user_id": 42,
  "drama_id": 999,
  "exc_type": "DramaNotFoundError",
  "exc_msg": "Drama 999 does not exist"
}
```

---

## 反模式与检查清单

### 可观测性反模式

```python
# ❌ 静默吞异常
try:
    result = fetch_drama(drama_id)
except Exception:
    pass

# ❌ 模糊错误信息
raise Exception("Failed")

# ❌ 非结构化文本日志
print(f"[{datetime.now()}] Something happened in drama service")

# ❌ 前端错误只在控制台显示，没有上报
console.error("API Error:", err)
```

### 可测试性反模式

```python
# ❌ 测试依赖外部服务（七牛云、微信登录）
# 外部服务不可用 → 测试挂 → 无法区分是业务逻辑问题还是网络问题

# ❌ 测试之间有顺序依赖
def test_b():
    response = client.get("/api/dramas/1")  # 隐式依赖 test_a 插入了 id=1

# ❌ 用 sleep 等待异步操作
time.sleep(2)

# ❌ 测试范围没有文档，误以为"有测试"等于"已验证"
```

### 对照检查清单

**可观测性**：
- [ ] 所有 `except` 块是否都有日志输出？
- [ ] 日志是否包含足够的上下文（ID、参数）？
- [ ] API 错误响应是否有结构化的 error_code？
- [ ] 前端是否有全局错误捕获和上报？
- [ ] 状态机的每次转换是否有记录？

**可测试性**：
- [ ] 是否知道每个模块的测试接缝在哪里？
- [ ] 测试是否依赖外部服务（如果是，是否有 mock）？
- [ ] 测试是否自带数据、自己清理？
- [ ] 是否有测试范围地图，标注哪些场景只能手动验证？
- [ ] CI 中的测试是否稳定（连续三次运行结果一致）？

---

## 成熟度阶梯

| 阶段 | 可观测性 | 可测试性 | Agent 能做什么 |
|------|---------|---------|--------------|
| **L0** | 靠 print 调试，生产无记录 | 无自动化，全靠手动 | 完全依赖人 |
| **L1** | 有日志，但非结构化 | 有测试，但抖动严重 | 能读日志但误报多；测试结果不可信 |
| **L2** | 结构化日志，含必要上下文 | API 层有稳定的自动化测试 | 可定位错误，可自行验证修复 |
| **L3** | 完整三支柱（日志+指标+追踪） | 多层测试，有测试范围地图 | 可主动发现异常，验证范围清晰 |
| **L4** | 闭环自愈 | 测试即文档，Agent 能自选策略验证 | 常见故障和修复无需人工介入 |

**最小可行目标：L2**——结构化日志让 Agent 读懂系统状态，稳定的 API 测试让 Agent 能自证修复正确。低于 L2，Agent 就只是代码生成器，验证环节仍然完全依赖人。
