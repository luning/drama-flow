## 1. H5 Detail 页 — 播放交互

- [x] 1.1 在 Detail.vue 中实现 `playFirst()`：调用 `window.DramaFlowBridge.playVideo()` 播放第一集
- [x] 1.2 在 EpisodeList.vue 中添加集数点击事件，调用 `window.DramaFlowBridge.playVideo()` 播放对应集
- [x] 1.3 确保 EpisodeList.vue 通过 emits 向父组件上报点击事件，父组件负责 JSBridge 调用

## 2. H5 Detail 页 — 加载与错误状态

- [x] 2.1 在 drama store 中添加 `loading` 和 `error` 状态变量
- [x] 2.2 在 Detail.vue 中添加骨架屏加载状态（数据加载中显示占位 UI）
- [x] 2.3 在 Detail.vue 中添加错误处理：后端 404 时显示"剧集不存在"及返回按钮
- [x] 2.4 在 Detail.vue 中添加网络错误时显示"网络加载失败"及重试按钮

## 3. H5 Detail 页 — Design Token 替换

- [x] 3.1 替换 Detail.vue 中的硬编码色值为 CSS 变量（`var(--primary)`、`var(--bg)`、`var(--rating)` 等）
- [x] 3.2 替换 EpisodeList.vue 中的硬编码色值为 CSS 变量

## 4. Android WebView 导航支持

- [x] 4.1 确保 HomeFragment WebView 支持 H5 内 hash 路由导航（`/detail/:id`），点击剧集卡片后正确跳转到详情页
- [x] 4.2 注入 JSBridge 到 WebView，确保 H5 可调用原生播放功能

## 5. 测试与验证

- [x] 5.1 运行后端 pytest，确认现有 43 个测试全部通过
- [ ] 5.2 手动验证用户路径：首页 → 点击剧集 → 详情页展示 → 点击播放 → 调用 PlayerActivity
- [ ] 5.3 验证 404 和网络错误场景的 UI 表现
