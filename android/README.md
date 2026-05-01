# DramaFlow Android

Kotlin 原生 Android 客户端。

## 技术栈

- Kotlin + Android Studio
- ViewModel + LiveData 架构
- Navigation Component 导航
- Retrofit + OkHttp + Moshi 网络请求与序列化
- ExoPlayer (Media3) 视频播放
- EncryptedSharedPreferences 安全存储
- WebView 内嵌 Vue3 H5

> ⚠️ **Media3 说明**：本项目的播放器使用 `androidx.media3:media3-exoplayer`（Google 新一代媒体库品牌，2023 年取代旧版 `com.google.android.exoplayer`）。搜索旧版 ExoPlayer 教程时注意版本差异，旧版 `ExoPlayer.Builder` 的 API 在 Media3 中已迁移至 `ExoPlayer.Builder`（包名从 `com.google.android.exoplayer2` 改为 `androidx.media3.exoplayer`）。

## 目录结构

```
android/
├── app/
│   ├── src/main/
│   │   ├── java/com/dramaflow/
│   │   │   ├── DramaFlowApp.kt          # Application
│   │   │   ├── MainActivity.kt          # 主 Activity + 底部导航
│   │   │   ├── auth/                    # 认证模块
│   │   │   │   ├── ui/LoginFragment.kt
│   │   │   │   ├── ui/RegisterFragment.kt
│   │   │   │   └── viewmodel/AuthViewModel.kt
│   │   │   ├── home/                    # 首页模块
│   │   │   │   ├── ui/HomeFragment.kt    # WebView 容器
│   │   │   │   └── viewmodel/HomeViewModel.kt
│   │   │   ├── detail/                  # 详情模块
│   │   │   │   └── viewmodel/DetailViewModel.kt
│   │   │   ├── player/                  # 播放器模块
│   │   │   │   ├── ui/PlayerActivity.kt
│   │   │   │   └── viewmodel/PlayerViewModel.kt
│   │   │   ├── data/                    # 数据层
│   │   │   │   ├── remote/              # Retrofit API 定义
│   │   │   │   ├── local/              # PreferencesManager
│   │   │   │   └── repository/         # 数据仓库
│   │   │   └── common/                 # JSBridge 等通用工具
│   │   └── res/                        # 布局/资源
│   ├── build.gradle.kts
├── build.gradle.kts
├── settings.gradle.kts
└── gradle.properties
```

## 架构约束

- Fragment 只负责 UI 绑定，业务逻辑在 ViewModel
- 网络请求统一通过 Repository 层调用，Fragment 不直接持有 API 实例
- WebView 内容页面（首页/详情）由 Vue3 H5 渲染，通过 JSBridge 与原生通信
- Token 存储使用 EncryptedSharedPreferences，禁止明文存 SharedPreferences
- Player Activity 使用 ExoPlayer Media3，状态管理由 PlayerViewModel 驱动
