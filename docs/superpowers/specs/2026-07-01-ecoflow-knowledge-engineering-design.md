# EcoFlow 知识工程体系 — 设计文档

**日期：** 2026-07-01  
**场景：** EcoFlow（正浩创新）EMS + IoT 系统 Agent 知识工程落地  
**目标：** 构建一套可供 Agent 路由和加载的五类知识体系，与现有 business-rules/ 领域文档集成，放置于 `EcoFlow/` 目录下与 DramaFlow 主项目隔离

---

## 1. 背景与问题

EcoFlow 固件与云端 IoT 团队在引入 Agent 辅助开发后，代码生成质量不稳定：

- BMS 保护逻辑生成时遗漏 FINIT 模式检查，导致寄存器写入无效（已复现 2 次）
- EMS 调度任务生成时不了解并网切换的时序约束，产生倒灌风险
- IoT OTA 功能生成时未考虑 A/B 分区策略，生成了覆盖写逻辑

根因：关键工程知识（芯片时序、历史故障、设计决策）分散在 Confluence、钉钉群记录、老工程师脑海中，Agent 执行时完全看不到。

解法：参照知识工程五类模型，将分散知识系统化组织为 Agent 可路由、可加载的结构，存放于 `EcoFlow/` 目录。本次实施创建**典型示范文件**各一份，展示五类知识中最核心的三类（结构知识、编码规范、任务经验）+ Router。

---

## 2. 整体架构

```
EcoFlow/
├── knowledge/
│   ├── structure/
│   │   └── ems-system.md        # 结构知识（本次新建）
│   ├── coding-standard/
│   │   └── firmware.md          # 编码规范（本次新建）
│   └── domain/                  # 领域知识（business-rules/ git mv 迁入）
│       ├── portable-power/
│       │   └── bms-inverter.md
│       ├── home-energy/
│       │   └── smart-panel.md
│       └── iot-cloud/
│           └── device-management.md
├── src/
│   └── bms/
│       └── EXPERIENCE.md        # 任务经验（本次新建）
├── .claude/
│   └── experience/
│       └── INDEX.md             # EXPERIENCE.md 中央索引（本次新建）
└── router/
    ├── implement-bms-feature.yaml   # BMS 功能开发路由（本次新建）
    └── debug-firmware-issue.yaml    # 固件调试路由（本次新建）
```

**文件操作：**
- `git mv business-rules/ EcoFlow/knowledge/domain/`（保留 git 历史）
- 新建 5 个文件

---

## 3. 各文件内容设计

### 3.1 结构知识：`EcoFlow/knowledge/structure/ems-system.md`

**加载时机：** 分析影响范围或定位具体模块时。

**内容：**

EMS（Energy Management System）是 EcoFlow PowerStation Pro / PowerHub 产品线的能量仲裁核心，描述：

- **六路能量接口**：市电（AC-IN）、光伏1/2（PV1/PV2，双路独立 MPPT）、交流逆变输出（AC-OUT）、直流负载输出（DC-OUT）、扩展电池接口（EXTRA-BAT）
- **核心组件 `EnergyArbiter`**：100ms 调度周期；接收各接口实时功率 + SoC + 电价 TOU 表，输出 `PowerSetpoint`（功率目标值 W）给各执行层
- **模块边界**（关键约束）：EMS **只下发功率目标值**，不直接操控 BMS/MPPT 寄存器；BMS 和 MPPT 各自执行本地闭环控制
- **四种运行模式**：`GRID_TIED`（并网）/ `OFF_GRID`（离网）/ `BACKUP`（备电，市电掉电自动触发）/ `SELL_BACK`（余电上网）
- **数据流**：传感器层（INA228 采样）→ EMS Core 仲裁 → 执行层（BMS/MPPT/Inverter 驱动）→ 状态上报（IoT 遥测队列）
- **调度规则分层优先级**：安全层（SoC 保护/过温）> 用户策略层（TOU/备电）> 经济优化层（光伏自消纳），安全层规则**不可被经济性规则覆盖**

约 60-80 行，含 ASCII 功率流向图。

---

### 3.2 编码规范：`EcoFlow/knowledge/coding-standard/firmware.md`

**加载时机：** 每个任务全量常驻，Router 的 `load` 字段必须始终包含。

**内容（覆盖四个核心约束领域）：**

*任务与调度*
- 命名：`Task_<Module>_<Function>`，如 `Task_BMS_VoltageScan`、`Task_EMS_Arbiter`
- 栈大小下限：512 words（普通），1024 words（含 printf/sprintf 的调试任务）
- 优先级分层：`PRIO_ISR_DEFERRED`(5) > `PRIO_PROTECTION`(4) > `PRIO_CONTROL`(3) > `PRIO_TELEMETRY`(2) > `PRIO_IDLE_WORK`(1)
- ISR 内**禁止**任何可能阻塞的 FreeRTOS API，只允许 `xQueueSendFromISR` / `xSemaphoreGiveFromISR`

*内存管理*
- **禁止** `malloc`/`free`，统一使用 `mem_pool_alloc(pool_id, size)`
- 栈上**禁止**声明大于 256 字节的数组，改用静态缓冲区
- 跨任务数据传递用消息队列，**禁止**裸指针跨任务传递

*I2C / SPI 总线访问*
- 同一总线所有访问必须持有 `g_i2c1_mutex`，持锁时间**不得超过** 5ms
- 中断上下文**禁止**访问 I2C/SPI，通过 `xQueueSendFromISR` 延迟到任务处理

*故障记录*
- 故障事件必须写入 NVRAM 环形日志（`nvram_fault_log_write`），包含：RTC 时间戳、故障码、上下文寄存器快照
- **禁止**在故障处理路径上调用 `HAL_Delay`（可能关中断）

*MISRA-C 2012 必选子集*
- Rule 15.5：函数只有一个 `return`
- Rule 17.7：非 `void` 函数返回值**必须**检查
- Rule 14.4：`if`/`while` 条件必须是布尔类型
- 所有局部变量声明时必须赋初值

约 80-100 行。

---

### 3.3 任务经验：`EcoFlow/src/bms/EXPERIENCE.md`

**加载时机：** 开始执行 BMS 相关任务时（保护逻辑、ADC 采样、SoC 估算）。

**内容：** 三条历史陷阱 + 两个执行检查清单。

**陷阱 1：BQ76952 寄存器写入前必须进入 FINIT 模式**（已触发 2 次）
- 症状：写入 `FET_CONTROL`(0x05) 或 `CBCTRL`(0x06/07) 后回读值不变，不报错
- 根因：BQ76952 过滤/控制类寄存器在非 FINIT 模式下写入被静默丢弃
- 规则：修改这类寄存器**必须先**置 `FMR` 寄存器 `FINIT` 位，操作完成后清除；写后回读验证
- 相关规格：`knowledge/domain/portable-power/bms-inverter.md` §A.1

**陷阱 2：OVP 中断处理与 SoC 积分任务争抢 I2C 总线（竞态）**
- 症状：OVP 触发后 CHG MOSFET 关断延迟偶发超 50μs 约束
- 根因：`Task_BMS_SoCIntegration`（PRIO 3）持有 `g_i2c1_mutex` 读 INA228，OVP ISR Deferred 任务（PRIO 4）等锁
- 修复：OVP 安全关断改为 GPIO 直驱（PB12/PB13），I2C 写 BQ76952 作为后续非关键确认操作
- 规则：**安全关断路径禁止等待互斥锁**，必须有 GPIO 直驱后备

**陷阱 3：满充后库仑计未清零导致 SoC 偏移**
- 症状：满充重启后 SoC 显示偏高，实际电量不足时仍显示较高 SoC（约 8-12% 偏差）
- 根因：`bms_soc_set_full()` 将 `soc_percent` 置 100%，但未调用 `coulomb_counter_reset(70.0f)`
- 规则：调用 `bms_soc_set_full()` 后**必须**紧跟 `coulomb_counter_reset(NOMINAL_CAPACITY_AH)`

**新增保护逻辑检查清单**（每次修改保护相关代码时）
1. BQ76952 寄存器写入 → 确认已进入/退出 FINIT 模式序列
2. 安全关断路径 → 确认有 GPIO 直驱后备，不依赖互斥锁
3. 故障码置位后 → 确认写入 NVRAM 日志（含上下文快照）

**新增 ADC 采样逻辑检查清单**（每次修改 RULE-BMS-001 相关代码时）
1. MUX 通道切换后**必须** `delay_us(10)`（建立时间 ≥ 8μs）
2. ADS1115 转换轮询上限 1.2ms，连续 3 次超时触发 `ADC_COMM_ERR`
3. 电压合法性范围 2.0V ~ 3.9V，**不得**改宽

约 80-100 行。

---

### 3.4 EXPERIENCE.md 中央索引：`EcoFlow/.claude/experience/INDEX.md`

按任务类型索引，供 Router 按任务类型加载：

| 任务类型 | 加载的 EXPERIENCE.md | 说明 |
|---------|-------------------|------|
| BMS 保护逻辑 / ADC 采样 / SoC | `EcoFlow/src/bms/EXPERIENCE.md` | FINIT、竞态、库仑计 |
| EMS 调度规则 / 模式切换 | `EcoFlow/src/ems/EXPERIENCE.md`（待补充） | 并网切换握手、TOU 时区 |
| IoT MQTT / OTA / Shadow | `EcoFlow/src/iot/EXPERIENCE.md`（待补充） | 重连风暴、分区兼容、幂等 |

约 20 行。

---

### 3.5 Router 设计

#### `EcoFlow/router/implement-bms-feature.yaml`

```yaml
task: implement-change
module: bms

steps:
  - 阅读 knowledge/structure/ems-system.md，确认 BMS 与 EMS 的边界（BMS 只接受 PowerSetpoint，不受 EMS 直接寄存器操控）
  - 阅读 src/bms/EXPERIENCE.md，重点检查：FINIT 模式序列、I2C 互斥锁安全关断、满充后库仑计清零
  - 涉及 BQ76952 寄存器操作 → 对照 knowledge/domain/portable-power/bms-inverter.md §附录A 的寄存器映射
  - 涉及保护阈值修改 → 对照 bms-inverter.md §附录B 保护阈值总表，不得独自更改（需评审）
  - 安全关断路径必须实现 GPIO 直驱后备（见 EXPERIENCE.md 陷阱 2）
  - 完成后逐条对照 AC，未覆盖项须列出并确认

load:
  - EcoFlow/knowledge/coding-standard/firmware.md
  - EcoFlow/knowledge/structure/ems-system.md
  - EcoFlow/knowledge/domain/portable-power/bms-inverter.md
  - EcoFlow/src/bms/EXPERIENCE.md
```

#### `EcoFlow/router/debug-firmware-issue.yaml`

```yaml
task: debug-issue
module: bms_or_ems

steps:
  - 先读 src/bms/EXPERIENCE.md（BMS 报告）或 src/ems/EXPERIENCE.md（EMS 报告）中的历史陷阱
  - 对照 knowledge/domain/portable-power/bms-inverter.md 故障码寄存器（0x10）确认当前故障状态
  - 检查 NVRAM 事件日志，找到故障前 50ms 的电流/电压波形数据（见 bms-inverter.md §RULE-BMS-004）
  - 怀疑 I2C 竞态 → 先确认两个任务的优先级（见 firmware.md PRIO 分层），再看持锁时序
  - 怀疑 BQ76952 写入无效 → 先确认 FINIT 模式进退序列（见 bms/EXPERIENCE.md 陷阱 1）
  - 根因确认后，若与已有陷阱不同，在 EXPERIENCE.md 中补充新条目

load:
  - EcoFlow/knowledge/coding-standard/firmware.md
  - EcoFlow/knowledge/domain/portable-power/bms-inverter.md
  - EcoFlow/src/bms/EXPERIENCE.md
```

---

## 4. 文件清单

| 操作 | 路径 | 说明 |
|------|------|------|
| `git mv` | `business-rules/` → `EcoFlow/knowledge/domain/` | 保留 git 历史，3 个子目录含已有文件 |
| 新建 | `EcoFlow/knowledge/structure/ems-system.md` | 结构知识，~70 行 |
| 新建 | `EcoFlow/knowledge/coding-standard/firmware.md` | 编码规范，~100 行 |
| 新建 | `EcoFlow/src/bms/EXPERIENCE.md` | 任务经验，~100 行 |
| 新建 | `EcoFlow/.claude/experience/INDEX.md` | 索引，~20 行 |
| 新建 | `EcoFlow/router/implement-bms-feature.yaml` | Router，~20 行 |
| 新建 | `EcoFlow/router/debug-firmware-issue.yaml` | Router，~20 行 |

**合计：** 1 次 git mv + 6 个新建文件

---

## 5. 知识加载策略

| 类别 | 文件 | 加载时机 | Router 处理 |
|------|------|---------|------------|
| 编码规范 | `coding-standard/firmware.md` | **每个任务** | 所有 router `load` 必含 |
| 结构知识 | `structure/ems-system.md` | 分析影响范围时 | 按 module 按需 |
| 任务经验 | `src/bms/EXPERIENCE.md` | 执行 BMS 任务前 | 按 module 按需 |
| 领域知识 | `domain/portable-power/bms-inverter.md` | 涉及具体寄存器规格时 | EXPERIENCE 中引用，按需 |
