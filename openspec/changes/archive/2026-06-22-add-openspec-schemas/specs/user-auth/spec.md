## ADDED Requirements

### Requirement: 用户注册

系统 SHALL 允许新用户通过邮箱和密码注册账号。

**Scope**: Backend + H5  
**Endpoint**: `POST /api/auth/register`  
**Request**: `{ email: string, password: string, username?: string }`  
**Response 201**: `{ access_token: string, refresh_token: string, token_type: "bearer" }`  
**Response 400**: `{ detail: string }` — 邮箱已注册或格式无效  

#### Scenario: 注册成功
- **WHEN** 用户提交未注册的邮箱和合法密码
- **THEN** 返回 `201 Created` 及有效的 access_token 和 refresh_token

#### Scenario: 邮箱已存在
- **WHEN** 用户提交已注册的邮箱
- **THEN** 返回 `400 Bad Request`，不泄露用户是否已存在

#### Scenario: 注册后可立即登录
- **WHEN** 注册成功后使用同一邮箱密码登录
- **THEN** 登录返回 `200 OK` 及新的 token

---

### Requirement: 用户登录

系统 SHALL 支持用户通过邮箱和密码登录，并提供"记住我"选项控制 Token 持久化策略。

**Scope**: Backend + Android + H5  
**Endpoint**: `POST /api/auth/login`  
**Request**: `{ email: string, password: string }`  
**Response 200**: `{ access_token: string, refresh_token: string, token_type: "bearer", expires_in: number }`  
**Response 401**: `{ detail: "邮箱或密码错误" }` — 不区分邮箱不存在与密码错误  

#### Scenario: 凭证正确登录
- **WHEN** 用户提交正确的邮箱和密码
- **THEN** 返回 `200 OK`，包含 access_token（含用户 ID 和过期时间）和 refresh_token

#### Scenario: 密码错误
- **WHEN** 用户提交错误密码
- **THEN** 返回 `401 Unauthorized`，Android 端清空密码框并显示"邮箱或密码错误"

#### Scenario: 勾选记住我 — Token 持久化
- **WHEN** 用户勾选"记住我"并登录成功
- **THEN** Android 端将 access_token 和 refresh_token 写入 EncryptedSharedPreferences，App 重启后自动恢复登录状态

#### Scenario: 未勾选记住我 — Token 仅存内存
- **WHEN** 用户未勾选"记住我"并登录成功
- **THEN** Token 仅保存在 ViewModel 内存中，App 退出后清除，下次启动需重新登录

---

### Requirement: Token 刷新

系统 SHALL 允许客户端使用有效的 refresh_token 无感刷新 access_token，刷新失败时静默跳转登录页。

**Scope**: Backend + Android  
**Endpoint**: `POST /api/auth/refresh`  
**Request**: `{ refresh_token: string }`  
**Response 200**: `{ access_token: string, refresh_token: string, expires_in: number }`  
**Response 401**: `{ detail: "refresh token 无效或已过期" }`  

#### Scenario: access_token 过期自动刷新
- **WHEN** API 请求返回 `401 Unauthorized` 且本地有 refresh_token
- **THEN** Android 端自动调用 `/api/auth/refresh`，替换 access_token 后重试原始请求，用户无感知

#### Scenario: refresh_token 失效跳转登录
- **WHEN** `/api/auth/refresh` 返回 `401`
- **THEN** Android 端清除所有 Token，跳转登录页，不产生白屏或崩溃

---

### Requirement: 用户登出

系统 SHALL 支持用户主动登出，服务端使当前 Token 失效，客户端清除本地凭证。

**Scope**: Backend + Android  
**Endpoint**: `POST /api/auth/logout`  
**Request Header**: `Authorization: Bearer <access_token>`  
**Response 200**: `{ message: "登出成功" }`  

#### Scenario: 登出成功
- **WHEN** 用户点击退出登录并携带有效 access_token 请求
- **THEN** 返回 `200`，Android 端清除 EncryptedSharedPreferences 中的 Token，通过 `popUpToInclusive=true` 清除回退栈后跳转登录页

#### Scenario: 首页展示退出入口
- **WHEN** 用户已登录并打开首页
- **THEN** 页面提供退出登录入口（按钮或菜单项）
