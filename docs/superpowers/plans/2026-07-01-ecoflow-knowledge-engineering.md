# EcoFlow 知识工程体系 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `EcoFlow/` 目录下构建 EMS/IoT 知识工程体系，将现有 `business-rules/` 迁为领域知识，并新建结构知识、编码规范、任务经验、Router 各一份典型示范文件。

**Architecture:** `business-rules/` 通过 `git mv` 整体迁入 `EcoFlow/knowledge/domain/`（保留 git 历史）；新建 5 个知识文件 + 2 个 router YAML + 1 个索引文件，均放在 `EcoFlow/` 目录下与 DramaFlow 主项目隔离。

**Tech Stack:** Markdown (GFM)，YAML，无代码生成。

## Global Constraints

- 所有文件放在 `EcoFlow/` 目录下，不修改 DramaFlow 主项目任何文件
- router YAML 的 `load` 路径以 `EcoFlow/` 为根的相对路径
- 内容必须逼真：寄存器地址、函数名、故障码与 `bms-inverter.md` 完全一致
- 不自动 git commit，用户决定提交时机

---

## Task 1: 目录迁移 — business-rules/ → EcoFlow/knowledge/domain/

**Files:**
- Move: `business-rules/` → `EcoFlow/knowledge/domain/`（git mv，保留历史）

- [ ] **Step 1: 创建 EcoFlow/ 顶层目录结构**

```bash
mkdir -p EcoFlow/knowledge/structure \
         EcoFlow/knowledge/coding-standard \
         EcoFlow/knowledge/domain \
         EcoFlow/src/bms \
         EcoFlow/.claude/experience \
         EcoFlow/router
```

- [ ] **Step 2: git mv business-rules/ 到新位置**

```bash
git mv business-rules/portable-power EcoFlow/knowledge/domain/portable-power
git mv business-rules/home-energy    EcoFlow/knowledge/domain/home-energy
git mv business-rules/iot-cloud      EcoFlow/knowledge/domain/iot-cloud
rmdir business-rules
```

- [ ] **Step 3: 验证迁移结果**

```bash
ls EcoFlow/knowledge/domain/
# 期望输出：home-energy  iot-cloud  portable-power

ls EcoFlow/knowledge/domain/portable-power/
# 期望输出：bms-inverter.md

git status --short | grep "knowledge/domain"
# 期望：R  business-rules/... -> EcoFlow/knowledge/domain/...（renamed）
```

---

## Task 2: 结构知识 — EcoFlow/knowledge/structure/ems-system.md

**Files:**
- Create: `EcoFlow/knowledge/structure/ems-system.md`

- [ ] **Step 1: 写入文件**

写入 `EcoFlow/knowledge/structure/ems-system.md`：

```markdown
---
type: structure
scope: system
module: ems
updated: 2026-07-01
---

# EMS 能量管理系统 — 系统架构

## 系统定位

EMS（Energy Management System）是 EcoFlow PowerStation Pro / PowerHub 产品线的能量仲裁核心，运行于 STM32H743 主控 MCU，负责协调六路能量接口的实时功率分配。

## 六路能量接口

```
                                ┌───────────────────────┐
AC-IN (市电/充电桩) ─────────►│                       │──► AC-OUT (逆变器输出, 3600W)
PV1   (光伏1 MPPT)  ─────────►│   EnergyArbiter       │──► DC-OUT (USB-C/DC 负载, 600W)
PV2   (光伏2 MPPT)  ─────────►│   (100ms 调度周期)    │
EXTRA-BAT (扩展电池) ◄────────►│                       │
BAT   (内置电池)    ◄────────►│                       │
                                └───────────────────────┘
```

| 接口 | 方向 | 最大功率 | 说明 |
|------|------|---------|------|
| AC-IN | 输入 | 3000W | 市电 / 充电桩，经 PFC 整流 |
| PV1 | 输入 | 800W | 光伏1，独立 MPPT 跟踪 |
| PV2 | 输入 | 800W | 光伏2，独立 MPPT 跟踪 |
| AC-OUT | 输出 | 3600W | 纯正弦波逆变器输出，50Hz |
| DC-OUT | 输出 | 600W | USB-C 100W + Anderson + 车载 |
| EXTRA-BAT | 双向 | 3000W | 扩展电池（Delta Pro Extra） |

## 核心组件：EnergyArbiter

**文件：** `src/ems/ems_arbiter.c`
**入口：** `ems_core_start()` → 创建 `Task_EMS_Arbiter`（FreeRTOS 优先级 PRIO_CONTROL=3）
**调度周期：** 100ms，由 TIM6 硬件定时器触发

**仲裁输入：**
- `bms_status_t g_bms_status`（共享内存）：SoC、温度、最大可用充放电功率
- `mppt_status_t g_mppt_status`（共享内存）：PV1/PV2 实时输入功率
- `ems_rule_chain_t g_rule_chain`：注册的调度规则链（按优先级排序）

**仲裁输出：**
- `ems_setpoint_t`（通过 `ems_setpoint_queue` 消息队列）：各接口功率目标值（W）
- `ems_telemetry_t`（通过 `iot_telemetry_queue` 消息队列）：遥测数据上报

## 模块边界约束

**EMS 只下发功率目标值（`PowerSetpoint`，单位 W），不直接操控任何外设寄存器。**

| 被控模块 | 文件 | 接收方式 | 自主负责 |
|---------|------|---------|---------|
| BMS | `src/bms/` | 读 `ems_setpoint_queue` | FET 开关、均衡、所有保护逻辑 |
| MPPT | `src/mppt/` | 读 `ems_setpoint_queue` | MPPT 跟踪算法、PV 输入限流 |
| Inverter | `src/inverter/` | 读 `ems_setpoint_queue` | PWM 输出、预充时序、软启动 |

## 四种运行模式

| 模式 | 触发条件 | 功率流向优先级 |
|------|---------|--------------|
| `GRID_TIED` | 市电正常（AC-IN 检测到 50Hz/230V） | PV → 负载 → 充电 → 余电回馈 |
| `OFF_GRID` | 市电断开 | BAT + PV → AC-OUT + DC-OUT |
| `BACKUP` | 市电掉电（< 20ms 切换，不间断） | 同 OFF_GRID，AC-OUT 优先保障 |
| `SELL_BACK` | SoC > 设定阈值 + 市电接入 + 用户授权 | 余电通过并网逆变器上网 |

**模式切换规则：** 必须调用 `ems_mode_switch(target_mode)`，等待 `ems_get_mode_status()` 返回 `MODE_SWITCH_DONE` 后，才可发出继电器操作指令。**禁止直接写继电器 GPIO。**（见 `src/ems/EXPERIENCE.md` 陷阱1）

## 调度规则分层

```
┌─────────────────────────────────────────────────────┐  高优先级
│ 安全层（Safety）：SoC ≤ 15% 强制停放；过温降额/关断  │
│ 不可被任何下层规则覆盖，规则变更需硬件 HIL 测试验证   │
├─────────────────────────────────────────────────────┤
│ 用户策略层（Policy）：TOU 电价分时；备电预留容量；    │
│ 手动优先级设置                                       │
├─────────────────────────────────────────────────────┤
│ 经济优化层（Economy）：光伏自消纳最大化；峰谷差价；   │
│ 余电售出比例                                         │
└─────────────────────────────────────────────────────┘  低优先级
```

新增调度规则实现 `IScheduleRule` 接口，通过 `ems_rule_registry.c` 的 `ems_rule_register()` 注册到规则链。**不修改 `EnergyArbiter` 仲裁器核心逻辑。**

## 数据流全图

```
[传感器层]
  INA228 (电流) ──┐
  NTC (温度)    ──┼──► Task_BMS_VoltageScan (100ms) ──► bms_status_t (共享内存)
  ADS1115 (电压)──┘                                           │
                                                              ▼
[EMS 仲裁]                                          Task_EMS_Arbiter (100ms)
  g_rule_chain ──────────────────────────────────────────────►│
                                                              │ ems_setpoint_t
                                                              ▼
[执行层]                                   ems_setpoint_queue (FreeRTOS Queue)
  BMS Driver   ◄───────────────────────────────────────────────┤
  MPPT Driver  ◄───────────────────────────────────────────────┤
  Inverter Driver ◄────────────────────────────────────────────┘
                                                              │
[IoT 遥测]                                     iot_telemetry_queue
  Task_IoT_Main ◄─────────────────────────────────────────────┘
  (MQTT 上报至 EcoFlow Cloud)
```
```

- [ ] **Step 2: 验证文件内容**

```bash
grep -c "EnergyArbiter\|模块边界\|运行模式\|调度规则" EcoFlow/knowledge/structure/ems-system.md
# 期望输出：4（四个关键章节均存在）
```

---

## Task 3: 编码规范 — EcoFlow/knowledge/coding-standard/firmware.md

**Files:**
- Create: `EcoFlow/knowledge/coding-standard/firmware.md`

- [ ] **Step 1: 写入文件**

写入 `EcoFlow/knowledge/coding-standard/firmware.md`：

```markdown
---
type: coding-standard
scope: firmware
platform: STM32 + FreeRTOS
updated: 2026-07-01
---

# 固件编码规范 — STM32 / FreeRTOS

适用范围：所有运行于 EcoFlow 设备 STM32 系列 MCU 的 FreeRTOS 固件代码（BMS、EMS、MPPT、Inverter、IoT 子模块）。

---

## 任务与调度

### 命名约定

```c
// ✅ 正确：Task_<模块>_<功能>
Task_BMS_VoltageScan
Task_EMS_Arbiter
Task_IoT_Main
Task_BMS_FaultHandler

// ❌ 错误
bmsTask         // 无模块前缀
task1           // 无意义命名
BMSvoltage_task // 格式混乱
```

### 优先级分层（数值越高优先级越高）

```c
#define PRIO_ISR_DEFERRED   5   // 中断延迟处理（保护动作、故障响应）
#define PRIO_PROTECTION     4   // 保护逻辑主循环（OVP/UVP 检查）
#define PRIO_CONTROL        3   // 控制算法（EMS 仲裁、MPPT 跟踪）
#define PRIO_TELEMETRY      2   // 数据上报（IoT 遥测、日志写入）
#define PRIO_IDLE_WORK      1   // 后台任务（均衡检查、OTA 下载）
```

### 栈大小约定

```c
#define STACK_MIN_WORDS     512    // 普通任务下限（2KB）
#define STACK_DEBUG_WORDS   1024   // 含 printf/sprintf 的任务（4KB）
#define STACK_IOT_WORDS     2048   // IoT 任务（含 TLS，8KB）
```

### ISR 约束

ISR 内**禁止**调用任何可能阻塞的 FreeRTOS API。只允许：

```c
// ✅ ISR 内允许
xQueueSendFromISR(queue, &data, &xHigherPriorityTaskWoken);
xSemaphoreGiveFromISR(sem, &xHigherPriorityTaskWoken);
portYIELD_FROM_ISR(xHigherPriorityTaskWoken);

// ❌ ISR 内禁止（会阻塞/崩溃）
xQueueSend(queue, &data, portMAX_DELAY);   // 阻塞版本
vTaskDelay(10);
HAL_Delay(1);
printf("debug");                           // 持有 UART 锁
```

---

## 内存管理

```c
// ✅ 正确：使用项目内存池
uint8_t *buf = mem_pool_alloc(POOL_COMM, 64);
// ... 使用完毕 ...
mem_pool_free(POOL_COMM, buf);

// ❌ 禁止：堆动态分配
uint8_t *buf = malloc(64);   // 禁止
free(buf);                   // 禁止
```

```c
// ❌ 禁止：栈上大数组（超过 256 字节）
void process_data(void) {
    uint8_t tmp[512];   // 禁止，改用 static 或内存池
}

// ✅ 正确：静态缓冲区
static uint8_t s_tmp_buf[512];   // BSS 段，生命周期明确
```

跨任务数据传递用消息队列，**禁止裸指针跨任务传递：**

```c
// ✅ 正确：传递数据副本
bms_voltage_data_t data = {
    .cell_v    = { /* 16 路电压 */ },
    .timestamp = xTaskGetTickCount(),
};
xQueueSend(bms_data_queue, &data, pdMS_TO_TICKS(10));

// ❌ 禁止：传递指针（指向的内存生命周期不可控）
bms_voltage_data_t *ptr = &local_data;
xQueueSend(ptr_queue, &ptr, 0);
```

---

## I2C / SPI 总线访问

```c
// ✅ 正确：持锁访问，限时 5ms 内完成
if (xSemaphoreTake(g_i2c1_mutex, pdMS_TO_TICKS(10)) == pdTRUE) {
    HAL_StatusTypeDef ret = HAL_I2C_Mem_Write(
        &hi2c1, dev_addr, reg, 1, &val, 1, pdMS_TO_TICKS(5));
    xSemaphoreGive(g_i2c1_mutex);
    if (ret != HAL_OK) { fault_handler(FAULT_COMM_ERR); }
}

// ❌ 禁止：无锁访问（多任务竞争）
HAL_I2C_Mem_Write(&hi2c1, dev_addr, reg, 1, &val, 1, 100);

// ❌ 禁止：ISR 内访问 I2C
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    HAL_I2C_Mem_Read(&hi2c1, ...);   // 禁止！改用 xQueueSendFromISR 延迟到任务
}
```

**安全关断路径例外——禁止等待互斥锁，必须 GPIO 直驱：**

```c
// ✅ 安全关断：GPIO 直驱，无锁，微秒级生效
void bms_emergency_shutdown(void) {
    // 第一步：GPIO 直驱立即关断（< 1μs，无任何等待）
    HAL_GPIO_WritePin(GPIOB, CHG_MOS_CTRL_Pin, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, DSG_MOS_CTRL_Pin, GPIO_PIN_RESET);
    // 第二步：异步通知故障处理任务（非阻塞）
    xQueueSendFromISR(bms_fault_queue, &fault_code, NULL);
    // 第三步：BQ76952 寄存器写入由 Task_BMS_FaultHandler 在取锁后执行
}
```

---

## 故障记录

```c
// ✅ 正确：写入 NVRAM 环形日志（含完整上下文）
bms_fault_event_t evt = {
    .timestamp  = rtc_get_unix_ts(),
    .fault_code = FAULT_CHG_OVP,
    .context    = {
        .v_max  = g_bms_status.v_cell_max,
        .i_pack = g_bms_status.i_pack,
        .soc    = g_bms_status.soc,
    },
};
nvram_fault_log_write(&evt);   // 环形覆盖，容量 64 条

// ❌ 禁止：故障路径上使用 HAL_Delay（可能关中断，影响时序）
void handle_ovp_WRONG(void) {
    HAL_Delay(10);             // 禁止！
    nvram_fault_log_write(&evt);
}
```

---

## 代码风格（MISRA-C 2012 必选子集）

**Rule 15.5：函数只有一个 `return`**

```c
// ❌ 错误
int get_value(int x) {
    if (x < 0) { return -1; }
    return x * 2;
}

// ✅ 正确
int get_value(int x) {
    int result = 0;
    if (x < 0) { result = -1; }
    else        { result = x * 2; }
    return result;
}
```

**Rule 17.7：非 `void` 函数返回值必须检查**

```c
// ❌ 错误
HAL_I2C_Mem_Write(&hi2c1, addr, reg, 1, &val, 1, 10);

// ✅ 正确
HAL_StatusTypeDef ret = HAL_I2C_Mem_Write(&hi2c1, addr, reg, 1, &val, 1, 10);
if (ret != HAL_OK) { fault_handler(FAULT_I2C_COMM_ERR); }
```

**Rule 14.4：`if`/`while` 条件必须是布尔类型**

```c
// ❌ 错误
if (ptr)          { ... }
while (connected) { ... }

// ✅ 正确
if (ptr != NULL)        { ... }
while (connected == true) { ... }
```

**所有局部变量声明时必须赋初值：**

```c
// ❌ 错误
int count;
HAL_StatusTypeDef ret;

// ✅ 正确
int count = 0;
HAL_StatusTypeDef ret = HAL_OK;
```
```

- [ ] **Step 2: 验证文件内容**

```bash
grep -c "ISR\|内存管理\|I2C\|故障记录\|MISRA" EcoFlow/knowledge/coding-standard/firmware.md
# 期望输出：5（五个核心章节均存在）
```

---

## Task 4: 任务经验 — EcoFlow/src/bms/EXPERIENCE.md

**Files:**
- Create: `EcoFlow/src/bms/EXPERIENCE.md`

- [ ] **Step 1: 写入文件**

写入 `EcoFlow/src/bms/EXPERIENCE.md`：

```markdown
# BMS 模块 — 任务经验

> 加载时机：开始执行 BMS 相关任务前（保护逻辑、ADC 采样、SoC 估算、均衡）。
> 背景：以下陷阱均在 EcoFlow Delta Pro / PowerStation Pro 实际研发中出现，Agent 多次在同类任务中重复触发。

---

## 新增保护逻辑 — 执行检查清单

每次修改或新增 BMS 保护逻辑（RULE-BMS-002/003/004）时，按顺序执行：

1. BQ76952 寄存器操作 → **确认已正确进入/退出 FINIT 模式**（见陷阱 1）
2. 安全关断路径 → **确认有 GPIO 直驱后备，不依赖互斥锁**（见陷阱 2）
3. 故障码置位后 → **确认调用 `nvram_fault_log_write`，含上下文快照**
4. 锁存故障（CHG_OVP/SCD 等）→ **确认 `[MUST NOT]` 自动恢复**，必须等上位机清除命令

---

## 新增 ADC 采样逻辑 — 执行检查清单

每次修改 RULE-BMS-001（电芯电压/温度采样）相关代码时：

1. MUX 通道切换后 → **必须 `delay_us(10)` 等待建立时间（≥ 8μs）**
2. ADS1115 转换轮询 → **超时上限 1.2ms**，连续 3 次超时触发 `ADC_COMM_ERR`
3. 电压合法性范围 → **2.0V ~ 3.9V，不得改宽**（保护损坏电芯的最后防线）
4. 满充判定后 → **必须调用 `coulomb_counter_reset()`**（见陷阱 3）

---

## 陷阱 1：BQ76952 寄存器写入前必须进入 FINIT 模式

**已触发次数：** 2 次（2024-Q2 均衡功能开发，2025-Q1 保护阈值调整）

**症状：** 写入 `FET_CONTROL`(0x05)、`CBCTRL1_8`(0x06)、`CBCTRL9_16`(0x07) 后回读值不变，程序不报错，但寄存器实际未被修改，导致保护动作或均衡不生效。

**根因：** BQ76952 上述寄存器在非 FINIT 模式下写入被**静默丢弃**，芯片不返回 NACK。

**正确序列：**

```c
// ✅ 正确：先进 FINIT，操作，再退出，写后回读验证
static HAL_StatusTypeDef bq76952_write_protected_reg(uint8_t reg, uint8_t val) {
    HAL_StatusTypeDef ret = HAL_OK;
    uint8_t fmr_val = 0U;

    // Step 1: 进入 FINIT 模式
    ret = bq76952_read_reg(BQ76952_FMR, &fmr_val);
    if (ret != HAL_OK) { return ret; }
    ret = bq76952_write_reg(BQ76952_FMR, fmr_val | BQ76952_FINIT_BIT);
    if (ret != HAL_OK) { return ret; }

    // Step 2: 写目标寄存器
    ret = bq76952_write_reg(reg, val);
    if (ret != HAL_OK) { goto exit_finit; }

    // Step 3: 回读验证（写入静默失败的唯一检测手段）
    uint8_t readback = 0U;
    ret = bq76952_read_reg(reg, &readback);
    if (ret != HAL_OK) { goto exit_finit; }
    if (readback != val) {
        fault_handler(FAULT_COMM_ERR);
        ret = HAL_ERROR;
    }

exit_finit:
    // Step 4: 退出 FINIT 模式（无论是否成功，必须执行）
    (void)bq76952_write_reg(BQ76952_FMR, fmr_val & ~BQ76952_FINIT_BIT);
    return ret;
}
```

**适用寄存器：** 0x05 (FET_CONTROL)、0x06 (CBCTRL1_8)、0x07 (CBCTRL9_16)
**不适用：** 0x10 (FAULT_STATUS，只读)、0x1F (FAULT_CLEAR，无需 FINIT)
**参考规格：** `knowledge/domain/portable-power/bms-inverter.md` §A.1

---

## 陷阱 2：OVP 安全关断路径与 SoC 积分任务争抢 I2C 总线

**已触发版本：** Delta Pro 固件 v1.4.2（2025-Q1 压测，高温高压极限测试）

**症状：** OVP 触发后 CHG MOSFET 关断延迟偶发超 50μs 约束（实测 80-120μs），极限条件下电芯出现轻微过充（< 10mV，已触发二级 OVP2 警戒线）。

**根因：**
- `Task_BMS_SoCIntegration`（PRIO_CONTROL=3）持有 `g_i2c1_mutex` 读 INA228，单次耗时约 40-60μs
- OVP ISR Deferred 任务（PRIO_ISR_DEFERRED=5）通过 I2C 写 BQ76952 关断 MOSFET，需等待互斥锁
- FreeRTOS 优先级抢占在持锁任务间不立即生效，等锁时间不可控

**修复方案：安全关断路径第一动作改为 GPIO 直驱，不等锁**

```c
// ✅ 正确（v1.4.3 修复）
void bms_ovp_emergency_shutdown(void) {
    // 第一步：GPIO 直驱，立即生效（< 1μs，绝对无锁）
    HAL_GPIO_WritePin(GPIOB, CHG_MOS_CTRL_Pin, GPIO_PIN_RESET);  // PB12

    // 第二步：故障事件入队（ISR 安全 API，非阻塞）
    bms_fault_event_t evt = {
        .fault_code = FAULT_CHG_OVP,
        .timestamp  = xTaskGetTickCountFromISR(),
        .context    = {
            .v_max  = g_bms_status.v_cell_max,
            .i_pack = g_bms_status.i_pack,
        },
    };
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xQueueSendFromISR(bms_fault_queue, &evt, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);

    // 第三步：BQ76952 寄存器 0x05 写入由 Task_BMS_FaultHandler 异步执行（非关键路径）
}

// ❌ 错误原实现（v1.4.2）
void bms_ovp_handler_v142_WRONG(void) {
    xSemaphoreTake(g_i2c1_mutex, portMAX_DELAY);   // 可能等待 40-60μs！违反 50μs 约束
    bq76952_write_reg(BQ76952_FET_CONTROL, 0x00);
    xSemaphoreGive(g_i2c1_mutex);
}
```

**规则：** Level 0（紧急）和 Level 1（严重）保护动作**必须**有 GPIO 直驱后备路径作为第一个动作，BQ76952 寄存器写入作为后续异步确认。
**参考规格：** `knowledge/domain/portable-power/bms-inverter.md` §RULE-BMS-002 MOSFET 关断时序

---

## 陷阱 3：满充判定后库仑计未清零导致 SoC 长期偏移

**已触发版本：** Delta Pro 固件 v1.3.0（2024-Q4，用户反馈"电量显示不准"）

**症状：** 满充重启后 SoC 内部计数器偏高约 8-12%，实际电量不足时仍显示较高 SoC。表现：DSG UVP 在 SoC 显示约 12% 时触发（预期应为 5%），用户误认为电池缩水。

**根因：** `bms_soc_set_full()` 只更新显示值，未重置库仑计基准：

```c
// ❌ 问题代码（v1.3.0）
void bms_soc_set_full(void) {
    g_bms_soc.soc_display_pct = 100U;
    // 漏掉：coulomb_counter_reset(NOMINAL_CAPACITY_AH);
    // 库仑计从错误基准继续积分，偏差累积
}
```

**正确实现：**

```c
// ✅ 正确（v1.3.1 修复，已封装为原子操作）
void bms_soc_set_full(void) {
    g_bms_soc.soc_display_pct = 100U;
    // MUST: 满充后必须重置库仑计，以实测满充容量为基准
    coulomb_counter_reset(NOMINAL_CAPACITY_AH);   // 70.0f Ah（Delta Pro 标称）

    // 写 NVRAM 记录满充事件（含满充时实际容量，用于健康度分析）
    bms_fault_event_t evt = {
        .fault_code = EVENT_CHARGE_FULL,
        .timestamp  = rtc_get_unix_ts(),
        .context    = { .soc = 100U, .capacity_ah = (uint16_t)NOMINAL_CAPACITY_AH },
    };
    nvram_fault_log_write(&evt);
}
```

**规则：** `bms_soc_set_full()` 与 `coulomb_counter_reset()` 已在 `bms_soc.c` 中封装为同一函数，**不得**在外部单独调用 `bms_soc_set_full()`，必须调用封装后的 `bms_soc_record_full_charge()`。
**参考规格：** `knowledge/domain/portable-power/bms-inverter.md` §RULE-BMS-006 OCV-SoC 查表

---

## 参考

- 寄存器详细规格：`knowledge/domain/portable-power/bms-inverter.md` §附录A
- 保护阈值总表：`knowledge/domain/portable-power/bms-inverter.md` §附录B
- 时序约束清单：`knowledge/domain/portable-power/bms-inverter.md` §附录C
- 固件编码规范：`knowledge/coding-standard/firmware.md`
```

- [ ] **Step 2: 验证文件内容**

```bash
grep -c "陷阱\|检查清单\|FINIT\|GPIO 直驱\|库仑计" EcoFlow/src/bms/EXPERIENCE.md
# 期望输出：5
```

---

## Task 5: 支撑文件 — INDEX.md + Router YAMLs

**Files:**
- Create: `EcoFlow/.claude/experience/INDEX.md`
- Create: `EcoFlow/router/implement-bms-feature.yaml`
- Create: `EcoFlow/router/debug-firmware-issue.yaml`

- [ ] **Step 1: 写入 .claude/experience/INDEX.md**

写入 `EcoFlow/.claude/experience/INDEX.md`：

```markdown
# EXPERIENCE.md 中央索引

按任务类型加载对应模块的 EXPERIENCE.md。Router 根据 `module` 字段选择。

| 任务类型 | EXPERIENCE.md 路径 | 核心陷阱 |
|---------|-------------------|---------|
| BMS 保护逻辑 / ADC 采样 / SoC 估算 / 均衡 | `EcoFlow/src/bms/EXPERIENCE.md` | FINIT 序列、I2C 竞态、库仑计清零 |
| EMS 调度规则 / 模式切换 / TOU 策略 | `EcoFlow/src/ems/EXPERIENCE.md`（待补充） | 并网切换握手、夏令时 TOU 双执行 |
| IoT MQTT / OTA / Shadow / 遥测 | `EcoFlow/src/iot/EXPERIENCE.md`（待补充） | 上线风暴、OTA 分区兼容、消息幂等 |

## 使用方式

Router 在 `load` 字段按模块引用：

```yaml
load:
  - EcoFlow/src/bms/EXPERIENCE.md   # BMS 相关任务
```

Agent 在任务开始前加载，在任务完成后若发现新陷阱，追加到对应 EXPERIENCE.md 末尾。
```

- [ ] **Step 2: 写入 router/implement-bms-feature.yaml**

写入 `EcoFlow/router/implement-bms-feature.yaml`：

```yaml
# Router: BMS 功能开发
# 适用场景: 新增或修改 BMS 保护逻辑、ADC 采样、SoC 估算、均衡策略

task: implement-change
module: bms

steps:
  - 阅读 EcoFlow/knowledge/structure/ems-system.md §模块边界约束，确认 BMS 只接受
    PowerSetpoint，不受 EMS 直接寄存器操控
  - 阅读 EcoFlow/src/bms/EXPERIENCE.md，重点检查三个检查清单：
    保护逻辑清单（FINIT 序列 / GPIO 后备 / 故障日志 / 锁存不自动恢复）
    ADC 采样清单（MUX 建立时间 / 转换超时 / 合法性范围 / 满充清零）
  - 涉及 BQ76952 寄存器操作（0x05/0x06/0x07）→
    对照 knowledge/domain/portable-power/bms-inverter.md §A.1 寄存器映射
    使用 bq76952_write_protected_reg()，不直接调用 bq76952_write_reg()
  - 涉及保护阈值数值 → 对照 bms-inverter.md §附录B 保护阈值总表，
    不得独自修改阈值（需评审），修改后更新附录B
  - 安全关断路径实现 → GPIO 直驱作为第一动作（见 EXPERIENCE.md 陷阱2），
    通过 xQueueSendFromISR 异步通知故障处理任务
  - 编码风格 → 对照 knowledge/coding-standard/firmware.md：
    任务命名、优先级、ISR 约束、MISRA-C 子集
  - 完成后逐条对照 AC，未覆盖项须列出并确认

load:
  - EcoFlow/knowledge/coding-standard/firmware.md
  - EcoFlow/knowledge/structure/ems-system.md
  - EcoFlow/knowledge/domain/portable-power/bms-inverter.md
  - EcoFlow/src/bms/EXPERIENCE.md
```

- [ ] **Step 3: 写入 router/debug-firmware-issue.yaml**

写入 `EcoFlow/router/debug-firmware-issue.yaml`：

```yaml
# Router: 固件 Bug 调试
# 适用场景: 调查 BMS / EMS 模块运行时异常、保护误触发、数据不准

task: debug-issue
module: bms_or_ems

steps:
  - 先读 EcoFlow/src/bms/EXPERIENCE.md 历史陷阱（BMS 报告）
    或 EcoFlow/src/ems/EXPERIENCE.md（EMS 报告），
    90% 的 Bug 在陷阱列表中已有先例
  - 对照 knowledge/domain/portable-power/bms-inverter.md §RULE-BMS-010
    故障码寄存器（0x10），确认当前 fault_code 的准确含义和锁存状态
  - 检查 NVRAM 事件日志（nvram_fault_log_read()），找到故障前 50ms
    的电流/电压波形（参见 bms-inverter.md §RULE-BMS-004 短路保护的日志格式）
  - 怀疑 I2C 竞态 → 对照 firmware.md §优先级分层，确认两个相关任务的
    PRIO 值；检查安全关断路径是否等待了互斥锁（见 EXPERIENCE.md 陷阱2）
  - 怀疑 BQ76952 写入无效 → 先确认代码是否通过 bq76952_write_protected_reg()
    进行了 FINIT 进退序列（见 EXPERIENCE.md 陷阱1）；对照 §A.1 确认寄存器地址
  - 怀疑 SoC 偏移 → 检查 bms_soc_set_full() 调用后是否紧跟
    coulomb_counter_reset()（见 EXPERIENCE.md 陷阱3）
  - 根因确认后：若与已有陷阱不同，在 EXPERIENCE.md 末尾追加新条目
    （格式参照现有三条陷阱：已触发次数/症状/根因/代码示例/规则）

load:
  - EcoFlow/knowledge/coding-standard/firmware.md
  - EcoFlow/knowledge/domain/portable-power/bms-inverter.md
  - EcoFlow/src/bms/EXPERIENCE.md
```

- [ ] **Step 4: 验证所有文件已创建**

```bash
find EcoFlow/ -type f | sort
# 期望输出（共 10 个文件）：
# EcoFlow/.claude/experience/INDEX.md
# EcoFlow/knowledge/coding-standard/firmware.md
# EcoFlow/knowledge/domain/home-energy/smart-panel.md
# EcoFlow/knowledge/domain/iot-cloud/device-management.md
# EcoFlow/knowledge/domain/portable-power/bms-inverter.md
# EcoFlow/knowledge/structure/ems-system.md
# EcoFlow/router/debug-firmware-issue.yaml
# EcoFlow/router/implement-bms-feature.yaml
# EcoFlow/src/bms/EXPERIENCE.md
```
