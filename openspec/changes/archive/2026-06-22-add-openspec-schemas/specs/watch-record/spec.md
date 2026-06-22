## ADDED Requirements

### Requirement: 观看进度上报

系统 SHALL 接受客户端定期上报的视频播放进度，并在用户登录状态下持久化保存。

**Scope**: Backend + Android  
**Endpoint**: `PUT /api/watch-records/{episode_id}`  
**Request Header**: `Authorization: Bearer <access_token>`  
**Request**: `{ position_seconds: number, duration_seconds: number, completed?: boolean }`  
**Response 200**: `{ episode_id, position_seconds, updated_at }`  
**Response 401**: `{ detail: "未认证" }` — 未登录用户无法上报  

#### Scenario: 播放中定期上报
- **WHEN** Android 播放器每 15 秒触发一次进度上报
- **THEN** 服务端保存或更新该用户对该剧集的 WatchRecord，返回 `200 OK`

#### Scenario: 暂停时上报
- **WHEN** 用户暂停播放
- **THEN** Android 端立即调用进度上报接口

#### Scenario: 未登录用户上报
- **WHEN** 未携带 Token 的请求调用上报接口
- **THEN** 返回 `401 Unauthorized`

#### Scenario: 标记完成
- **WHEN** 视频播放到最后 5 秒或到达 `duration_seconds` 时上报 `completed: true`
- **THEN** 服务端将该 WatchRecord 的 `completed` 字段设为 `true`

---

### Requirement: 单集观看记录查询

系统 SHALL 支持查询指定剧集的当前用户观看记录，用于恢复播放位置。

**Scope**: Backend + Android + H5  
**Endpoint**: `GET /api/watch-records/{episode_id}`  
**Request Header**: `Authorization: Bearer <access_token>`  
**Response 200**: `{ episode_id, position_seconds, duration_seconds, completed, updated_at }`  
**Response 404**: `{ detail: "无观看记录" }` — 未看过该集  

#### Scenario: 查询已有记录
- **WHEN** 已登录用户请求曾播放过的剧集记录
- **THEN** 返回 `200` 及进度信息

#### Scenario: 无记录时返回 404
- **WHEN** 已登录用户请求从未播放的剧集记录
- **THEN** 返回 `404`，播放器从头开始播放

---

### Requirement: 继续观看列表

系统 SHALL 提供"继续观看"聚合列表，按更新时间降序返回用户最近有进度的剧目。

**Scope**: Backend + H5 + Android  
**Endpoint**: `GET /api/watch-records/continue-watching`  
**Request Header**: `Authorization: Bearer <access_token>`  
**Response 200**: `[{ drama_info: { drama_id, title, image_url }, episode_info: { episode_id, episode_number, title }, progress: number, last_position: number }]`  

#### Scenario: 已登录用户获取继续观看列表
- **WHEN** 已登录用户 GET `/api/watch-records/continue-watching`
- **THEN** 返回该用户有进度的剧目列表，按 `updated_at` 降序

#### Scenario: 无观看记录时返回空数组
- **WHEN** 新用户或没有任何观看记录的用户请求
- **THEN** 返回 `200 OK` + `[]`，前端继续观看区域隐藏

#### Scenario: 未登录用户请求
- **WHEN** 未携带 Token 的请求调用继续观看接口
- **THEN** 返回 `401 Unauthorized`

---

### Requirement: 用户观看记录列表

系统 SHALL 支持分页查询当前用户的全部观看记录，按更新时间降序。

**Scope**: Backend  
**Endpoint**: `GET /api/watch-records?page={n}&size={m}`  
**Request Header**: `Authorization: Bearer <access_token>`  
**Response 200**: `{ items: WatchRecord[], total: number, page: number, size: number }`  

#### Scenario: 获取观看记录列表
- **WHEN** 已登录用户请求观看记录列表
- **THEN** 返回按 `updated_at` 降序分页数据
