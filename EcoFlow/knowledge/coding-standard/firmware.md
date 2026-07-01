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
if (ptr)            { ... }
while (connected)   { ... }

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
