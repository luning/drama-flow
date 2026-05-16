# DramaFlow 原型

## 目录结构

```
prototype/
├── index.html          # 原始手写原型（保留，全9页面在一个文件中）
├── generated/          # 从 screen spec 自动生成的原型
│   ├── home.html       # 首页（生成自 specs/screens/home.yaml）
│   └── detail.html     # 详情页（生成自 specs/screens/detail.yaml）
└── README.md           # 本文件
```

## 生成方式

```bash
# 从 screen spec 生成所有原型页面
python scripts/design-system/generate_prototype.py

# 生成单个页面
python scripts/design-system/generate_prototype.py --screen home

# 输出到 stdout 查看
python scripts/design-system/generate_prototype.py --stdout
```

## 生成的页面

- 引用 `design-system/tokens/tokens.css` — 所有颜色通过 CSS 变量
- 引用 `design-system/components/components.css` — 共享组件样式
- 包含 `@component` 注释标记 — 标记每个组件的生成边界

## 与 H5/Android 的关系

```
specs/screens/home.yaml
    │
    ├── generate_prototype.py ──> prototype/generated/home.html  (给 PM 看)
    └── generate_h5_template.py ──> h5/src/pages/Home.vue 骨架     (给研发用)
```

两者同源，改 screen spec，两个产物同步更新。Android 端可通过 `generate_android.py` 从 tokens.css 生成 colors.xml 和 styles.xml。
