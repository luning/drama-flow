---
name: spec-validate
description: AC 覆盖检查与自动补测试——提取 SPEC.md AC，对比测试覆盖，默认自动补缺并运行测试，加 --check 只读。触发："spec-validate"、"生成测试"、"补充测试"、"覆盖检查"。
---

# spec-validate

默认补测试，加 `--check` 只读报告。

| 模式 | 命令 | 行为 |
|------|------|------|
| **Default** | `spec-validate` | 补缺 + 更新 `[Changed]` AC 测试 → 全量 pytest → 重试 2 轮 |
| **Check（只读）** | `spec-validate --check` | 仅覆盖率报告，不写文件 |

## 公共步骤

### 1. 提取 AC 清单

读 [SPEC.md](/SPEC.md)，提取所有 `AC-` 开头的验收标准，按领域分组，标记 `[Changed]`。

### 2. 分析测试覆盖

扫描 `backend/tests/` 下所有 `test_*.py`，提取 docstring 中的 AC-ID：

- 已覆盖 → `AC-ID → test_xxx`
- `[Changed]` → 定位对应测试，准备更新
- 未覆盖 → 待生成

跳过非后端 AC（`AC-VIS-*`、`AC-PLAYER-*` 等）。

### Default 模式（写入）

### 3. 生成/更新测试

按领域归属文件：

| 领域 | 文件 | 类 |
|------|------|-----|
| Auth | `test_auth.py` | `TestAuth` |
| Drama | `test_dramas.py` | `TestDramas` |
| Episode | `test_episodes.py` | `TestEpisodes` |
| WatchRecord | `test_watch_records.py` | `TestWatchRecords` |
| Health | `test_health.py` | `TestHealth` |

- 已有文件 → 对应类末尾追加
- 新建 → 参考 [test_auth.py](/backend/tests/test_auth.py) 的导入和 fixture
- `[Changed]` AC → 修改已有测试的断言/参数，保留 AC-ID 引用

**新增模板**：
```python
def test_{action}_{scenario}(self, <fixtures>):
    """<AC-ID>: 描述"""
    response = client.<method>("<path>", {json/headers})
    assert response.status_code == <code>
    data = response.json()
    {assertions}
```

**端点场景**：POST → 201/409/422/401；PUT → 200/404/401；DELETE → 200/204/404/401；GET list → 200/pagination/401；GET detail → 200/404。

**Fixture**：能用真实服务不用 mock，仅异常场景用 monkeypatch。

### 4. 运行全量测试

```bash
cd backend && python -m pytest tests/ -v
```

### 5. 处理失败（最多 2 轮）

根据失败类型修正（断言→按实际响应修、422→修请求参数、401→检查 auth_header、404→检查路径、fixture→检查签名、语法→修代码）。3 次不过输出失败报告。

### 6. 输出

```
SPEC AC: N 个
已覆盖: N  已变更: N → 已更新  新增: N
测试结果: N passed, N failed
失败详情: ...
```

## Check 模式（只读）

只运行 `python -m pytest tests/ -v`，输出文本覆盖率报告。

## 安全边界

- 只追加不修改（除非 `[Changed]`）
- 不编造 AC-ID、不修改 conftest.py
- 仅后端 API 测试
- `--check` 不写任何文件
