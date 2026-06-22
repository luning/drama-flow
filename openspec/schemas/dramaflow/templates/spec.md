<!-- 
Scope 标注（在每个 Requirement 下注明所属端）：
  **Scope**: Backend | Android | H5 | JSBridge  （可多选，用 + 连接，如 Backend + H5）

API 描述约定（仅 Backend/JSBridge 端 Requirement 使用）：
  **Endpoint**: `METHOD /path/{param}`
  **Request**: `{ field: type, ... }` 或 Header 说明
  **Response NNN**: `{ field: type, ... }` — 说明

格式规则：
  - 每个 Requirement 至少包含一个 Scenario
  - Scenario 使用 #### (4 个 #)，不用 3 个 # 或 bullet
  - 规范性要求用 SHALL / MUST，非规范性用 MAY / SHOULD
  - 新增用 ## ADDED Requirements，修改用 ## MODIFIED Requirements，删除用 ## REMOVED Requirements
-->

## ADDED Requirements

### Requirement: <!-- requirement name -->

**Scope**: <!-- Backend | Android | H5 | JSBridge -->

<!-- requirement text (use SHALL/MUST for normative) -->

<!-- For Backend/JSBridge requirements, add API description:
**Endpoint**: `METHOD /path`
**Request**: `{ field: type }`
**Response 200**: `{ field: type }` — description
-->

#### Scenario: <!-- scenario name -->
- **WHEN** <!-- condition -->
- **THEN** <!-- expected outcome -->
