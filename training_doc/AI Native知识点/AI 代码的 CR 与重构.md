# AI 代码的 CR 与重构 - 找错误 · 控技术债 · 重构决策

## 目录

1. [AI 高频错误模式（找什么）](#ai-高频错误模式找什么)
   - [重复逻辑](#重复逻辑)
   - [状态泄漏](#状态泄漏)
   - [命名混乱](#命名混乱)
   - [不遵循约定架构](#不遵循约定架构)
   - [啰嗦的注释或实现](#啰嗦的注释或实现)
   - [把规律性错误写回 CLAUDE.md](#把规律性错误写回-claudemd)
2. [CR 扫描与重构提示词](#cr-扫描与重构提示词)
   - [扫描阶段](#扫描阶段)
   - [优先级确认](#优先级确认)
   - [执行重构](#执行重构)
3. [重构 vs 重写：如何决策](#重构-vs-重写如何决策)
   - [技术债：接受 vs 立即修复](#技术债接受-vs-立即修复)
4. [三种 CR 做法](#三种-cr-做法)

---

> **为什么 AI 时代反而更需要 CR + 重构？**
> AI 生成代码的速度是传统开发的 10 倍，技术债的积累速度也是 10 倍。没有 CR + 重构节奏，代码库会在不知不觉中变成 AI 无法理解自己写过的东西的迷宫。
>
> **节奏原则**：每次迭代结束做一次 CR，是避免"还不如重写"的最低成本路径。CR 是主动节奏，不是被动救火。

---

## AI 高频错误模式（找什么）

这五类问题在 AI 生成的代码中出现频率最高，CR 时优先扫描：

### 重复逻辑
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

### 状态泄漏
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

### 命名混乱
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

### 不遵循约定架构
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

### 啰嗦的注释或实现

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

### 把规律性错误写回 CLAUDE.md

CR 发现的问题如果**有规律性**（如"AI 总是在 API 层直接查数据库"），立刻写入 CLAUDE.md——下一次 Agent 接受任务时会读到这条约束，不会重犯：

```markdown
## 架构约束（重要）
- 禁止：API 路由层直接操作数据库，必须通过 Service 层
- 禁止：跨模块直接 import 对方的私有实现
```

---

## CR 扫描与重构提示词

### 扫描阶段

```
"对 backend/app/ 目录做 CR，输出以下分类的问题清单：
 - 重复逻辑（可复用但未复用的代码片段）
 - 状态管理风险（类变量/全局变量）
 - 命名一致性（同一概念不同叫法）
 - 架构违规（跳过层的直接调用）
 - 测试盲区（无任何测试覆盖的关键路径）
 按影响范围排序，只列出有实际风险的，不需要风格偏好。"
```

### 优先级确认

```
"从上面的清单中，哪 2-3 条在现有测试的保护下可以安全重构？
 哪些需要先补测试再动？哪些可以接受暂不处理？"
```

### 执行重构

重构的铁律：**不改功能，只改结构。** 用提示词明确边界，防止 AI 顺手改了逻辑：

```
"重构 [目标函数/模块]，目标是 [提取重复逻辑/改善命名/分离职责]。
 约束：
 1. 不修改任何业务逻辑和返回值格式
 2. 保持所有已通过的 pytest 用例继续通过
 3. 不引入新的依赖
 4. 每次只改一个地方，改完后告诉我下一步

 先告诉我你的重构计划，我确认后再执行。"
```

**为什么要"先告诉我计划"**：AI 重构时有时会"顺手"修改逻辑，或修改多处造成难以 review 的大 diff。强制分步可控。

重构完成后立即跑测试，有失败立刻回滚，不要继续重构其他地方：

```bash
source backend/drama-flow/bin/activate
pytest backend/tests/ -v
```

---

## 重构 vs 重写：如何决策

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

### 技术债：接受 vs 立即修复

| 债的来源 | 处置方式 |
|---------|---------|
| 旧路径因新需求失效、临时桥接逻辑（**需求变更债**）| 标注 `# TODO: cleanup after v1.1`，下个迭代开始前统一清理 |
| 新代码复制了已有逻辑（**新功能债**）| 本迭代 CR 时处理，不能留 |
| 新功能绕过架构层、引入全局状态（**新功能债**）| 本迭代 CR 时处理，不能留 |

**判断原则**：技术债如果会"传染"下一个功能点，立即还；如果只是孤立的旧代码，可以标记后计划清理。

---

## 三种 CR 做法

做 CR 没有固定工具要求，根据个人习惯选自己顺手的就行：

| 做法 | 说明 |
|------|------|
| **直接让 Agent CR** | 把第二节的扫描提示词发给 Agent，让它输出问题清单，再逐条跟进 |
| **用自己写的 Skill**（`cr-refactor`）| 封装好了扫描逻辑，`/cr-refactor [路径]` 直接触发，省去手写提示词 |
| **用工具内置的 CR Skill**（`gsd:code-review`）| GSD 工具链的 CR 命令，输出格式更结构化，适合已经在用 GSD 工作流的场景 |
