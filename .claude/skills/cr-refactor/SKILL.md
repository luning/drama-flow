---
name: cr-refactor
description: 代码审查（Code Review）与重构建议。当用户说"审查代码"、"做 CR"、"重构建议"、"代码评审"、"review 一下"、"/review"时触发。输出 CR 清单和重构优先级。
---

# cr-refactor

分析指定路径的代码变更，输出 Code Review 清单和重构建议。

## 工作流程

### 1. 理解范围

- 如果用户指定了文件路径，分析该路径
- 如果用户在 git 分支上且未指定路径，分析当前分支的变更（与目标分支的 diff）
- 如果既无路径也无 git 上下文，列出可选项让用户指定

### 2. 审查维度

从以下维度审查代码：

| 维度 | 检查内容 |
|------|---------|
| 架构合规 | 是否违反 CLAUDE.md 中的架构约束（跨模块调用、分层违规）|
| 命名规范 | 是否符合项目命名规范（snake_case / camelCase / PascalCase）|
| 安全 | Token 硬编码、SQL 注入、敏感信息暴露 |
| 异常处理 | 是否缺少错误处理、是否暴露技术细节给用户 |
| 重复代码 | 是否存在可提取的重复逻辑（3 次以上重复）|
| 死代码 | 未使用的变量/函数/import、注释掉的代码、不可达分支 |
| 可读性 | 实现是否过于 tricky、命名是否误导、逻辑是否难以理解或过度设计 |
| 状态管理 | 状态机是否完整（IDLE→BUFFERING→READY→PLAYING↔PAUSED→ERROR/ENDED）|
| 测试 | 新功能是否有对应测试 |

### 3. 输出报告格式

按问题分类输出，每个问题包含：

- **严重级别**：Critical / Major / Minor
- **位置**：`文件路径:行号`
- **问题描述与改进建议**

示例：

```
## CR 报告

### Critical
无

### Major
- `backend/app/services/drama_service.py:42` — Service 层直接调用 db.query()，应提取到 Repository
  建议：将剧集查询提取为 DramaRepository.get_by_category()

### Minor
- `backend/app/services/drama_service.py:55` — 变量命名 `x` 含义不明
  建议：改为 `episode_count`

## 重构候选

| 优先级 | 模式 | 说明 | 预估工作量 |
|--------|------|------|-----------|
| High | 重复逻辑 | list_dramas 和 get_drama_detail 都计算了 episode_count | 5min |

## 测试覆盖
当前修改的文件有 {n} 个对应测试
```

### 4. 重构建议优先级

- **High**：重复 3 次以上的代码、架构违规、安全隐患
- **Medium**：命名不规范、缺少错误处理
- **Low**：注释风格、格式调整
