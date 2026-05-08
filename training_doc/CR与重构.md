# CR 与重构方法论

> **为什么 AI 时代反而更需要 CR + 重构？**
> AI 生成代码的速度是传统开发的 10 倍，技术债的积累速度也是 10 倍。没有 CR + 重构节奏，代码库会在不知不觉中变成 AI 无法理解自己写过的东西的迷宫。

---

## 一、CR 的触发时机与节奏

**不要等问题出现才触发 CR。** CR 是主动节奏，不是被动救火。

```
Day 1
  迭代 1 开发结束 → CR + 重构（4.6）
      ↓ 发现 AI 高频错误，记入 CLAUDE.md，防止下次重犯

Day 2 上午
  迭代 2 开发结束 → CR + 重构（6.6）
      ↓ 两轮代码积累后，跨模块模式浮现，系统性清理

Day 2 下午
  迭代 3（需求改造）结束 → CR + 重构（8.5）
      ↓ 区分"需求变更债"vs"新功能债"，分别处置
```

> 每次迭代结束做一次 CR，是避免"还不如重写"的最低成本路径。

---

## 二、AI 高频错误模式（找什么）

这五类问题在 AI 生成的代码中出现频率最高，CR 时优先扫描：

### 1. 重复逻辑
同一段逻辑在不同地方出现了两次或更多次，通常是 AI 不知道之前已经写过了。

```python
# ❌ AI 在两个 service 里都写了同样的 token 校验逻辑
class DramaService:
    def get_drama(self, token: str):
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        ...

class WatchService:
    def record_progress(self, token: str):
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])  # 重复
        ...

# ✅ 提取到 auth 中间件或 get_current_user dependency
```

**提问框架**：`扫描这个模块，找出逻辑重复的片段，按相似度排序。`

### 2. 状态泄漏
跨请求的状态被意外共享，尤其是类级别的可变属性、全局变量。

```python
# ❌ class-level 可变默认值，所有实例共享同一个列表
class RecommendService:
    cache = []  # 意外的类变量共享状态

# ✅ 实例变量
class RecommendService:
    def __init__(self):
        self.cache = []
```

**提问框架**：`检查这个文件里是否有跨请求共享的可变状态，特别是类变量和全局变量。`

### 3. 命名混乱
AI 在不同地方用不同风格命名同一概念，或名字与实际行为不符。

```python
# ❌ 同一概念三种叫法
get_drama_list()   # 某个 service
fetch_dramas()     # 某个 api route
load_all_dramas()  # 某个 repository

# ❌ 名字说一件事，做另一件事
def validate_token(token):
    user = db.get_user(token)
    user.last_seen = datetime.now()  # 意外副作用
    db.save(user)
    return user
```

**提问框架**：`扫描这个模块的函数/变量命名，找出：1) 同一概念的不一致命名；2) 名字与实现不符的函数。`

### 4. 不遵循约定架构
AI 有时会跳过中间层（如 Service 层直接操作 ORM），违反 CLAUDE.md 中定义的架构约束。

```python
# ❌ API 路由层直接查数据库，跳过 Service 层
@router.get("/dramas")
def get_dramas(db: Session = Depends(get_db)):
    return db.query(Drama).filter(Drama.is_active == True).all()

# ✅ 通过 Service 层
@router.get("/dramas")
def get_dramas(drama_service: DramaService = Depends()):
    return drama_service.get_active_dramas()
```

**提问框架**：`对照 CLAUDE.md 中的架构约束，找出这个模块中直接跨层调用的地方。`

### 5. 啰嗦的注释或实现

AI 倾向于在每个函数前加大段注释，或写出"教材感"的冗长实现——在实际项目中是噪音。

```python
# ❌ AI 加的无用注释
# This function gets the drama by id
# Parameters:
#   - drama_id: the id of the drama
# Returns:
#   - the drama object
def get_drama(drama_id: int):
    ...

# ✅ 名字即文档，有注释也只写"为什么"而非"是什么"
def get_drama(drama_id: int):
    ...
```

---

## 三、重构线索的提问框架

一次完整的 CR 扫描可以用以下提问拆解：

```
1. 全局扫描（找问题）
   "对 backend/app/ 目录做 CR，输出以下分类的问题清单：
    - 重复逻辑（可复用但未复用的代码片段）
    - 状态管理风险（类变量/全局变量）
    - 命名一致性（同一概念不同叫法）
    - 架构违规（跳过层的直接调用）
    - 测试盲区（无任何测试覆盖的关键路径）
    按影响范围排序，只列出有实际风险的，不需要风格偏好。"

2. 聚焦确认（定优先级）
   "从上面的清单中，哪 2-3 条在现有测试的保护下可以安全重构？
    哪些需要先补测试再动？哪些可以接受暂不处理？"

3. 执行重构（保持行为不变）
   [见下一节]
```

---

## 四、保持行为不变的重构提示词

重构的铁律：**不改功能，只改结构。** 用提示词明确边界，防止 AI 顺手改了逻辑：

```
重构提示词模板：

"重构 [目标函数/模块]，目标是 [提取重复逻辑/改善命名/分离职责]。
 约束：
 1. 不修改任何业务逻辑和返回值格式
 2. 保持所有已通过的 pytest 用例继续通过
 3. 不引入新的依赖
 4. 每次只改一个地方，改完后告诉我下一步

 先告诉我你的重构计划，我确认后再执行。"
```

**为什么要"先告诉我计划"**：AI 重构时有时会"顺手"修改逻辑，或修改多处造成难以 review 的大 diff。强制分步可控。

**验证不变**：重构完成后立即跑测试：

```bash
source backend/drama-flow/bin/activate
pytest backend/tests/ -v
```

如果有测试失败，立刻回滚，不要继续重构其他地方。

---

## 五、重构 vs 重写：判断标准

| 情形 | 判断 | 理由 |
|------|------|------|
| 逻辑正确，只是结构混乱 | **重构** | 行为有保障，改结构成本低 |
| 逻辑本身有缺陷（设计错了）| **重写** | 修修补补只会更乱 |
| 测试覆盖率低，改动风险高 | **先补测试再重构** | 没有安全网不要动 |
| 影响 3+ 个模块，改动范围大 | **重写（局部）+ 迁移策略** | 分步替换，不整块推倒 |
| 下个迭代会大改这部分 | **接受技术债，先不动** | 成本不合算 |

**"还不如重写"的信号**：
- 读懂现有代码的时间 > 重写时间
- 每次改一处，三处跟着报错
- 测试无法覆盖，因为耦合太紧

---

## 六、技术债分类：接受 vs 立即修复

不是所有技术债都要立即还。尤其在迭代 3（需求改造）后，需要区分两类债：

```
需求变更引入的债（接受优先）：
  - 旧的实现路径因新需求而失效，留着旧代码没人用了
  - 改造过程中临时引入的"桥接"逻辑
  → 在注释中标 # TODO: cleanup after v1.1，或加 ADR 说明
  → 下个迭代开始前统一清理

新功能引入的债（立即修复优先）：
  - 新代码复制了已有逻辑，不是旧的被废弃了
  - 新功能绕过了架构层（直接操作 DB）
  - 新功能引入了全局状态
  → 这是设计问题，在本迭代 CR 时处理，不能留
```

> **判断原则**：技术债如果会"传染"下一个功能点，立即还；如果只是孤立的旧代码，可以标记后计划清理。

---

## 七、三种 CR 工具的选择

| 工具 | 适用场景 | 特点 |
|------|---------|------|
| **`cr-refactor` Skill** | 快速扫描，先看再决定改什么 | 输出 CR 清单 + 重构建议，参数只需路径，自动定位问题 |
| **`gsd:code-review`** | 知道要改什么，但步骤复杂、跨多文件 | 系统化、阶段化执行框架，适合"明确方向后的大范围重构" |
| **`requesting-code-review`（Superpowers Skill）** | 需要独立视角复查，防止自我确认偏差 | 派出独立子 Agent 审查，适合在合入主分支前做最后把关 |

**简单判断**：

```
"不确定哪里有问题，先扫一眼" → cr-refactor
"知道要大范围重构，需要分步执行" → gsd:code-review
"改完了，要确认没有遗漏" → requesting-code-review
```

三者不是竞争关系，是顺序使用的工具链：cr-refactor 发现问题 → gsd:code-review 执行重构 → requesting-code-review 最终把关。

---

## 八、AI 时代的重构节奏

**核心认知**：AI 不会自发重构。它只在你要求时清理，其余时间只会往前堆代码。重构节奏必须由人主动建立。

```
团队重构节奏建议：
  每迭代结束    → CR + 局部重构（30min）
  每里程碑结束  → 系统性重构 + Architecture as Code 检查
  技术债警戒线  → 当 cr-refactor 输出超过 10 条高优问题时，
                   下一个功能点之前先重构再开发
```

**写入 CLAUDE.md 防止 AI 重犯高频错误**：

CR 发现的问题如果有规律性（如"AI 总是在 API 层直接查数据库"），应该立刻写入 CLAUDE.md：

```markdown
## 架构约束（重要）
- 禁止：API 路由层直接操作数据库，必须通过 Service 层
- 禁止：跨模块直接 import 对方的私有实现
```

这样下一次 Agent 接受任务时会读到这条约束，不会重犯。
