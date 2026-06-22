## ADDED Requirements

### Requirement: JSBridge 对象挂载

Android 端 SHALL 在 WebView 加载完成后将 `DramaFlowBridge` 对象注入到 `window` 对象，H5 在访问前 SHALL 先判断对象是否存在。

**Scope**: Android + H5  

#### Scenario: Bridge 对象存在检查
- **WHEN** H5 代码需要调用任何 Bridge 方法
- **THEN** 先判断 `typeof window !== 'undefined' && window.DramaFlowBridge` 为真，否则降级处理（不抛出异常）

#### Scenario: Bridge 注入时机
- **WHEN** WebView 的 `onPageFinished` 触发
- **THEN** `window.DramaFlowBridge` 已可用，H5 可安全调用所有 Bridge 方法

---

### Requirement: 播放器调用方法

`DramaFlowBridge` SHALL 提供两种方式从 H5 启动 Android 原生播放器。

**Scope**: Android + H5  
**方法签名**:
```
openPlayer(episodeId: number, dramaId: number, episodeNumber: number): void
playVideo(episodeId: number, videoUrl: string, title: string, dramaId?: number, episodeNumber?: number): void
```

#### Scenario: H5 详情页通过 openPlayer 启动播放器
- **WHEN** H5 详情页用户点击某集
- **THEN** H5 调用 `window.DramaFlowBridge.openPlayer(episodeId, dramaId, episodeNumber)`，Android 启动 PlayerActivity

#### Scenario: H5 通过 playVideo 直接播放
- **WHEN** H5 已获取签名 URL 并调用 `playVideo`
- **THEN** Android 使用传入的 `videoUrl` 直接初始化 ExoPlayer，不再请求签名接口

#### Scenario: 参数缺失
- **WHEN** `openPlayer` 或 `playVideo` 的必传参数为 null/undefined
- **THEN** Android 端忽略调用，不崩溃；H5 端不应传入 null

---

### Requirement: Token 同步方法

`DramaFlowBridge` SHALL 提供读取 Android 本地 Token 的方法，使 H5 无需重复登录。

**Scope**: Android + H5  
**方法签名**:
```
getAccessToken(): string
getRefreshToken(): string
```

#### Scenario: H5 启动时同步 Token
- **WHEN** H5 的 `main.ts` 在 WebView 环境中执行
- **THEN** 调用 `DramaFlowBridge.getAccessToken()` 获取 Token 并写入 localStorage，H5 后续请求携带此 Token

#### Scenario: 未登录时返回空字符串
- **WHEN** Android 端无有效 Token（未登录或已登出）
- **THEN** `getAccessToken()` 返回空字符串 `""`，H5 跳转登录页

---

### Requirement: 可选扩展方法

`DramaFlowBridge` MAY 提供分享和登录通知方法，H5 调用前 SHALL 检查方法是否存在。

**Scope**: Android + H5  
**方法签名**:
```
shareDrama?(id: number, title: string): void
login?(token: string): void
logout?(): void
```

#### Scenario: 条件调用可选方法
- **WHEN** H5 需要调用可选方法（如 `shareDrama`）
- **THEN** 先判断 `typeof window.DramaFlowBridge.shareDrama === 'function'` 为真后再调用

#### Scenario: H5 登出通知 Android
- **WHEN** H5 用户点击登出并完成
- **THEN** 若 `window.DramaFlowBridge.logout` 存在，H5 调用之，Android 同步清除本地 Token
