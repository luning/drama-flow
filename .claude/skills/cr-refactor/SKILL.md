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
| 重复 | 是否存在可提取的重复逻辑（3 次以上重复）|
| 状态管理 | 状态机是否完整（IDLE→BUFFERING→READY→PLAYING↔PAUSED→ERROR/ENDED）|
| 测试 | 新功能是否有对应测试 |

### 3. 输出结构化报告

```json
{
  "summary": {
    "files_reviewed": 5,
    "issues_found": 3,
    "critical": 0,
    "major": 1,
    "minor": 2
  },
  "issues": [
    {
      "severity": "major",
      "file": "backend/app/services/drama_service.py",
      "line": 42,
      "category": "architecture",
      "description": "Service 层直接调用了 db.query()，但此处可以提取为 Repository 方法",
      "suggestion": "将剧集查询提取到 DramaRepository.get_by_category()"
    }
  ],
  "refactoring_candidates": [
    {
      "priority": "high",
      "pattern": "重复逻辑",
      "description": "list_dramas 和 get_drama_detail 都计算了 episode_count，可提取为公用方法",
      "estimated_effort": "5min"
    }
  ],
  "test_coverage_note": "当前修改的文件有 {n} 个对应测试"
}
```

### 4. 重构建议优先级

- **High**：重复 3 次以上的代码、架构违规、安全隐患
- **Medium**：命名不规范、缺少错误处理
- **Low**：注释风格、格式调整
