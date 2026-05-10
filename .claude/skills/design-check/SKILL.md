---
name: design-check
description: Design Token 合规检查——扫描前端文件中的 hardcoded 色值，确保代码引用 CSS 变量。触发："design-check"、"检查 Token"、"合规检查"、"token check"、"check design"、"色值检查"。
---

# design-check

扫描前端文件是否存在 hardcoded 色值（应改用 `var(--token-name)` CSS 变量）。

| 模式 | 命令 | 行为 |
|------|------|------|
| **Default** | `design-check` | 扫描 → 报告违规 → 提供修复建议 |
| **Fix** | `design-check --fix` | 扫描 → 对已知 Token 色值自动替换 |

## 工作流

### 1. 运行检查脚本

```bash
python scripts/check_design_tokens.py
```

如需指定路径：

```bash
python scripts/check_design_tokens.py --path prototype h5/src
```

### 2. 解读结果

**✅ 通过**：
```
✅  全部通过！0 个 hardcoded 色值
```

**❌ 有违规（示例）**：
```
❌  prototype/index.html
    L42    #6c5ce7      →  var(--color-primary)
           color: #6c5ce7; /* 应该是 var(--color-primary) */
```

每条违规包含：
- 文件路径 + 行号
- 发现的 hardcoded 色值
- 对应的 CSS 变量建议（基于 `design-system/tokens.css`）
- 上下文代码片段

### 3. Fix 模式（--fix）

对于有对应 Token 的色值，使用 Edit 工具自动替换：

1. 读取 `design-system/tokens.css`，获取所有变量映射
2. 运行脚本获取违规列表
3. 对每处有对应 Token 的违规，调用 Edit 工具替换：
   - `#6c5ce7` → `var(--color-primary)`
   - `#0f0f23` → `var(--bg-primary)`
   - ...（参考 scripts/check_design_tokens.py 中的 TOKEN_MAP）
4. 替换范围：CSS `<style>` 块 + HTML `style=""` 属性
5. **不替换** JS 数据对象中的色值（如 DRAMAS 数组）
6. 替换后重新运行检查，确认通过

### 4. 输出摘要

```
扫描结果: N 个文件
违规总数: M 处
  · 有对应 Token（可自动替换）: X 处
  · 无对应 Token（需人工审查）: Y 处
```

## 说明

视觉验收的三层防线：

```
代码合规（本 Skill）← 最早、最便宜
    ↓ 通过
渲染正确（Playwright 截图对比）
    ↓ 通过
体验质量（人工走查）← 最晚、最贵
```

**不检查什么**：
- JS 数据对象中的色值（如 DRAMAS 数组中的 `color:'#6c5ce7'`）——这些是数据
- `#000`/`#fff` 纯黑白——允许在视频播放器等明确场景使用
- 注释中的色值
