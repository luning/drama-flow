---
id: RULE-BMS
title: BMS 电池管理 + 逆变器控制 — 便携储能系统
status: approved
owner: pm-ecoflow-bms
version: v2.3
updated: 2026-07-01
related:
  - RULE-HOME-ENERGY   # Smart Panel 负载切换联动（business-rules/home-energy/smart-panel.md）
  - RULE-IOT-CLOUD     # 遥测数据上报（business-rules/iot-cloud/device-management.md）
  - SPEC.md#bms-protection
hardware_platform: Delta Pro（3.6kWh / 3.6kW，LFP 16S 串联，标称电压 51.2V）
---

# BMS 电池管理 + 逆变器控制 — 便携储能系统

## 业务概述

本文档是 EcoFlow Delta Pro 级别便携储能产品 BMS（Battery Management System）和逆变器控制的**唯一事实来源（SSoT）**。覆盖从电芯采样、保护动作、SoC 估算、均衡控制到逆变器启停的完整业务规则，以及太阳能输入（MPPT）和 AC 充电策略。

硬件平台参数：

| 参数 | 值 |
|------|-----|
| 电芯化学体系 | 磷酸铁锂（LFP） |
| 串联数 | 16S |
| 单体标称电压 | 3.20 V |
| 系统标称电压 | 51.2 V（= 16 × 3.20 V） |
| 满充电压 | 58.4 V（= 16 × 3.65 V） |
| 截止放电电压 | 44.8 V（= 16 × 2.80 V） |
| 额定容量 | 3.6 kWh（≈ 70 Ah @ 51.2 V） |
| 最大放电功率 | 3600 W（持续）/ 7200 W（5 s 峰值） |
| BMS 主芯片 | TI BQ76952（集成 16 路 AFE + 保护逻辑） |
| MCU | STM32G474（ARM Cortex-M4，170 MHz） |

---

## 业务流程

### RULE-BMS-001：电芯电压 / 温度采样

```
MCU 上电 → I2C 总线初始化（400 kHz Fast Mode [CONSTRAINT:timing]）
  → 配置 BQ76952 AO（Analog Output）多路复用器，通道 0–15 对应 16 路电芯 [详见 §寄存器-REG_VCELL_MUX]
  → 启动周期扫描（100 ms / 次 [CONSTRAINT:timing]）：
      1. 写 MUX_CFG 寄存器切换通道（通道切换后等待 ≥ 8 μs [CONSTRAINT:timing]）
      2. 触发 BQ76952 单次 ADC 转换（转换时间 ≤ 1.1 ms @ 860 SPS）
      3. 读取 VCELL_n 寄存器（16-bit，LSB = 190.73 μV）→ 换算为实际电压 V = raw × 190.73e-6
      4. 对比过充/过放阈值 [详见 §保护阈值-电压]，触发保护或告警
  → NTC 温度采样（通道 16–19，每 500 ms 采样一次 [CONSTRAINT:timing]）：
      通道 16: Pack+ 极柱温度
      通道 17: Pack- 极柱温度
      通道 18: 电池中部 NTC
      通道 19: 环境温度（PCB 板载）
  → 采样结果写入环形缓冲区（深度 16 组，双 buffer，SoC 算法和均衡算法各消费一份）
```

[MUST] 全部 16 路电压和 4 路温度在每个 100 ms 扫描周期内完成更新。  
[MUST NOT] 任意单次 I2C 读写事务持续时间超过 10 ms（超时触发通信故障 FAULT_CODE_I2C_TIMEOUT）。

### RULE-BMS-002：过充 / 过放保护

**过充保护（OVP）触发流程：**

```
电芯电压检测 → 任一 VCELL_n > 3.65 V
  → BQ76952 硬件比较器触发（不依赖 MCU 软件）
  → CHARGE_DSG FET 关断（≤ 50 μs [CONSTRAINT:safety]）[详见 §时序-OVP]
  → 状态寄存器 REG_FAULT_STATUS bit2 置 1 [详见 §寄存器-REG_FAULT_STATUS]
  → MCU 读取故障状态 → 上报故障码 0x02 → 通知 IoT 云端 [详见 RULE-IOT-CLOUD §RULE-IOT-003]
```

**恢复条件：**
- 所有电芯电压 < 3.40 V（回差 250 mV，防止阈值边界振荡）
- 上位机通过 I2C 向 REG_OVP_CLEAR（0x1F）写入 0x02 发送清除命令 [详见 §寄存器-REG_OVP_CLEAR]
- [MUST NOT] 硬件自动恢复，[MUST] 等待软件清除

**过放保护（UVP）触发流程：**

```
任一 VCELL_n < 2.80 V
  → DSG FET 关断（≤ 50 μs [CONSTRAINT:safety]）
  → 状态寄存器 REG_FAULT_STATUS bit3 置 1
  → 休眠计时器启动（1800 s 后进入深度休眠，减少自放电）
```

**恢复条件：**
- 接入 AC 充电器或太阳能 → 检测到充电电压 > 系统电压 + 2 V
- 所有电芯电压 > 3.00 V（UVP 回差 200 mV）
- [SHOULD] 优先提示用户"电量过低，请充电"而非直接关机

### RULE-BMS-003：过温保护（充放电独立阈值）

三级降功率策略：

| 等级 | 充电温度触发 | 放电温度触发 | 动作 |
|------|------------|------------|------|
| 一级降额 | T > 40°C | T > 45°C | 限制至额定功率 70% |
| 二级降额 | T > 45°C | T > 55°C | 限制至额定功率 40% |
| 三级保护 | T > 50°C | T > 60°C | CHG/DSG FET 关断 |
| 低温保护 | T < 0°C（充电）| — | 禁止充电（防止锂析晶）|

[MUST NOT] 电芯温度 < 0°C 时允许任何充电电流（包括太阳能 MPPT）[详见 §保护阈值-温度]。  
[CONSTRAINT:safety] 过温保护触发后 FET 关断时间 ≤ 100 ms。

**温度回差：** 降额解除需温度持续低于触发阈值 5°C 以上，持续时间 ≥ 30 s，防止功率振荡。

### RULE-BMS-004：短路保护（SCD）

```
电流传感器检测 di/dt → 斜率超过 SCD 斜率阈值（默认 ΔI/Δt > 5 A/μs）
  → BQ76952 SCD 引脚硬件锁存（≤ 10 μs [CONSTRAINT:safety]）
  → CHG + DSG FET 同时关断
  → LATCH 位置 1（REG_FAULT_STATUS bit0）[详见 §寄存器-REG_FAULT_STATUS]
  → 产生中断信号通知 MCU（ALERT 引脚下降沿）
```

[MUST NOT] SCD 触发后自动恢复（硬件锁存，防止负载持续损坏）。  
[MUST] 移除故障负载后，上位机发送 SCD_CLEAR 命令（REG_SCD_CLEAR ← 0x01）方可解锁 [详见 §寄存器-REG_SCD_CLEAR]。  
[CONSTRAINT:safety] SCD 响应时间硬件保证 ≤ 10 μs（不可配置，固化在 BQ76952 内部）。

### RULE-BMS-005：被动电芯均衡

```
均衡触发条件（同时满足）：
  1. 电池包处于充电状态（CHARGE FET = ON）
  2. SoC ≥ 80%（进入 CV 阶段前后）
  3. 任意两电芯电压差 ΔV ≥ 20 mV [详见 §寄存器-REG_BAL_CFG]

均衡执行：
  → 识别最高电压电芯组
  → 开启对应均衡 MOSFET（REG_BAL_CTRL）
  → 通过均衡电阻（47 Ω）耗散多余能量（均衡电流 ≈ 70 mA @ 3.3V）
  → 每 10 s 重新评估均衡状态 [CONSTRAINT:timing]
```

[MUST NOT] 均衡同时开启超过 4 路（热管理限制，防止 PCB 温升过高）。  
[SHOULD] 均衡超时保护：单次均衡周期 ≤ 3600 s，超时自动停止并记录告警。

### RULE-BMS-006：SoC 估算（库仑计 + OCV 校正）

```
运行期间：
  库仑计积分 SoC += (I × Δt) / Q_nominal × 100%
  积分周期：Δt = 1 s [CONSTRAINT:timing]
  电流方向：充电为正，放电为负

OCV 静置校正触发条件（满足任一）：
  1. 电流 |I| < 0.5 A 持续 > 600 s
  2. 满充截止（VCELL_max > 3.64 V 且 I < 0.5 A）
  3. MCU 重启（上电后强制 OCV 校正）

OCV 查表：通过 OCV-SoC 对应表（分辨率 5%，共 21 个数据点）线性插值 [详见 §附录-OCV查表]
满充重置：检测到充电截止条件（I < 0.2 A 且 VCELL_max ≥ 3.650 V）→ 强制 SoC = 100%
```

[MUST] SoC 显示精度：云端上报和本地显示均保留整数，内部计算保留小数点后 2 位。  
[MUST NOT] 在电流 |I| > 5 A 时执行 OCV 查表校正（极化电压影响精度）。

### RULE-BMS-007：逆变器启停控制

**启动时序（含预充电路）：**

```
用户触发开机 / IoT 云端指令
  → Step 1: 检查 BMS 状态（无激活故障码，SoC > 3%）
  → Step 2: 闭合预充继电器 K_PRECHARGE（REG_RELAY_CTRL bit0 = 1）
            预充电流通过 100 Ω / 50 W 预充电阻流入逆变器大电容
            等待预充完成：VBUS ≥ 0.9 × VBAT 或超时 3 s [CONSTRAINT:timing]
  → Step 3: 闭合主继电器 K_MAIN（REG_RELAY_CTRL bit1 = 1）
  → Step 4: 延迟 50 ms 后断开预充继电器 K_PRECHARGE（bit0 = 0）[CONSTRAINT:timing]
  → Step 5: 使能逆变器 ENABLE 信号（GPIO 拉高）
  → Step 6: 等待逆变器就绪信号（INVERTER_READY 引脚高电平，超时 2 s 报错）
  → 逆变器输出 AC 120V / 60Hz（北美）或 230V / 50Hz（欧洲）
```

[MUST NOT] 跳过预充步骤直接闭合主继电器（会产生冲击电流损坏大电容 → 寿命衰减）。  
[CONSTRAINT:timing] 主继电器 K_MAIN 触点抖动稳定时间 ≥ 10 ms，需在此后才允许发送 ENABLE 信号。

**关机时序：**

```
关机指令到达
  → 通知负载即将断电（发送广播帧，预留 200 ms 给负载自保存）
  → 禁用逆变器 ENABLE 信号
  → 等待逆变器输出电压 < 5 V（超时 1 s）
  → 断开主继电器 K_MAIN（REG_RELAY_CTRL bit1 = 0）
```

### RULE-BMS-008：MPPT 太阳能输入

```
MPPT 控制器上电 → 检测 PV 输入电压 VPV（范围：11–150 V DC [详见 §保护阈值-太阳能]）
  → 扰动观察法（P&O）MPPT 扫描：
      步长：ΔV = 0.5 V / 次
      扫描周期：每 500 ms 执行一次全局 MPPT 扫描 [CONSTRAINT:timing]
      局部最大值检测：若 P(V+ΔV) < P(V)，则反转方向
  → 最大充电功率限制：
      MPPT 最大输入功率 = min(PV 实际功率, 1600 W)
      当电池温度 > 45°C 时，动态降额至 50%（与 RULE-BMS-003 联动）[详见 §RULE-BMS-003]
  → 低温截止：电芯温度 < 0°C 时 MPPT 输出限制为 0（禁止充电）
```

[MUST] PV 输入电压 > 12 V 且 < 150 V 时方可启动 MPPT（防止欠压和过压损坏）。  
[CONSTRAINT:safety] PV 反极性保护：输入端配置肖特基二极管，无需软件介入。

### RULE-BMS-009：AC 充电策略

充电功率阶梯降额（热管理联动）：

| 条件 | 充电功率 | 触发来源 |
|------|---------|---------|
| 正常充电（T < 35°C，SoC < 80%） | 1800 W（额定） | — |
| SoC ≥ 80%（进入 CV 阶段） | 降额至 900 W | BMS SoC 算法 |
| 电池温度 35–40°C | 降额至 70% = 1260 W | 热管理 RULE-BMS-003 |
| 电池温度 > 45°C | 停止充电 | 热管理 RULE-BMS-003 |
| 电网电压异常（< 100 V 或 > 130 V @北美） | 停止充电，记录事件 | AC 输入监测 |

```
PFC（功率因数校正）控制：
  目标功率因数 > 0.99
  输入电流 THD < 5%
  PFC 控制器：STM32 内建 HRTIM 生成 PWM 信号，频率 65 kHz [CONSTRAINT:timing]
```

[MUST] 充电过程中 LED 状态指示灯按 SoC 分 4 段显示（0–25%/25–50%/50–75%/75–100%）。  
[MUST NOT] 允许 AC 充电和逆变器输出同时以最大功率运行（总功率 > 3600 W 时，优先保障负载）。

### RULE-BMS-010：故障码系统

故障分级与处理：

| 等级 | 定义 | 用户通知方式 | IoT 上报 | 自动恢复 |
|------|------|-----------|---------|---------|
| 0-紧急 | 短路、热失控 | 蜂鸣器 + App 推送 | 立即上报 | 否，[MUST] 人工干预 |
| 1-严重 | OVP/UVP/OTP | App 推送 + LED 闪烁 | 立即上报 | 条件恢复后自动（需软件清除） |
| 2-一般 | 均衡超时、通信异常 | App 通知 | 30 s 内上报 | 自动重试 3 次后告警 |
| 3-信息 | SoC 校正完成、OTA 完成 | App 消息中心 | 批量上报（5 min） | — |

故障码寄存器定义 [详见 §寄存器-REG_FAULT_STATUS 和 REG_FAULT_DETAIL]。

---

## 运行态状态机

```
                    上电 / 复位
                        │
                        ▼
                  ┌──────────┐
              ┌──▶│   INIT   │──────────── 自检失败（通信/硬件故障）──────────┐
              │   └────┬─────┘                                               │
              │        │ 自检通过                                             ▼
              │        ▼                                               ┌──────────┐
              │   ┌──────────┐                                         │  FAULT   │
              │   │  STANDBY │◀─────── 故障清除 / 用户复位 ────────────│          │
              │   └────┬─────┘                                         └──────────┘
              │        │ 开机指令 / 充电接入                                   ▲
              │        ▼                                                       │
              │   ┌──────────┐         ┌──────────┐                           │
              │   │ CHARGING │◀────────│DISCHARGING│                           │
              │   │(AC/MPPT) │         │(逆变输出) │                           │
              │   └────┬─────┘         └────┬──────┘                          │
              │        │ 满充 / 断开充电     │ 放电截止 / 关机                  │
              │        │                    │                                  │
              │        ▼                    ▼                                  │
              │   ┌──────────────────────────┐                                │
              │   │    BALANCED_IDLE         │ ──── 异常保护触发 ─────────────┘
              └───│  (SoC 100%，无负载)      │
                  └──────────────────────────┘
```

状态转换条件详见各 RULE 章节。FAULT 状态进入后 [MUST] 记录时间戳和故障码到 NVRAM（防止掉电丢失）。

---

## 异常处理

| 场景 | 检测方式 | 硬件动作 | 恢复条件 | 告警级别 | 对应 AC |
|------|---------|---------|---------|---------|---------|
| 任一电芯电压 > 3.65 V（OVP） | BQ76952 硬件比较器 | CHARGE_DSG FET 关断（≤ 50 μs）[详见 §时序-OVP] | 所有电芯 < 3.40 V + 软件清除 | 1-严重 | AC-3 |
| 任一电芯电压 < 2.80 V（UVP） | BQ76952 硬件比较器 | DSG FET 关断 + 休眠计时 | 接入充电源 + 所有电芯 > 3.00 V | 1-严重 | AC-4 |
| 短路电流（SCD 触发） | BQ76952 SCD 引脚硬件锁存 | CHG+DSG FET 同时关断（≤ 10 μs）[详见 §时序-SCD] | 移除负载 + 上位机发 SCD_CLEAR | 0-紧急 | AC-7 |
| 电芯温度 > 60°C（OTP-DSG） | NTC 采样（软件） | DSG FET 关断（≤ 100 ms） | 温度 < 55°C 持续 30 s | 1-严重 | AC-5 |
| 电芯温度 > 50°C（OTP-CHG） | NTC 采样（软件） | CHARGE FET 关断 | 温度 < 45°C 持续 30 s | 1-严重 | AC-5 |
| 低温充电（T < 0°C） | NTC 采样（软件） | 禁止 AC 充电和 MPPT | T > 5°C 持续 60 s | 2-一般 | AC-6 |
| I2C 通信超时（> 10 ms） | MCU 超时计数器 | 尝试 I2C 复位（3 次），失败后进入 FAULT | 手动复位 | 1-严重 | AC-8 |
| 预充超时（> 3 s） | MCU 定时器 | 断开预充继电器，禁止开机 | 用户重新触发开机 | 2-一般 | AC-9 |
| 电芯电压差 > 200 mV | 软件比较 | 限制充放电功率至 30%，发出均衡告警 | 电压差 < 50 mV | 2-一般 | AC-10 |

---

## 验收标准

**RULE-BMS-001（采样）：**

AC-1: 全部 16 路电芯电压和 4 路温度在 110 ms 内完成更新（100 ms 扫描周期 + 10 ms 余量）[CONSTRAINT:timing]  
AC-2: I2C 通道切换后 delay ≥ 8 μs，且单路 ADC 转换时间 ≤ 1.1 ms，可由逻辑分析仪验证

**RULE-BMS-002（过充/过放）：**

AC-3: 任一电芯电压 > 3.65 V → MOSFET CHARGE_DSG 在 50 μs 内关断，REG_FAULT_STATUS bit2 = 1  
AC-4: OVP 触发后所有电芯 < 3.40 V 但未收到软件清除命令 → [MUST NOT] 自动导通，状态持续为 FAULT

**RULE-BMS-003（过温）：**

AC-5: 任意 NTC 温度通道 > 60°C → DSG FET 在 100 ms 内关断；温度 < 55°C 持续 30 s 后自动恢复  
AC-6: 任意 NTC 温度通道 < 0°C → AC 充电器和 MPPT 充电均被禁止，仅允许放电

**RULE-BMS-004（短路）：**

AC-7: 短路电流触发 SCD → FET 在 10 μs 内关断，REG_FAULT_STATUS bit0 = 1（硬件锁存），[MUST NOT] 自动恢复  
AC-8: SCD 清除命令（REG_SCD_CLEAR ← 0x01）发送后 FET 恢复导通，LATCH 位清零

**RULE-BMS-005（均衡）：**

AC-9: 均衡触发后同时开启的均衡通道数 ≤ 4 路，每 10 s 重新评估一次均衡状态  
AC-10: 均衡时间超过 3600 s → 自动停止并在 REG_FAULT_DETAIL 记录均衡超时告警

**RULE-BMS-006（SoC）：**

AC-11: 静置 600 s（电流 < 0.5 A）后自动触发 OCV 校正，校正后 SoC 与 OCV 查表偏差 ≤ 3%  
AC-12: 满充截止条件满足 → SoC 强制重置为 100%，云端上报更新

**RULE-BMS-007（逆变器）：**

AC-13: 启动序列中预充继电器 K_PRECHARGE 先于主继电器 K_MAIN 闭合，主继电器闭合后 50 ms 内断开预充  
AC-14: VBUS < 0.9 × VBAT 且超过 3 s → 预充超时，禁止闭合主继电器，记录错误码

**RULE-BMS-008（MPPT）：**

AC-15: PV 输入电压在 11–150 V DC 范围内 MPPT 正常工作；< 11 V 或 > 150 V 时停止输入并发出告警  
AC-16: MPPT 每 500 ms 执行一次扫描，捕获到的最大功率与理论 MPP 偏差 ≤ 5%

**RULE-BMS-009（AC 充电）：**

AC-17: SoC ≥ 80% 后充电功率自动降额至 900 W（从额定 1800 W），过渡时间 ≤ 2 s  
AC-18: 逆变器和 AC 充电同时运行时，总功率超过 3600 W → 充电功率优先降额

**RULE-BMS-010（故障码）：**

AC-19: 所有 0 级和 1 级故障 → 立即上报云端（MQTT QoS 1）且记录到 NVRAM（掉电不丢失）  
AC-20: 故障时间戳以 RTC Unix 时间戳记录（精度 ≤ 1 s），通过 RULE-IOT-CLOUD §RULE-IOT-008 补传

---

## 附录 A：寄存器映射表（BQ76952 I2C，设备地址 0x08）

地址使用 16 进制，LSB 在前（小端）。

| 地址 | 寄存器名 | 位宽 | R/W | 默认值 | 描述 | 关联 AC |
|------|---------|------|-----|--------|------|---------|
| 0x14 | REG_VCELL_1 | 16-bit | R | — | 电芯 1 电压，LSB = 190.73 μV | AC-1 |
| 0x15 | REG_VCELL_2 | 16-bit | R | — | 电芯 2 电压 | AC-1 |
| … | REG_VCELL_3~15 | 16-bit | R | — | 电芯 3–15 电压（地址 0x16–0x22） | AC-1 |
| 0x23 | REG_VCELL_16 | 16-bit | R | — | 电芯 16 电压 | AC-1 |
| 0x28 | REG_VCELL_MUX | 8-bit | R/W | 0x00 | MUX 通道选择（bit[3:0] = 通道号 0–15） | AC-2 |
| 0x2A | REG_TEMP_1 | 16-bit | R | — | NTC 通道 1（Pack+），LSB = 0.1°C，偏移 −40°C | AC-5 |
| 0x2B | REG_TEMP_2 | 16-bit | R | — | NTC 通道 2（Pack−） | AC-5 |
| 0x2C | REG_TEMP_3 | 16-bit | R | — | NTC 通道 3（电池中部） | AC-5 |
| 0x2D | REG_TEMP_4 | 16-bit | R | — | NTC 通道 4（环境） | AC-5 |
| 0x10 | REG_FAULT_STATUS | 16-bit | R | 0x0000 | 故障状态位域（见下方位定义） | AC-3, AC-7 |
| 0x11 | REG_FAULT_DETAIL | 32-bit | R | 0x00000000 | 扩展故障详情（故障码 + 计数） | AC-10, AC-19 |
| 0x1F | REG_OVP_CLEAR | 8-bit | W | — | 写 0x02 清除 OVP 故障（写后自清除） | AC-4 → AC-3 |
| 0x20 | REG_SCD_CLEAR | 8-bit | W | — | 写 0x01 清除 SCD 锁存 | AC-8 → AC-7 |
| 0x30 | REG_BAL_CFG | 16-bit | R/W | 0x0014 | 均衡配置（bit[7:0] = ΔV 阈值，LSB = 1 mV；默认 20 mV） | AC-9 |
| 0x31 | REG_BAL_CTRL | 16-bit | R/W | 0x0000 | 均衡通道控制（bit[n] = 1 开启第 n 路均衡） | AC-9 |
| 0x40 | REG_RELAY_CTRL | 8-bit | R/W | 0x00 | 继电器控制（bit0 = 预充，bit1 = 主继电器） | AC-13 |
| 0x41 | REG_RELAY_STATUS | 8-bit | R | 0x00 | 继电器实际状态反馈（与 REG_RELAY_CTRL 校验） | AC-13 |
| 0x50 | REG_SOC | 16-bit | R | — | SoC，LSB = 0.01%，范围 0–10000（= 0%–100.00%） | AC-11 |
| 0x51 | REG_COULOMB | 32-bit | R/W | — | 库仑计累计值（mAh，有符号整数，充电为正） | AC-11 |
| 0x60 | REG_FW_VER | 16-bit | R | — | BMS 固件版本（high byte = 主版本，low byte = 次版本） | RULE-IOT-006 |

**REG_FAULT_STATUS 位定义（0x10）：**

| Bit | 名称 | 含义 | 清除方式 |
|-----|------|------|---------|
| 0 | SCD_LATCH | 短路保护锁存 | REG_SCD_CLEAR ← 0x01 → AC-8 |
| 1 | OCD | 过流放电 | 故障消除后自动清除 |
| 2 | OVP | 过充保护 | REG_OVP_CLEAR ← 0x02 → AC-4 |
| 3 | UVP | 过放保护 | 接入充电源 + 电压恢复 |
| 4 | OTP_CHG | 充电过温 | 温度恢复后自动清除 |
| 5 | OTP_DSG | 放电过温 | 温度恢复后自动清除 |
| 6 | I2C_TIMEOUT | I2C 通信超时 | MCU 复位 I2C 总线 |
| 7 | BAL_TIMEOUT | 均衡超时 | 均衡停止后自动清除 → AC-10 |
| 8–15 | Reserved | — | — |

---

## 附录 B：保护阈值表

### B.1 电压保护阈值

| 参数 | 阈值 | 回差 | 说明 |
|------|------|------|------|
| 单体过充保护（OVP） | 3.65 V | 250 mV（恢复 < 3.40 V） | LFP 安全上限 → AC-3 |
| 单体过放保护（UVP） | 2.80 V | 200 mV（恢复 > 3.00 V） | LFP 损坏下限 → AC-4 |
| 系统过压（OVP，Pack） | 58.4 V（= 16 × 3.65 V） | — | 对应单体 OVP |
| 系统欠压（UVP，Pack） | 44.8 V（= 16 × 2.80 V） | — | 对应单体 UVP |
| 单体均衡触发 ΔV | ≥ 20 mV | — | 可通过 REG_BAL_CFG 配置 → AC-9 |
| 单体危险电压差 | > 200 mV | — | 触发功率限制 → AC-10 |

### B.2 温度保护阈值

| 参数 | 充电阈值 | 放电阈值 | 回差（恢复条件） |
|------|---------|---------|----------------|
| 一级降额 | T > 40°C | T > 45°C | 降额后 T < 35°C / T < 40°C，持续 30 s |
| 二级降额 | T > 45°C | T > 55°C | 降额后 T < 40°C / T < 50°C，持续 30 s |
| 三级保护（FET 关断） | T > 50°C | T > 60°C | T < 45°C / T < 55°C，持续 30 s → AC-5 |
| 低温充电禁止 | T < 0°C | — | T > 5°C，持续 60 s → AC-6 |

### B.3 电流 / 功率保护阈值

| 参数 | 阈值 | 保护动作 |
|------|------|---------|
| 短路电流斜率（SCD） | ΔI/Δt > 5 A/μs | FET 硬件锁存（≤ 10 μs） → AC-7 |
| 持续过流放电（OCD） | I_DSG > 100 A（= 1.4C） | FET 关断（≤ 50 μs） |
| 瞬时峰值电流（5 s） | I_peak ≤ 200 A | 允许（设计上限） |
| MPPT 最大输入功率 | 1600 W | 软件限制 → AC-15 |
| AC 充电额定功率 | 1800 W | 可降额，最低 0 W → AC-17 |

### B.4 太阳能输入保护阈值

| 参数 | 阈值 | 说明 |
|------|------|------|
| PV 输入电压最小值 | 11 V DC | 低于此值 MPPT 停止 → AC-15 |
| PV 输入电压最大值 | 150 V DC | 超过此值触发 OVP，MPPT 停止 → AC-15 |
| PV 输入电流最大值 | 15 A | 硬件保险丝保护 |
| MPPT 工作温度范围 | −10°C 至 +50°C（环境温度）| 超出范围降额 |

---

## 附录 C：时序约束清单

| 时序 ID | 描述 | 要求 | 测量方式 |
|---------|------|------|---------|
| TIM-001 | I2C 总线速率 | 400 kHz Fast Mode | 逻辑分析仪测量 SCL 频率 |
| TIM-002 | MUX 通道切换稳定时间 | ≥ 8 μs（切换后到触发 ADC）| 示波器测量 MUX_CFG 写入到 ADC 触发间隔 |
| TIM-003 | BQ76952 ADC 转换时间 | ≤ 1.1 ms @ 860 SPS | BQ76952 数据手册 §7.4 |
| TIM-004 | 全电芯扫描周期 | ≤ 100 ms（16 路电压 + 4 路温度）| 固件 systick 计数 |
| TIM-005 | OVP FET 关断时间 | ≤ 50 μs（从阈值超过到 FET 完全关断）| 示波器测量 VCELL → GATE 信号 |
| TIM-006 | SCD FET 关断时间 | ≤ 10 μs（硬件路径，不经过 MCU）| 示波器测量 SCD 引脚 → GATE 信号 |
| TIM-007 | 均衡状态重评估周期 | 10 s | 固件 systick |
| TIM-008 | 预充超时门限 | 3 s（VBUS 未达到 0.9 × VBAT 则放弃）| 固件定时器 |
| TIM-009 | 主继电器触点稳定时间 | ≥ 10 ms（闭合后到允许发 ENABLE）| 继电器数据手册规格 |
| TIM-010 | MPPT 扫描周期 | 500 ms | 固件定时器 |
| TIM-011 | NTC 温度采样周期 | 500 ms（独立于电压扫描）| 固件 systick |
| TIM-012 | OCV 静置校正触发 | 电流 < 0.5 A 持续 600 s | 固件计时 |

---

## 附录 D：通信帧格式

### D.1 I2C 寄存器读写格式（BQ76952）

**写操作（单寄存器）：**

```
START | 设备地址(0x08) W | ACK | 寄存器地址(8-bit) | ACK | 数据字节 | ACK | STOP
```

**读操作（16-bit 寄存器，小端序）：**

```
START | 设备地址(0x08) W | ACK | 寄存器地址(8-bit) | ACK |
Re-START | 设备地址(0x08) R | ACK | 数据低字节 | ACK | 数据高字节 | NACK | STOP
```

**I2C 错误处理：**
- ACK 未收到 → 重试 3 次 → 触发 REG_FAULT_STATUS bit6（I2C_TIMEOUT）
- 总线挂起 → MCU 执行 I2C 总线复位（发送 9 个时钟脉冲清除从机状态）

### D.2 内部 CAN 总线帧格式（BMS → 逆变器控制板）

EcoFlow 内部 CAN 2.0B，29-bit 扩展 ID，波特率 500 kbps。

**BMS 状态帧（ID: 0x18BMS001，周期 100 ms）：**

```
字节  | 7    6    5    4    3    2    1    0
------+----------------------------------
Byte0 | SoC（0–100，单位 1%）
Byte1 | 平均电芯电压高字节（mV，uint16）
Byte2 | 平均电芯电压低字节
Byte3 | 最大电芯电压高字节（mV，uint16）
Byte4 | 最大电芯电压低字节
Byte5 | 最小电芯电压高字节（mV，uint16）
Byte6 | 最小电芯电压低字节
Byte7 | 故障位域（= REG_FAULT_STATUS low byte）
```

**BMS 温度帧（ID: 0x18BMS002，周期 500 ms）：**

```
字节  | 描述
------+---------------------------------
Byte0 | NTC1 温度（°C，偏移 −40，uint8，范围 −40 ~ +215°C）
Byte1 | NTC2 温度
Byte2 | NTC3 温度（电池中部）
Byte3 | NTC4 温度（环境）
Byte4 | 充电状态（0x01=充电中 0x02=放电中 0x00=待机）
Byte5–7 | Reserved（填 0xFF）
```

---

## 附录 E：OCV-SoC 对照表（LFP 16S）

OCV 为静置 600 s 后的开路电压（Pack 总电压），以下为采样点（线性插值）：

| SoC (%) | OCV (V) |
|---------|---------|
| 0 | 44.80 |
| 5 | 50.08 |
| 10 | 51.36 |
| 20 | 52.00 |
| 30 | 52.48 |
| 40 | 52.80 |
| 50 | 53.12 |
| 60 | 53.44 |
| 70 | 53.76 |
| 80 | 54.24 |
| 90 | 55.36 |
| 95 | 56.96 |
| 100 | 58.40 |

[MUST NOT] 在充放电过程中（|I| > 0.5 A）使用 OCV 表进行 SoC 校正（极化电压偏差 > 500 mV）。  
[SHOULD] 出厂前在 25°C 标准温度下对 OCV 表进行校准，温度系数由 NTC4 环境温度补偿。
