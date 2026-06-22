## Context

DramaFlow 已有 3 个 OpenSpec spec（player-state-machine、video-player、video-sign-url），均使用默认的 `spec-driven` schema。当前 spec 模板对"端"归属（Backend/Android/H5/JSBridge）无显式标注，REST 接口描述散落在 scenario 正文中，无固定格式。核心业务能力（认证、目录、观看记录、JSBridge）缺乏 spec，导致 AI 执行变更时无法对照规格自检。

## Goals / Non-Goals

**Goals:**
- Fork `spec-driven` 创建项目本地 schema `dramaflow`，加入端标注和 API 描述扩展
- 为 4 个缺失核心能力创建 spec 文件
- 所有 spec 使用统一的 SHALL/MUST + Scenario 格式，与现有 spec 风格一致

**Non-Goals:**
- 不修改现有 3 个 spec 的内容（不破坏已归档变更的可追溯性）
- 不迁移到完全不同的规格语言（OpenAPI、AsyncAPI）—— OpenSpec 已满足需求
- 不实现任何业务功能代码

## Decisions

### D1：Fork spec-driven 而非从零创建 schema

**选择**：`openspec schema fork spec-driven dramaflow`  
**理由**：保留 proposal → specs → design → tasks 的现有流程，只在 `spec.md` 模板增加「端」标注块（`## Scope: Backend | Android | H5 | JSBridge`）和 API 描述约定，最小改动。  
**替代方案**：`openspec schema init dramaflow`（从空白创建）—— 成本高，且现有团队已熟悉 spec-driven 流程。

### D2：API 描述嵌入 Requirement，不单独 artifact

**选择**：在 spec.md 的 Requirement 下增加 `**Endpoint**`、`**Request**`、`**Response**` 字段行，而非新增独立 `api-spec` artifact。  
**理由**：OpenSpec schema 的 artifact 扩展属于实验性功能，复杂度高；嵌入 Requirement 更轻量且与现有工具兼容。  
**替代方案**：新增 `api-spec` artifact —— 需要修改 schema.yaml 结构，AI 指令维护成本增加。

### D3：4 个新 spec 的范围划定

| Spec | 端 | 核心职责 |
|------|---|---------|
| `user-auth` | Backend + Android + H5 | JWT 发放/刷新/登出；EncryptedSharedPreferences 存储；登录页 H5 跳转 |
| `drama-catalog` | Backend + H5 | 剧目列表分页、分类筛选、搜索、详情返回格式 |
| `watch-record` | Backend + Android + H5 | 进度上报（每 5 秒或暂停时）、继续观看列表查询 |
| `jsbridge-protocol` | Android + H5 | `window.DramaFlowBridge` 方法签名、回调格式、异步事件 |

## Risks / Trade-offs

- **风险：dramaflow schema 与上游 spec-driven 更新不同步** → 缓解：在 schema README 中记录 fork 来源版本，定期对比 `openspec schema validate dramaflow`。
- **风险：spec 描述与实际实现出现漂移** → 缓解：CLAUDE.md 已要求"生成代码后逐条自检 AC"，spec 变更标注 `[Changed]`。
- **取舍：API 描述嵌入 spec 而非独立文件** → 好处是简单，代价是无法直接生成 OpenAPI 文档；当前阶段可接受，后期可引入 openapi-spec artifact。

## Migration Plan

1. `openspec schema fork spec-driven dramaflow` 生成本地 schema
2. 修改 `openspec/schemas/dramaflow/templates/spec.md`，增加端标注约定和 API 字段说明
3. 依次创建 4 个 spec 文件（user-auth → drama-catalog → watch-record → jsbridge-protocol）
4. 更新 `openspec/.openspec.yaml` 的 `defaultSchema` 为 `dramaflow`（可选，不影响现有 spec）
5. 无需回滚策略：新增文件，不修改已有代码
