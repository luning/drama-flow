---
name: spec-validate
description: AC 覆盖检查——对比 SPEC.md 中的验收标准与实际测试覆盖，输出覆盖率报告。当用户说"检查 AC 覆盖"、"跑一下 spec validate"、"验证验收标准"、"覆盖率检查"、"spec 检查"时触发。
---

# spec-validate

逐条检查 SPEC.md 中的验收标准（AC）是否被测试用例覆盖，输出覆盖率报告。

## 执行步骤

### 1. 提取 AC

1. 读取 [SPEC.md](/SPEC.md)
2. 提取所有以 `AC-` 开头的验收标准
3. 列出每个 AC 的 ID 和描述

### 2. 分析测试覆盖

1. 读取 [tests/test_api_all.py](/backend/tests/test_api_all.py) 和 [tests/test_auth.py](/backend/tests/test_auth.py)
2. 检查哪些 AC 有对应的测试方法
3. 对于未覆盖的 AC，标记为 `❌ 未覆盖`

### 3. 运行测试

1. 激活虚拟环境并运行 `python -m pytest tests/ -v`
2. 记录通过的测试和失败的测试

### 4. 输出覆盖率报告

报告格式：

```json
{
  "ac_total": 20,
  "ac_covered": 18,
  "ac_missing": 2,
  "coverage_rate": "90%",
  "test_pass_rate": "100%",
  "details": {
    "covered": ["AC-DRAMA-01", "AC-DRAMA-02", ...],
    "missing": ["AC-EP-03", ...],
    "failed_tests": []
  }
}
```

## 注意事项

- 如果 AC 在新迭代中被标记为 `[Changed]`，仍按最新版本检查
- 不要求每个 AC 都有独立测试方法，一个测试可以覆盖多个 AC
