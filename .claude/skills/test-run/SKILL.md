---
name: test-run
description: 运行 DramaFlow 后端 pytest 测试并输出结构化报告。当用户说"跑测试"、"运行测试"、"跑 pytest"、"测试一下"、"run tests"时触发。
---

# test-run

运行后端的 pytest 测试套件，输出结构化的测试报告。

## 执行步骤

1. 激活虚拟环境 `source backend/drama-flow/bin/activate`
2. 进入 `backend/` 目录
3. 确认测试数据库 `test.db` 存在（由 conftest.py 自动管理）
4. 运行测试并捕获输出

```bash
python -m pytest tests/ -v 2>&1
```

### 参数

- `--path`：指定测试文件或目录，默认 `tests/`
- `--verbose` / `-v`：详细输出（默认启用）
- `--coverage`：是否输出覆盖率报告（需安装 pytest-cov）

## 结构化输出

```json
{
  "status": "passed | failed | error",
  "summary": {
    "total": 47,
    "passed": 47,
    "failed": 0,
    "errors": 0,
    "duration_seconds": 6.2
  },
  "details": [
    {
      "test": "tests/test_api_all.py::TestAuth::test_register_success",
      "status": "PASSED"
    },
    {
      "test": "tests/test_api_all.py::TestAuth::test_register_weak_password",
      "status": "PASSED"
    }
  ],
  "failed_tests": []
}
```

## 失败处理

- 如果有测试失败，列出每个失败测试的断言错误信息
- 如涉及数据库状态问题，建议用户运行 `db-reset` 重置数据后重试
