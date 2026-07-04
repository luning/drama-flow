# EcoFlow 模块约束

EcoFlow 是 EMS + IoT 固件/云端系统的知识工程示范区，与 DramaFlow 主项目（Android/H5/后端）相互独立，不共享代码，仅共享仓库。

## SDD 最小约束

在为 EcoFlow 任何模块起草设计方案或规划实现步骤前（不论通过 `openspec new change` 还是 `superpowers:brainstorming`/`writing-plans`）：

1. **先查 `EcoFlow/.claude/changes/INDEX.md`**——按模块加载命中的任务经验（EXPERIENCE.md）与设计决策条目。这两类信息从当前代码看不出任何线索，跳过这一步会重复踩已知的坑，或重新推导一遍已被否决的方案。
2. 若任务涉及具体模块的现状（架构、边界、寄存器），按需浏览 `EcoFlow/knowledge/structure/`、`EcoFlow/knowledge/domain/` 下的对应文档——这部分不需要强制加载，跟着任务探索自然会碰到。
3. 完成设计后，若发现新的陷阱或做出了新的架构决策，追加到对应文件末尾，并在 `.claude/changes/INDEX.md` 补充一行索引。

## 目录速查

| 目录 | 内容 | 消费方式 |
|------|------|---------|
| `knowledge/structure/` | 结构知识：系统架构、模块边界 | 按需浏览（现状类） |
| `knowledge/domain/` | 领域知识：业务规则、寄存器手册、AC | 按需浏览（现状类） |
| `knowledge/coding-standard/` | 编码规范 | 每个任务全量加载 |
| `src/*/EXPERIENCE.md` | 任务经验：历史陷阱 | 由 `.claude/changes/INDEX.md` 索引，主动加载（变更类） |
| `.claude/changes/INDEX.md` | 变更类知识统一索引 | 规划变更前必读 |
