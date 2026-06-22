# drama-catalog Specification

## Purpose
TBD - created by archiving change add-openspec-schemas. Update Purpose after archive.
## Requirements
### Requirement: 剧目列表接口

系统 SHALL 提供分页剧目列表，支持分类筛选；已登录用户未指定分类时返回个性化排序结果。

**Scope**: Backend + H5  
**Endpoint**: `GET /api/dramas?category={cat}&page={n}&size={m}`  
**Response 200**: `{ items: Drama[], total: number, page: number, size: number }`  
**Drama 字段**: `{ drama_id, title, image_url, category, rating, episode_count, sort_order }`  

#### Scenario: 未登录用户获取全量列表
- **WHEN** 未携带 Token 的客户端请求 `/api/dramas`（不传 category）
- **THEN** 返回全量剧目列表，按 `sort_order` 升序排列

#### Scenario: 已登录用户个性化排序
- **WHEN** 已登录用户请求 `/api/dramas`（不传 category）
- **THEN** 返回个性化排序列表：同类未看（最高优先）→ 进行中 → 其他未看 → 已全部看完（最低），同优先级内按评分降序

#### Scenario: 分类筛选
- **WHEN** 客户端传入 `category` 参数
- **THEN** 返回该分类下剧目，按更新时间降序，不受个性化排序影响

#### Scenario: 分页
- **WHEN** 客户端传入 `page` 和 `size` 参数
- **THEN** 返回对应分页数据，`total` 字段为该条件下总数量

---

### Requirement: 分类列表接口

系统 SHALL 提供可筛选的分类列表，每项包含分类 ID 和名称。

**Scope**: Backend + H5  
**Endpoint**: `GET /api/dramas/categories`  
**Response 200**: `[{ id: string, name: string, sort_order: number }]`  

#### Scenario: 获取分类列表
- **WHEN** 客户端 GET `/api/dramas/categories`
- **THEN** 返回全部分类数组，按 `sort_order` 升序，包含 `{ id, name, sort_order }`

---

### Requirement: 剧目详情接口

系统 SHALL 提供单部剧目的完整详情，包含剧目元信息和剧集列表。

**Scope**: Backend + H5  
**Endpoint**: `GET /api/dramas/{drama_id}`  
**Response 200**: `{ drama_id, title, description, image_url, category, rating, episode_count, tags, episodes: Episode[] }`  
**Episode 字段**: `{ episode_id, episode_number, title, duration_seconds }`  
**Response 404**: `{ detail: "剧目不存在" }`  

#### Scenario: 获取存在的剧目详情
- **WHEN** 客户端 GET `/api/dramas/{drama_id}` 且该剧目存在
- **THEN** 返回 `200`，包含完整剧目信息和有序剧集列表（按 `episode_number` 升序）

#### Scenario: 剧目不存在
- **WHEN** 客户端请求不存在的 `drama_id`
- **THEN** 返回 `404 Not Found`

---

### Requirement: 剧集列表接口

系统 SHALL 支持单独查询某剧目的剧集列表，不重复返回剧目元信息。

**Scope**: Backend + H5  
**Endpoint**: `GET /api/dramas/{drama_id}/episodes`  
**Response 200**: `[{ episode_id, episode_number, title, duration_seconds }]`  

#### Scenario: 获取剧集列表
- **WHEN** 客户端 GET `/api/dramas/{drama_id}/episodes`
- **THEN** 返回该剧目的所有剧集，按 `episode_number` 升序

#### Scenario: H5 详情页展示剧集列表
- **WHEN** H5 详情页加载完成
- **THEN** 展示剧集列表，用户点击剧集后通过 JSBridge 调用播放器

