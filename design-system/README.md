# DramaFlow 可执行设计系统

```
design-system/
├── tokens.css        ← CSS 变量（单一真相源，prototype 和 h5 直接引用）
├── tokens.ts         ← TypeScript 版本（Vue/React 组件引用）
├── constraints.md    ← 业务约束与尺寸规范
├── design-rules.md   ← AI 生成规则（Prototype Skill 自动注入此文件）
└── components/
    └── index.html    ← 组件 Gallery（可视化验证所有组件在 Token 下的渲染效果）
```

## 变更流程

1. 修改 `tokens.css`（需经设计负责人 Review）
2. 刷新 `components/index.html` 验证渲染效果
3. 运行 `python scripts/check_design_tokens.py` 确认无遗留 hardcoded 色值
4. PR 合并后，所有引用 tokens.css 的文件自动同步更新
