# 基线测试输出（不带 skill）

**运行时间：** 2026-06-25  
**场景：** scenario.md 的测试代码，Agent 无 skill

## 实际输出摘要

Agent 使用口语化描述代替规范技巧名：
- 说 "Extract helper / service method"，而非 **Extract Function** / **Move Method to Service Layer**
- 说 "Eliminate N+1 with a joined load / subquery"，而非 **Eager Load / SQL Aggregation**
- 说 "DRY / Extract function"（混用，不规范）

没有提运行测试的步骤——直接输出了重构后代码，未提 pytest 基线。

没有给出应用顺序的理由——只是顺序列出发现的问题，没有解释为什么先修 N+1 再 Extract。

识别到的 smells 不完整：
- ✅ 发现了 N+1
- ✅ 发现了重复逻辑
- ✅ 发现了业务逻辑在 route 层
- ❌ 未发现 `drama.status == 1` 是 Magic Literal

## 结论（对 skill 编写的启示）

1. 技巧名称需要在 skill 里**规范化且显眼**，Agent 会用自己的措辞绕过
2. pytest 步骤必须作为**强制前置条件**出现，而非建议
3. 应用顺序需要给出**决策理由**，不能只列清单
4. Magic Literal 这个 smell 容易被忽略，需要在 Smell→Technique Map 里明确列出
