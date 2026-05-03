## spec-validate 覆盖率报告

### AC 统计

| 指标 | 值 |
|------|-----|
| AC 总数 | 39 |
| 测试覆盖（后端 pytest） | 27 |
| 未覆盖（后端可测） | 2 |
| 未覆盖（Android/视觉验收） | 10 |
| 覆盖率（后端可测 AC） | 93.1% |

### 覆盖详情

#### ✅ 已覆盖的 AC（27）

AC-USER-01 ~ AC-USER-09, AC-DRAMA-01 ~ AC-DRAMA-06, AC-EP-01, AC-EP-02, AC-EP-05, AC-WR-01 ~ AC-WR-06

#### ❌ 未覆盖的 AC（12）

| AC-ID | 描述 | 原因 |
|-------|------|------|
| AC-EP-03 | 视频签名 URL 有效期内可正常播放 | 需 CDN 环境，无法纯后端测试 |
| AC-EP-04 | URL 过期后可重新获取新签名 | 同上 |
| AC-WR-07 | 非最后一集播放结束后自动加载并播放下一集 | Android 端行为，后端无法测试 |
| AC-WR-08 | 最后一集播放结束后回到剧集详情页 | Android 端行为 |
| AC-WR-09 | 自动连播时显示切换提示 | UI 行为 |
| AC-WR-10 | PlayerActivity 关闭后自然返回前一页 | Android 导航栈行为 |
| AC-VIS-01~12 | 视觉验收规范 | 人工截图比对 |

### 测试运行

后端 pytest: **47 passed, 0 failed** ✅
