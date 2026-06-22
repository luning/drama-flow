## 1. 创建本地 DramaFlow Schema

- [x] 1.1 执行 `openspec schema fork spec-driven dramaflow` 生成本地 schema 目录
- [x] 1.2 修改 `openspec/schemas/dramaflow/templates/spec.md`：在文件顶部增加 `**Scope**: <Backend|Android|H5|JSBridge>` 标注说明
- [x] 1.3 在 `openspec/schemas/dramaflow/templates/spec.md` 增加 API 描述约定说明（Endpoint / Request / Response 字段）
- [x] 1.4 执行 `openspec schema validate dramaflow` 验证 schema 合法

## 2. 归档新 Spec 到 openspec/specs/

- [x] 2.1 将 `user-auth/spec.md` 从 change 目录归档到 `openspec/specs/user-auth/spec.md`
- [x] 2.2 将 `drama-catalog/spec.md` 从 change 目录归档到 `openspec/specs/drama-catalog/spec.md`
- [x] 2.3 将 `watch-record/spec.md` 从 change 目录归档到 `openspec/specs/watch-record/spec.md`
- [x] 2.4 将 `jsbridge-protocol/spec.md` 从 change 目录归档到 `openspec/specs/jsbridge-protocol/spec.md`
- [x] 2.5 执行 `openspec list --specs` 确认 4 个新 spec 出现在列表中

## 3. 更新项目默认 Schema（可选）

- [x] 3.1 修改 `openspec/.openspec.yaml` 的 `defaultSchema` 为 `dramaflow`（注：openspec 无项目级 defaultSchema 配置，改为在 CLAUDE.md 中记录新建 change 时使用 `--schema dramaflow`）
- [x] 3.2 验证 `openspec new change test-schema-change` 使用 `dramaflow` schema，确认无误后删除测试 change

## 4. 归档本次变更

- [x] 4.1 执行 `openspec archive add-openspec-schemas` 完成变更归档
