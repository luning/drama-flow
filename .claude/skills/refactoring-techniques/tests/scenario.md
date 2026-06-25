# Test Scenario: FastAPI 路由重构

用于验证 `refactoring-techniques` skill 的压力场景。每次修改 skill 后重新运行以检查退化。

## 测试代码（输入）

```python
# backend/app/api/drama.py
@router.get("/dramas")
async def list_dramas(
    category: str = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Drama)
    if category:
        query = query.filter(Drama.category == category)
    total = query.count()
    dramas = query.offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for drama in dramas:
        episodes = db.query(Episode).filter(Episode.drama_id == drama.id).all()
        episode_count = len(episodes)
        latest_episode = max(episodes, key=lambda e: e.episode_number) if episodes else None
        result.append({
            "id": drama.id,
            "title": drama.title,
            "category": drama.category,
            "cover_url": drama.cover_url,
            "episode_count": episode_count,
            "latest_episode": latest_episode.episode_number if latest_episode else 0,
            "status": "ongoing" if drama.status == 1 else "completed"
        })
    return {"total": total, "items": result, "page": page, "page_size": page_size}


@router.get("/dramas/{drama_id}")
async def get_drama_detail(drama_id: int, db: Session = Depends(get_db)):
    drama = db.query(Drama).filter(Drama.id == drama_id).first()
    if not drama:
        raise HTTPException(status_code=404, detail="Drama not found")
    episodes = db.query(Episode).filter(Episode.drama_id == drama.id).all()
    episode_count = len(episodes)
    latest_episode = max(episodes, key=lambda e: e.episode_number) if episodes else None
    return {
        "id": drama.id,
        "title": drama.title,
        "category": drama.category,
        "cover_url": drama.cover_url,
        "description": drama.description,
        "episode_count": episode_count,
        "latest_episode": latest_episode.episode_number if latest_episode else 0,
        "episodes": [{"id": e.id, "number": e.episode_number, "title": e.title} for e in episodes],
        "status": "ongoing" if drama.status == 1 else "completed"
    }
```

## 测试问题（让 Agent 回答这三个问题）

1. Which smells did you identify and which **canonical technique name** maps to each?
2. In what order would you apply the techniques, and why that order?
3. What would you do **BEFORE** making any code changes?

## 通过标准（Pass Criteria）

| 检查点 | 期望行为 |
|--------|---------|
| 规范技巧名 | 使用 "Extract Function"、"Eager Load / SQL Aggregation"、"Move Method to Service Layer"、"Replace Magic Literal with Named Constant"，而非口语描述 |
| 识别 N+1 | 明确指出 `list_dramas` 中 loop 内的 `db.query(Episode)` 是 N+1 |
| 识别魔法数 | 指出 `drama.status == 1` 是 Magic Literal |
| 执行顺序 | 在写任何代码之前先提运行测试（pytest 基线）|
| 分步提交 | 每个技巧单独一次提交，不批量合并 |
| 业务逻辑归位 | 指出 route handler 里的序列化逻辑应 Move to Service Layer |

## 如何运行

在 Claude Code 里对一个新 Agent 发送以下 system prompt + user message：

**System prompt:** 把 `SKILL.md` 全文贴入（模拟 skill 已加载）

**User message:**
```
Here is Python code to refactor. Tell me:
1. Which smells did you identify and which canonical technique name maps to each?
2. In what order would you apply the techniques, and why?
3. What would you do BEFORE making any code changes?

[贴入上方测试代码]
```

## 失败时的处理

- Agent 说"extract helper"而非"Extract Function" → skill 的 technique 名称不够显眼，加粗或放到更早的位置
- Agent 没提 pytest → Safe Execution Protocol 不够强制，改为 Required 或加 ⚠️ 标记
- Agent 直接给出重构后代码而不说顺序 → 在 skill 里加"先列出计划，再执行"的约束
