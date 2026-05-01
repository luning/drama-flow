# DramaFlow H5

Vue3 + Vite 前端，内嵌于 Android WebView。

## 技术栈

- Vue 3.4 + Composition API + TypeScript
- Vite 5 + vue-router 4
- Pinia 状态管理
- Axios HTTP 客户端

## 目录结构

```
h5/
├── src/
│   ├── api/          # API 封装（auth/dramas/watchRecord）
│   ├── components/   # 通用组件（Banner/DramaCard/EpisodeList/...）
│   ├── pages/        # 页面组件（Home/Detail）
│   ├── stores/       # Pinia 状态（auth/home/drama）
│   ├── router/       # 路由配置
│   ├── App.vue       # 根组件
│   ├── main.ts       # 入口文件
│   └── style.css     # 全局样式 + 设计 Token
├── index.html
├── vite.config.ts    # Vite 配置 + API 代理
└── package.json
```

## 快速开始

```bash
npm install
npm run dev     # 开发模式，默认 :5173
npm run build   # 构建输出到 dist/
```

## 架构约束

- API 调用统一通过 `src/api/` 封装，不直接使用 axios
- 页面组件只负责布局，数据逻辑在 Store 中
- 设计 Token 统一在 `style.css` 中定义，组件不写死颜色值
- Vue Router 使用 hash 模式（兼容 Android WebView 文件协议）
