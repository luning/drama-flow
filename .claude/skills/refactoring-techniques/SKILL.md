---
name: refactoring-techniques
description: Use when asked to refactor code, clean up smells, or improve existing implementation. Provides canonical technique names, smell-to-technique mapping, before/after patterns, and safe execution steps.
---

# Refactoring Techniques

## Overview

Systematic catalog of refactoring techniques. Each smell maps to a named technique with a decision rule and before/after pattern. Always refactor safely: tests green before and after each technique.

## Safe Execution Protocol

1. Run tests (green baseline required)
2. Apply ONE technique at a time
3. Run tests again (stay green)
4. Commit the single change
5. Move to the next technique

Never batch multiple techniques into one commit.

## Smell → Technique Map

| Smell | Technique |
|-------|-----------|
| Duplicated logic block (3+ copies) | Extract Method / Extract Function |
| Method does too many things | Extract Method |
| Class has too many responsibilities | Extract Class |
| Deep nested if/else | Replace Nested Conditional with Guard Clauses |
| Type-based branching (`if type == "A"`) | Replace Conditional with Polymorphism |
| Magic number/string literal | Replace Magic Literal with Named Constant |
| Loop building a collection | Replace Loop with Pipeline |
| N+1 query in a loop | Eager Load / SQL Aggregation |
| Business logic in route/controller | Move Method to Service Layer |
| Method only used by another class | Move Method |
| Unclear name | Rename (Method / Variable / Class) |
| Large legacy system to replace incrementally | Strangler Fig |

## Technique Reference

### Extract Method / Function

**When:** Logic block appears 3+ times (Rule of Three), OR a single block does a conceptually distinct thing even once.

**Decision:** Extract Method within same class → Extract Function if used across multiple classes/files → Move to Service if it's business logic or touches the DB.

```python
# Before
for drama in dramas:
    episodes = db.query(Episode).filter(...).all()
    count = len(episodes)
    latest = max(episodes, key=lambda e: e.episode_number) if episodes else None
    result.append({"episode_count": count, "latest_episode": latest.episode_number if latest else 0})

# After — extract the repeated aggregation
def _episode_summary(episodes: list[Episode]) -> dict:
    count = len(episodes)
    latest = max(episodes, key=lambda e: e.episode_number) if episodes else None
    return {"episode_count": count, "latest_episode": latest.episode_number if latest else 0}

for drama in dramas:
    episodes = db.query(Episode).filter(...).all()
    result.append(_episode_summary(episodes))
```

---

### Replace Nested Conditional with Guard Clauses

**When:** Logic is buried inside 2+ levels of if/else. Guard clauses invert early-exit conditions to flatten the happy path.

```python
# Before
def process(drama):
    if drama:
        if drama.status == 1:
            if drama.episodes:
                return drama.episodes[0]
    return None

# After
def process(drama):
    if not drama:
        return None
    if drama.status != 1:
        return None
    if not drama.episodes:
        return None
    return drama.episodes[0]
```

---

### Replace Conditional with Polymorphism

**When:** Repeated `if type == X` branches that grow when you add new types.

```python
# Before
def render_player(drama_type):
    if drama_type == "short":
        return ShortPlayer()
    elif drama_type == "series":
        return SeriesPlayer()

# After
class PlayerFactory:
    _registry = {"short": ShortPlayer, "series": SeriesPlayer}
    
    @classmethod
    def create(cls, drama_type: str):
        cls = cls._registry.get(drama_type)
        if not cls:
            raise ValueError(f"Unknown type: {drama_type}")
        return cls()
```

---

### Replace Loop with Pipeline

**When:** A loop filters + transforms a collection. Pipelines are more composable and readable.

```python
# Before
result = []
for episode in episodes:
    if episode.is_free:
        result.append({"id": episode.id, "title": episode.title})

# After
result = [
    {"id": e.id, "title": e.title}
    for e in episodes
    if e.is_free
]
```

---

### Eager Load / SQL Aggregation

**When:** N+1 query — a query inside a loop over query results.

```python
# Before (N+1: 1 query for dramas + N queries for episodes)
dramas = db.query(Drama).all()
for drama in dramas:
    episodes = db.query(Episode).filter(Episode.drama_id == drama.id).all()

# After — SQL aggregation in one query
from sqlalchemy import func

stats = (
    db.query(
        Episode.drama_id,
        func.count(Episode.id).label("episode_count"),
        func.max(Episode.episode_number).label("latest_episode"),
    )
    .group_by(Episode.drama_id)
    .subquery()
)

rows = (
    db.query(Drama, stats.c.episode_count, stats.c.latest_episode)
    .outerjoin(stats, Drama.id == stats.c.drama_id)
    .all()
)
```

---

### Move Method to Service Layer

**When:** Business logic lives in a route handler, controller, or view. The rule: if it queries the DB, calculates derived values, or enforces business rules — it belongs in the service layer.

```python
# Before — business logic in route
@router.get("/dramas/{id}")
async def get_drama(id: int, db: Session = Depends(get_db)):
    drama = db.query(Drama).filter(Drama.id == id).first()
    episodes = db.query(Episode).filter(Episode.drama_id == id).all()
    return {"episode_count": len(episodes), "status": "ongoing" if drama.status == 1 else "completed"}

# After — route delegates to service
@router.get("/dramas/{id}")
async def get_drama(id: int, db: Session = Depends(get_db)):
    return drama_service.get_drama_detail(db, id)
```

---

### Strangler Fig

**When:** Replacing a large legacy module incrementally without a big-bang rewrite.

**Steps:**
1. Create new implementation alongside old one
2. Route a small percentage of traffic/calls to new implementation
3. Verify new implementation is correct
4. Gradually shift all calls to new implementation
5. Delete old implementation

---

### Replace Magic Literal with Named Constant

```python
# Before
if drama.status == 1:
    ...

# After
DRAMA_STATUS_ONGOING = 1

if drama.status == DRAMA_STATUS_ONGOING:
    ...
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Applying multiple techniques at once | One technique per commit |
| Refactoring without tests | Get green baseline first, even if you have to write the test |
| Extracting too eagerly (2 copies) | Wait for 3 copies before extracting; 2 might be coincidence |
| Using Extract Method when Move to Service is correct | Ask: "Does this touch business rules or DB?" → Service. "Is it pure transformation?" → Method |
| Strangler Fig without a feature flag | Always have a rollback switch during transition |
