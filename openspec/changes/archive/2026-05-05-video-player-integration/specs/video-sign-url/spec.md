## ADDED Requirements

### Requirement: 视频签名 URL 刷新

系统 SHALL 为已存在的剧集单集生成有时效性的 CDN 签名播放地址。

#### Scenario: 获取单集视频签名 URL
- **WHEN** 客户端 GET `/api/episodes/{episode_id}/video-url`
- **THEN** 返回 `200 OK` + `{ url: string, expires_at: string }`

#### Scenario: 签名 URL 有效期内可播放
- **WHEN** 客户端使用返回的 URL 请求视频流
- **THEN** 服务端返回 200 并可正常播放

#### Scenario: URL 过期后可重新获取
- **WHEN** 客户端在签名 URL 过期后再次请求 `/api/episodes/{episode_id}/video-url`
- **THEN** 返回新的有效签名 URL

#### Scenario: 单集不存在时返回 404
- **WHEN** 请求不存在的 `episode_id`
- **THEN** 返回 `404 Not Found`

#### Scenario: TOS 服务不可用时返回 503
- **WHEN** TOS 密钥未配置或签名服务异常
- **THEN** 返回 `503 Service Unavailable` + 明确错误信息
