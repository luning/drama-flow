# Phase 1: Homepage Recommendation Validation - Research

**Researched:** 2026-05-05
**Domain:** Backend recommendation algorithm + H5 data binding
**Confidence:** HIGH

## Summary

Phase 1 is a validation & completion phase for the "homepage recommendation" feature defined in Iteration 3 (AC-DRAMA-07/08/09). The core discovery is that **the personalized recommendation logic was specified and acceptance criteria were defined, but was never actually implemented** in the backend service layer. The H5 frontend is already set up to consume the data with no changes needed.

The implementation gap: `drama_service.list_dramas()` always returns results sorted by `updated_at DESC` regardless of user authentication status. The route handler does not inject `get_optional_user()`. The recommendation algorithm -- "same category first, completed dramas downgraded" -- must be added to the backend. The H5 home store and API client already propagate auth tokens via Axios interceptor, so the personalized response will flow automatically once the backend is updated.

**Primary recommendation:** Implement the personalized sorting algorithm in `drama_service.py`, wire `get_optional_user()` into the route handler, and add tests for AC-DRAMA-07/08/09. No H5 changes required for basic REC-01/REC-02/REC-03 compliance.

---

## User Constraints

No CONTEXT.md exists for this phase. No user decisions have been locked. Research covers all options with recommendations.

## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REC-01 | Logged-in users get personalized sorting based on watch history (same category first) | Algorithm designed below in Architecture Patterns. Implementation gap confirmed -- `drama_service.list_dramas()` currently only sorts by `updated_at DESC`. |
| REC-02 | Completed dramas get lower weight in recommendation list | Part of the sorting algorithm. Any drama with at least one completed WatchRecord gets lowest priority tier. |
| REC-03 | Unauthenticated users unaffected by personalization | Existing `get_optional_user()` middleware returns `None` for unauthenticated requests. Route must inject it; service must branch on presence of user. |
| REC-04 | Fallback when watch records are insufficient | When user has no WatchRecords (or only empty set), return default `updated_at DESC` order. Algorithm naturally handles this -- empty history produces no category signal. |

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Personalization sorting logic | Backend API | Database (SQLite) | Algorithm queries WatchRecords to compute sort order. DB provides the raw data; backend owns the sorting business logic. |
| Auth detection (optional user) | Backend API | -- | `get_optional_user()` middleware already exists in auth_middleware.py. Route just needs to inject it. |
| H5 data display | Browser (H5 WebView) | -- | Home.vue renders `store.dramas` in a grid. No UI changes needed -- data is already displayed. |
| Auth token propagation | Browser (H5) | -- | Axios interceptor in client.ts already attaches Bearer token from localStorage. |
| Current default sort (unauthed fallback) | Backend API | -- | `order_by(desc(Drama.updated_at))` is the existing default. Preserve for unauthed users and fallback. |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.128.8 | API framework | Already established. Route handlers, dependency injection, path/query params. |
| SQLAlchemy | 2.0.49 | ORM | Already established. Querying WatchRecords with joins to Episode/Drama for the recommendation algorithm. |
| Pydantic | 2.13.3 | Schema validation | Already established. Request/response models. |
| pytest | 8.4.2 | Testing | Already established. Add tests for AC-DRAMA-07/08/09. |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| PyJWT | 2.8.0+ | JWT token handling | Already used in auth_middleware.py for `decode_token()` -- no changes needed. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Custom SQLAlchemy sort logic | Redis-based recommendation cache | Unnecessary complexity. 5 dramas, single-user MVP. SQLAlchemy query is sufficient and directly uses existing data. |
| Backend-side personalization | Client-side re-sorting | Client-side would expose recommendation logic and require fetching all data. Backend side is cleaner and supports pagination. |
| Category-based personalization | Collaborative filtering (ALS) | Excluded by PROJECT.md decision. Category-based is simple, understandable, and sufficient for MVP. |

**Version verification:**
```bash
$ npm view fastapi version  # N/A -- Python package
```
Instead verified via pip: fastapi==0.128.8, sqlalchemy==2.0.49, pytest==8.4.2 [VERIFIED: pip list]

---

## Architecture Patterns

### System Architecture Diagram

```
                         GET /api/dramas?category=all&page=1
                         (Bearer token in Authorization header)
H5 Home.vue ─────────────────────────────────────────────► FastAPI Route
  │                                                         │
  │ Axios interceptor                                       │ Depends(get_optional_user)
  │ attaches Bearer token                                   │ Depends(get_db)
  │ from localStorage                                       │
  │                                                         ▼
  │                                              drama_service.list_dramas()
  │                                                │
  │                                                ├── user is None ──► default sort (updated_at DESC)
  │                                                │
  │                                                └── user is authenticated ──► personalized sort
  │                                                       │
  │                                                       ├── query WatchRecords for user_id
  │                                                       ├── extract watched category IDs
  │                                                       ├── separate completed vs in-progress
  │                                                       ├── sort: same-cat unwatched >
  │                                                       │       other-cat unwatched >
  │                                                       │       in-progress >
  │                                                       │       completed
  │                                                       └── no records? fallback to default sort
  │                                                              │
  │               ┌──────────────────────────────────────────────┘
  │               ▼
  │         JSON response: { items: [...], total, page, size }
  │               │
  ◄───────────────┘
  │
  ▼
store.dramas = resp.data.items
  │
  ▼
DramaCard grid renders
```

### Algorithm Details

The personalized sorting algorithm for REC-01 and REC-02:

```
Input:
  - all_dramas: list of Drama objects ordered by updated_at DESC (the query result)
  - user_id: int (authenticated user)

Process:
  1. Query all WatchRecords for this user:
     SELECT wr.*, e.drama_id FROM watch_records wr
     JOIN episodes e ON e.id = wr.episode_id
     WHERE wr.user_id = :user_id

  2. Build sets:
     - watched_drama_ids: all drama IDs with any watch record
     - completed_drama_ids: drama IDs where ANY episode has completed=True
     - in_progress_drama_ids: watched_drama_ids - completed_drama_ids
     - watched_category_ids: category IDs of all watched dramas

  3. Assign sort priority (lower = earlier in list):
     Priority 0: unwatched dramas in watched categories (same-category first)
     Priority 1: unwatched dramas in other categories
     Priority 2: in-progress dramas
     Priority 3: completed dramas

  4. Within each priority tier, preserve updated_at DESC order

  5. If watched_category_ids is empty (no records): return as-is (REC-04 fallback)

Output: sorted list of Drama objects
```

### Recommended Project Structure

No structural changes needed. All changes are in existing files:

```
backend/
├── app/
│   ├── api/
│   │   └── dramas.py              # [MODIFY] Add get_optional_user() dependency
│   └── services/
│       └── drama_service.py       # [MODIFY] Add personalized sorting logic
└── tests/
    └── test_dramas.py             # [MODIFY] Add AC-DRAMA-07/08/09 tests
```

### Pattern 1: Optional User Injection in Route

**What:** FastAPI pattern for routes that work both for authenticated and unauthenticated users. The `get_optional_user()` dependency returns `Optional[User]` without raising 401 on missing credentials.

**When to use:** Any route where behavior differs based on authentication but unauthenticated access is still valid.

**Example (already exists in codebase):**

```python
# Source: backend/app/middleware/auth_middleware.py [VERIFIED]
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.services.auth_service import decode_token
from app.models.user import User

security = HTTPBearer(auto_error=False)

def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        return db.query(User).filter(User.id == int(payload.get("sub"))).first()
    except (ValueError, Exception):
        return None
```

### Pattern 2: Service Layer with Optional User

**What:** The service method accepts `Optional[User]` as a parameter and branches behavior. This keeps business logic in the service layer rather than the route layer.

**Example (to be implemented):**

```python
# Source: recommended pattern for this phase
def list_dramas(
    db: Session,
    user: Optional[User] = None,
    category: Optional[str] = None,
    page: int = 1,
    size: int = 20,
):
    query = db.query(Drama).options(joinedload(Drama.category))

    if category and category != "all":
        query = query.join(Category).filter(Category.slug == category)

    total = query.count()

    if user and (not category or category == "all"):
        # Personalized sort for authenticated users
        items = _personalized_recommendations(db, user.id, query)
    else:
        # Default sort for unauthenticated or category-filtered requests
        items = query.order_by(desc(Drama.updated_at)).all()

    # Paginate after sorting (load all into memory for sort, then slice)
    paginated = items[(page - 1) * size : page * size]
    # ... build response dict ...
```

### Anti-Patterns to Avoid

- **Doing the sort in the route layer**: Business logic (recommendation algorithm) belongs in the service layer, not the API route handler. Keep `dramas.py` thin.
- **N+1 queries in sort loop**: Avoid querying WatchRecord inside a loop over dramas. Use a single query to get all relevant records upfront, then process in-memory.
- **Modifying query before calling `.count()`**: The `.count()` call evaluates the query. If modifications are made after `.count()`, the count reflects the wrong dataset. Count before applying personalization.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Recommendation engine | Collaborative filtering, ALS, ML model | Simple category-based sort from WatchRecord data | PROJECT.md explicitly excludes complex recommendation. Category-based sort is sufficient for MVP with 5 dramas. |
| Auth middleware | Custom auth dependency | Existing `get_optional_user()` | Already implemented and tested. Just need to wire into route. |

**Key insight:** The recommendation logic is intentionally simple -- no external recommendation engine, no ML. The algorithm is a sort-key assignment based on existing WatchRecord data. This is by design per PROJECT.md.

---

## Runtime State Inventory

> Skip -- this is not a rename/refactor/migration phase.

---

## Common Pitfalls

### Pitfall 1: Personalization applied even when category filter is active

**What goes wrong:** User clicks category "romance" tab but gets personalized sorting, which contradicts the user's explicit filter intent.
**Why it happens:** Route handler applies personalization for ALL authenticated requests instead of only when no category is specified.
**How to avoid:** Only apply `_personalized_recommendations()` when `category is None or category == "all"`. When a specific category slug is provided, always use default sort within that category.
**Warning signs:** A logged-in user filtering by category sees results in unexpected order.

### Pitfall 2: Sorting before pagination causes unexpected page behavior

**What goes wrong:** The personalized sort is applied to ALL dramas, then pagination slices. If the algorithm is expensive, this could be slow at scale.
**Why it happens:** Sort requires the full dataset to compute global order -- you cannot push pagination into the SQL query when the sort key is computed in Python.
**How to avoid:** Accept this tradeoff for MVP. Load all matching dramas into memory, sort, then paginate. For the current dataset (5 dramas) this is negligible. Document as a scalability concern if the drama catalog grows beyond ~1000 titles.
**Warning signs:** Recommendation endpoint response time increases as drama count grows.

### Pitfall 3: H5 does not send auth header on initial page load

**What goes wrong:** When a user first opens the H5 page (e.g., direct URL access, not via login flow), `localStorage` may not have the token yet even though the user is "logged in" from the Android side.
**Why it happens:** Android's EncryptedSharedPreferences and the H5's localStorage are separate stores. The H5 only gets the token after the auth store calls `tryRestoreSession()` or a login flow completes.
**How to avoid:** This is a pre-existing architectural issue not in scope for this phase. The current behavior is: unauthenticated users see default sort, which is acceptable per REC-03.
**Warning signs:** Users report inconsistent personalization between Android native screens and H5 screens.

### Pitfall 4: Neglecting to handle the "all watched" edge case

**What goes wrong:** A user has watched (and completed) ALL available dramas. The personalized sort puts them all at priority 3. The order within completed dramas is still `updated_at DESC`, but the page still needs to show content.
**Why it happens:** Low-priority items still appear in the list -- they just sort last. No special handling needed, but the planner should verify this case.
**How to avoid:** Default sort within each priority tier ensures sensible ordering. No special "if all watched" logic needed.
**Warning signs:** N/A -- this case works correctly by default.

---

## Code Examples

### Verified: Current `drama_service.list_dramas()` -- BEFORE state

```python
# Source: backend/app/services/drama_service.py [VERIFIED]
def list_dramas(db: Session, category: Optional[str] = None, page: int = 1, size: int = 20):
    query = db.query(Drama).options(joinedload(Drama.category))

    if category and category != "all":
        query = query.join(Category).filter(Category.slug == category)

    total = query.count()
    items = query.order_by(desc(Drama.updated_at)) \
                 .offset((page - 1) * size) \
                 .limit(size) \
                 .all()
    # ... build response ...
```

### Verified: Current route handler -- BEFORE state

```python
# Source: backend/app/api/dramas.py [VERIFIED]
@router.get("/dramas")
def list_dramas(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return drama_service.list_dramas(db, category, page, size)
```

### Verified: Current H5 auth token propagation

```typescript
// Source: h5/src/api/client.ts [VERIFIED]
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### Data Model: WatchRecord

```python
# Source: backend/app/models/watch_record.py [VERIFIED]
class WatchRecord(Base):
    __tablename__ = "watch_records"
    __table_args__ = (
        UniqueConstraint("user_id", "episode_id", name="uq_user_episode"),
    )
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)
    progress = Column(Float, default=0.0)       # 0-100
    last_position = Column(Float, default=0.0)  # seconds
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = relationship("User")
    episode = relationship("Episode", back_populates="watch_records")
```

### WatchRecord -> Drama relationship chain

```python
# WatchRecord -> Episode.drama_id -> Drama.id
# This requires a join across two tables to get drama_id from a WatchRecord
wr -> db.query(Episode).filter(Episode.id == wr.episode_id).first() -> episode.drama_id
# Or more efficiently with a single query:
# SELECT e.drama_id FROM watch_records wr
# JOIN episodes e ON e.id = wr.episode_id
# WHERE wr.user_id = :user_id
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Sort by `updated_at DESC` only | Personalized sort with same-category-first + completed-downgraded | Phase 1 | Logged-in users see relevant content first |
| Route `GET /api/dramas` uses `get_db` only | Route also uses `get_optional_user()` | Phase 1 | Backend can distinguish authenticated vs anonymous requests |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | H5 Axios interceptor already has the auth token in localStorage when the user is logged in | Standard Stack | If token is not in localStorage during Home.vue mount (e.g., session not restored yet), the request goes unauthenticated and user gets default sort -- which is acceptable per REC-03 |
| A2 | Python 3.9 compatibility is acceptable despite PROJECT.md stating 3.10+ | Standard Stack | If code introduced uses `str | None` syntax (Python 3.10+), it will fail at runtime on the installed 3.9.6 -- use `Optional[str]` instead |
| A3 | No existing tests for AC-DRAMA-07/08/09 | Common Pitfalls | If tests exist and we duplicate, we waste effort. Verified by reading test_dramas.py -- confirmed no such tests exist. |

---

## Open Questions

1. **Should `category="all"` trigger personalization?**
   - What we know: The H5 always sends `category=all` when no category tab is active. The current service treats `all` as "no filter". The SPEC says "不传分类参数时" (when no category parameter is passed).
   - What's unclear: If we only trigger personalization when `category` is None (not passed), the H5 will never trigger it since it always passes `category=all`.
   - Recommendation: Treat `category="all"` as equivalent to no category for personalization triggering. This is consistent with existing filter logic in `list_dramas()`.

2. **What defines a drama as "completed"?**
   - What we know: WatchRecord has a `completed` boolean per episode. A drama has multiple episodes.
   - What's unclear: Is a drama "completed" when ANY episode has `completed=True`, or only when ALL episodes are completed?
   - Recommendation: A drama is "completed" for downgrading if ANY of its episodes has `completed=True`. This is the simplest interpretation and matches user intent -- if they finished even one episode of a very short drama and didn't continue, they likely don't want to see it promoted. This is an [ASSUMED] claim that should be confirmed.

3. **What about dramas the user is currently watching (in-progress)?**
   - What we know: Some dramas have WatchRecords but none marked `completed=True`.
   - What's unclear: Should in-progress dramas be at priority 2 (between same-category and completed) or at the bottom?
   - Recommendation: Place in-progress at priority 2 (after all unwatched, before completed). Rationale: the user is already engaged with this drama -- showing other options first is more useful than re-promoting what they're already watching.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Backend runtime | Yes | 3.9.6 | -- (compatible with project code, but avoid 3.10+ syntax) |
| pip packages | All backend features | Yes | per requirements.txt | -- |
| pytest | Testing | Yes | 8.4.2 | -- |
| FastAPI | API framework | Yes | 0.128.8 | -- |
| SQLAlchemy | ORM | Yes | 2.0.49 | -- |
| SQLite | Database | Yes | (built-in Python) | -- |
| Node.js | H5 development | Unknown | -- | Not needed for this phase (no H5 changes expected) |
| npm/yarn | H5 dependencies | Unknown | -- | Not needed for this phase |

**Missing dependencies with no fallback:** None identified.

**Missing dependencies with fallback:** None identified.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.4.2 |
| Config file | none -- convention-based discovery |
| Quick run command | `source backend/drama-flow/bin/activate && cd backend && pytest -x` |
| Full suite command | `source backend/drama-flow/bin/activate && cd backend && pytest` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command |
|--------|----------|-----------|-------------------|
| REC-01 | Logged-in user with watch history gets personalized sort | integration | `pytest tests/test_dramas.py::TestDramasPersonalized::test_logged_in_personalized_sort -x` |
| REC-02 | Completed dramas get lower weight | integration | `pytest tests/test_dramas.py::TestDramasPersonalized::test_completed_dramas_downgraded -x` |
| REC-03 | Unauthenticated users get default sort | integration | `pytest tests/test_dramas.py::TestDramasPersonalized::test_unauthenticated_default_sort -x` |
| REC-04 | User with no watch records gets default sort (fallback) | integration | `pytest tests/test_dramas.py::TestDramasPersonalized::test_no_watch_records_fallback -x` |

### Sampling Rate
- **Per task commit:** `cd backend && source drama-flow/bin/activate && pytest -x`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_dramas.py` -- needs `TestDramasPersonalized` class with AC-DRAMA-07/08/09 tests
- [ ] `tests/conftest.py` -- needs `seed_watch_records` fixture for creating test watch records (or tests can create inline via API calls per existing pattern in test_watch_records.py)

### Test Data Strategy

For AC-DRAMA-07/08/09 tests, the test data needs:
1. A logged-in user with watch history
2. At least two dramas in the **same category** to test "same-category first" sorting
3. At least one completed drama to test "completed downgrade"

The existing `seed_dramas` fixture has 5 dramas in 5 different categories. To test "same-category first", a new fixture or additional drama is needed (e.g., add a 6th drama in the "fantasy" category). Alternatively, modify the test to create records mid-test using API calls, following the pattern in `test_watch_records.py`.

---

## Security Domain

> `security_enforcement` is not explicitly disabled in config.json. Domain covered.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | Yes | JWT via existing `get_optional_user()` middleware |
| V4 Access Control | Yes | Service layer branches on presence of user object. No sensitive data exposed to unauthenticated users. |
| V5 Input Validation | Yes | Pydantic models for all request bodies. Query params validated by FastAPI. |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| User ID tampering | Elevation of Privilege | The `user.id` comes from JWT token, not from request parameters. The service layer reads user ID from the decoded token via `get_optional_user()`, which is secure. |
| Data exposure to unauthenticated users | Information Disclosure | REC-03 explicitly requires unauthenticated users to see default sort, not personalized data. The service layer only queries WatchRecords when `user` is not None. |

---

## Sources

### Primary (HIGH confidence)
- Backend source code: `backend/app/services/drama_service.py`, `backend/app/api/dramas.py`, `backend/app/middleware/auth_middleware.py` -- verified current state of all implementation files
- Test suite: `backend/tests/test_dramas.py`, `backend/tests/conftest.py` -- verified no AC-DRAMA-07/08/09 tests exist
- Data models: `backend/app/models/watch_record.py`, `backend/app/models/drama.py`, `backend/app/models/episode.py` -- verified schema relationships
- H5 source: `h5/src/stores/home.ts`, `h5/src/api/client.ts`, `h5/src/pages/Home.vue` -- verified no H5 changes needed
- Requirements: `PROJECT.md`, `REQUIREMENTS.md`, `SPEC.md` -- verified requirement definitions and acceptance criteria
- Config: `.planning/config.json` -- verified `nyquist_validation: false`

### Secondary (MEDIUM confidence)
- [CITED: fastapi.tiangolo.com/tutorial/security/get-current-user/] -- FastAPI optional dependency pattern
- [CITED: stackoverflow.com/questions/67774905/make-depends-optional-in-fastapi] -- Optional auth dependency pattern, consistent with existing `get_optional_user()` implementation

### Tertiary (LOW confidence)
- None -- all key claims verified against codebase

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- verified against pip list, existing code imports, and requirements.txt
- Architecture: HIGH -- verified against current implementation files; the gap is clear and well-defined
- Pitfalls: MEDIUM -- based on code analysis and common FastAPI patterns, but untested at scale

**Research date:** 2026-05-05
**Valid until:** 2026-06-05 (stable project -- no fast-moving dependencies)
