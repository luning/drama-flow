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
void bms_soc_record_full_charge(void) {
    g_bms_soc.soc_display_pct = 100U;
    // MUST: 满充后必须重置库仑计，以实测满充容量为基准
    coulomb_counter_reset(NOMINAL_CAPACITY_AH);   // 70.0f Ah（Delta Pro 标称）

    // 写 NVRAM 记录满充事件（含满充时实际容量，用于健康度分析）
    bms_fault_event_t evt = {
        .fault_code    = EVENT_CHARGE_FULL,
        .timestamp     = rtc_get_unix_ts(),
        .context       = { .soc = 100U, .capacity_ah = (uint16_t)NOMINAL_CAPACITY_AH },
    };
    nvram_fault_log_write(&evt);
}
```

**规则：** `bms_soc_set_full()` 与 `coulomb_counter_reset()` 已封装为 `bms_soc_record_full_charge()`，**不得**在外部单独调用 `bms_soc_set_full()`。  
**参考规格：** `knowledge/domain/portable-power/bms-inverter.md` §RULE-BMS-006 OCV-SoC 查表

---

## 参考

- 寄存器详细规格：`knowledge/domain/portable-power/bms-inverter.md` §附录A
- 保护阈值总表：`knowledge/domain/portable-power/bms-inverter.md` §附录B
- 时序约束清单：`knowledge/domain/portable-power/bms-inverter.md` §附录C
- 固件编码规范：`knowledge/coding-standard/firmware.md`
