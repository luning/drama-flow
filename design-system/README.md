# DramaFlow 可执行设计系统 (v2.0)

## 概述

设计系统是 DramaFlow 的**唯一视觉真相源（Single Source of Truth）**。
Figma 是创作入口，但规范以本仓库中的文件为准。

## 目录结构

```
design-system/
├── tokens/                    # Layer 1: Design Tokens
│   ├── tokens.css             # CSS 自定义属性（prototype & H5 引用）
│   └── tokens.ts              # TypeScript 版本（组件中 import）
│
├── specs/                     # Layer 2: Specs & Constraints
│   ├── constraints.md         # 业务约束（可自动检查）
│   ├── design-rules.md        # AI 生成规则（Skill 自动注入）
│   └── screens/               # 屏幕规格（平台无关）
│       ├── home.yaml
│       └── detail.yaml
│
├── components/                # Layer 3: Component Specs
│   ├── components.yaml        # 平台无关组件规格（单一源）
│   ├── components.css         # 生成：CSS 组件样式（H5 引用）
│   └── index.html             # 组件 Gallery（可视化验证）
│
└── exports/                   # Layer 4: Platform Exports
    ├── h5/
    │   └── designsystem.css   # 一键导入：tokens + components.css
    └── android/
        ├── colors.xml         # 生成：Android 颜色资源
        └── styles.xml         # 生成：Android 组件样式
```

## 架构流水线

```
Figma (Designer)
    │
    ├── Tokens Studio Plugin → DTCG JSON
    │       │
    │       └── figma_sync_tokens.py → tokens.css + tokens.ts
    │
    ├── Figma REST API (Components)
    │       │
    │       └── figma_sync_components.py → components.yaml
    │               │
    │               ├── generate_css.py → components.css → H5
    │               └── generate_android.py → colors.xml + styles.xml → Android
    │
    └── Figma REST API (Pages, auto-layout required)
            │
            └── figma_sync_screens.py → screens/*.yaml
                    │
                    ├── generate_prototype.py → prototype HTML
                    └── generate_h5_template.py → Vue page templates
```

## 四层引用方式

| 层 | H5 引用 | Android 引用 |
|----|---------|-------------|
| Token | `var(--color-primary)` | `@color/color_primary` |
| Component | `class="btn-primary"` | `style="@style/DramaFlow.Button.Primary"` |
| Screen | Vue template from screen spec | (planned) |
| Check | `check_tokens.py --path h5/src` | `check_tokens.py --path android/...` |

## 合规检查

```bash
# Layer 1: 无硬编码色值，CSS 变量名正确
python scripts/check/check_tokens.py

# Layer 2: 业务约束（单 btn-primary、loading 态、触摸目标等）
python scripts/check/check_constraints.py

# Layer 3: 组件使用模式
python scripts/check/check_components.py
```

## 变更流程

1. **设计师** 在 Figma 中调整 Token 或组件
2. **Tokens Studio** 同步到 DTCG JSON
3. 运行 `figma_sync_tokens.py` 更新 `tokens.css` / `tokens.ts`
4. 运行 `generate_css.py` + `generate_android.py` 更新平台导出
5. 运行 compliance check 确认无违规
6. PR 合并 → CI 自动重建 prototype & 部署预览

## 设计角色参与方式

| 方式 | 门槛 | 适用场景 |
|------|------|---------|
| GitLab 网页编辑 constraints.md / design-rules.md | 零门槛 | 修改业务规则 |
| Tokens Studio 同步 Token | Figma 内操作 | 调整色值/间距 |
| CODEOWNERS 审批 | 需 Git 权限 | 设计负责人把关 |
