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
