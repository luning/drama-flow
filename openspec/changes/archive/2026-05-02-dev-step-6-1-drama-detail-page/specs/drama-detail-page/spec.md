## ADDED Requirements

### Requirement: 详情页展示完整剧集信息

详情页 SHALL 展示剧集的完整信息：标题、描述、评分、分类、年份、状态、总集数。

#### Scenario: 成功加载剧集详情
- **WHEN** 用户打开某剧集的详情页
- **THEN** 页面上显示剧集的标题、描述、评分（星级+数字）、分类标签、年份、状态（连载/完结）和总集数

#### Scenario: 加载中显示骨架屏
- **WHEN** 用户从首页导航到详情页，数据尚未加载完成
- **THEN** 页面显示骨架屏加载状态（非空白页）

#### Scenario: 剧集不存在显示错误提示
- **WHEN** 用户访问不存在的剧集 ID（后端返回 404）
- **THEN** 详情页显示友好错误提示，并提供返回首页的按钮

---

### Requirement: 从首页导航到详情页

用户从首页剧集列表中点击任意剧集卡片，SHALL 能跳转到对应的详情页。

#### Scenario: 点击剧集卡片进入详情
- **WHEN** 用户在首页 H5 中点击某个剧集卡片
- **THEN** H5 路由导航到 `/detail/{dramaId}`，页面切换到详情页视图
- **AND** 详情页自动加载该剧集的信息和集数列表

---

### Requirement: 通过 JSBridge 一键播放

详情页的"立即观看"按钮 SHALL 调用 JSBridge 播放第一集。

#### Scenario: 点击立即观看按钮
- **WHEN** 用户在详情页点击"立即观看"按钮
- **THEN** 调用 `window.DramaFlowBridge.playVideo(episodeId, videoUrl, title)` 通知 Android 原生播放器
- **AND** Android 端打开 PlayerActivity 开始播放

---

### Requirement: 集数列表支持点击播放

集数列表中的每一集 SHALL 可点击，点击后调用 JSBridge 播放对应剧集。

#### Scenario: 点击指定集数播放
- **WHEN** 用户在详情页的集数列表中点击某一集
- **THEN** 调用 `window.DramaFlowBridge.playVideo(episodeId, videoUrl, title)` 通知 Android 原生播放器
- **AND** Android 端打开 PlayerActivity 从该集开始播放

---

### Requirement: Design Token 替换硬编码色值

详情页和集数列表组件中的所有颜色值 SHALL 引用 `design_system.md` 中定义的 CSS 变量。

#### Scenario: 色值引用 Design Token
- **WHEN** 检查 Detail.vue 和 EpisodeList.vue 的样式代码
- **THEN** 所有颜色值应使用 `var(--primary)`、`var(--bg-card)`、`var(--rating)` 等 CSS 变量而非硬编码十六进制色值

#### Scenario: 不可见样式变化
- **WHEN** 对比修改前后的详情页视觉表现
- **THEN** 页面外观应与修改前一致（仅引用方式变化，非视觉变化）

---

### Requirement: 网络错误处理

详情页在网络请求失败时 SHALL 提供错误反馈。

#### Scenario: 网络请求失败
- **WHEN** 详情页数据加载因网络问题失败
- **THEN** 页面显示"网络加载失败"提示，并提供重试按钮
- **AND** 点击重试后重新发起数据请求
