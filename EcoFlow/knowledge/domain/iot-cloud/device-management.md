---
id: RULE-IOT-CLOUD
title: IoT 云端通信 — 设备管理 + OTA + 遥测 + 离线补传
status: approved
owner: pm-ecoflow-iot
version: v1.8
updated: 2026-07-01
related:
  - RULE-BMS             # 设备端 BMS 遥测数据源（business-rules/portable-power/bms-inverter.md）
  - RULE-HOME-ENERGY     # Smart Panel 能源数据上报（business-rules/home-energy/smart-panel.md）
  - SPEC.md#iot-cloud
hardware_platform: 设备端 ESP32-S3（Wi-Fi 2.4/5 GHz + BLE 5.0）+ SIM7600G-H（4G/LTE 备用）+ 云端 AWS IoT Core（MQTT Broker）
---

# IoT 云端通信 — 设备管理 + OTA + 遥测 + 离线补传

## 业务概述

本文档是 EcoFlow 设备 IoT 云端通信的**唯一事实来源（SSoT）**。覆盖设备激活与绑定、MQTT 长连接管理、遥测数据上报、云端指令下发、OTA 固件升级、MCU Flash 分区管理、TLS 证书管理和离线事件补传。

硬件平台参数：

| 参数 | 值 |
|------|-----|
| Wi-Fi 模组 | ESP32-S3（双核 Xtensa LX7，240 MHz）|
| 4G 备用模组 | SIM7600G-H（LTE Cat-4，最大 150 Mbps 下行）|
| 云端 Broker | AWS IoT Core（MQTT 3.1.1 / MQTT 5.0）|
| 设备证书类型 | X.509，由 EcoFlow PKI 签发，有效期 5 年 |
| MCU Flash | 16 MB（ESP32-S3 片外 NOR Flash，W25Q128）|
| RTC | DS3231（精度 ±2 ppm，断电后保持时间）|
| NVRAM | MCU 内部 EFUSE（4 KB，用于设备 UID 和证书指纹）|

---

## 业务流程

### RULE-IOT-001：设备激活与绑定

**首次激活流程（出厂后用户首次开机）：**

```
设备出厂时状态：
  - MCU UID（96-bit 唯一硬件 ID）写入 EFUSE（一次性可编程，不可修改）[详见 §寄存器-EFUSE]
  - 设备证书预置在 Flash Cert 分区 [详见 §Flash分区-CERT]
  - 激活状态：REG_ACTIVATION_STATE = 0x00（未激活）

用户开机 → 设备进入 AP 模式（热点：EcoFlow-XXXX，密码：ecoflow@2026）
  → 用户手机 EcoFlow App 连接设备热点
  → App 通过 BLE 或 HTTP（192.168.4.1）传入 Wi-Fi SSID + 密码
  → 设备连接家庭 Wi-Fi → 建立 TLS 连接到 EcoFlow 激活服务器
  → 设备发送激活请求：
      {
        "uid": "<96-bit UID hex>",
        "model": "DELTA_PRO_ULTRA",
        "fw_ver": "2.3.1",
        "cert_fingerprint": "<SHA256>"
      }
  → 服务器验证证书 + UID 合法性 → 返回激活码 + MQTT 连接参数
  → 设备将激活状态写入 REG_ACTIVATION_STATE = 0x01（已激活）[详见 §寄存器-REG_ACTIVATION_STATE]
  → 设备发布上线消息到 MQTT Topic：ecoflow/device/<uid>/status
  → 用户在 App 扫描设备 UID 二维码完成账号绑定
```

[MUST] 设备 UID 在 EFUSE 中写入后不可更改，替换主板视为新设备，需重新激活。  
[MUST NOT] 设备证书私钥离开设备（证书私钥在出厂时写入 Flash，不可读出，仅用于 TLS 握手）。  
[CONSTRAINT:timing] 激活请求服务器响应超时：30 s。超时后重试 3 次，间隔 10 s，仍失败则保持 AP 模式等待。

### RULE-IOT-002：MQTT 长连接管理

**连接参数：**

| 参数 | 值 |
|------|-----|
| Broker 地址 | `iot.ecoflow.com`（AWS IoT Core 自定义域名）|
| 端口 | 8883（MQTT over TLS 1.3）|
| KeepAlive | 60 s（心跳间隔）|
| CleanSession | false（订阅持久化，断线重连后恢复订阅）|
| 遗嘱消息 Topic | `ecoflow/device/<uid>/lwt` |
| 遗嘱消息 Payload | `{"status": "offline", "ts": <unix_ts>}` |
| 遗嘱消息 QoS | 1（至少送达一次）|
| 遗嘱消息 Retain | true（Broker 保留，新订阅者可见）|

**断线重连策略（指数退避）：**

```
连接断开检测：KeepAlive 超时（60 s 内未收到 PINGRESP）或 TCP 断开
  → 第 1 次重试：立即（0 s 后）
  → 第 2 次重试：5 s 后
  → 第 3 次重试：20 s 后
  → 第 4 次及以后：60 s 后（最大间隔，持续重试）
  → 每次重试使用 TLS Full Handshake（session ticket 失效时）
```

**Wi-Fi 不可用时切换 4G：**

```
Wi-Fi 连续 3 次重连失败（间隔 60 s）
  → 启动 SIM7600G-H 4G 模组（启动时间 ≤ 15 s [CONSTRAINT:timing]）
  → 尝试 4G MQTT 连接（参数相同）
  → 4G 连接成功：更新 REG_NETWORK_MODE = 0x02（4G 模式）
  → Wi-Fi 信号恢复后（每 5 min 探测一次）：切回 Wi-Fi，关闭 4G 模组（省电）
```

[MUST] Wi-Fi 和 4G 不同时发布遥测数据（防止重复上报，由 SEQ_NUM 去重 [详见 §RULE-IOT-003]）。  
[CONSTRAINT:timing] 切换至 4G 并建立 MQTT 连接的总时间 ≤ 30 s。

### RULE-IOT-003：遥测数据上报

**数据点定义（每条遥测消息包含以下字段）：**

| 数据点 | 类型 | 单位 | 来源 | 更新频率 |
|--------|------|------|------|---------|
| soc | uint8 | % | BMS REG_SOC [详见 RULE-BMS §寄存器-REG_SOC] | 10 s |
| vcell_avg | uint16 | mV | BMS REG_VCELL_1~16 平均值 | 10 s |
| vcell_min | uint16 | mV | BMS 扫描最低值 | 10 s |
| vcell_max | uint16 | mV | BMS 扫描最高值 | 10 s |
| temp_max | int8 | °C | BMS NTC 最大值 | 30 s |
| power_in | int32 | W | Smart Panel CT 汇总输入功率（正=充电）| 10 s |
| power_out | int32 | W | 逆变器输出功率 | 10 s |
| power_solar | uint32 | W | MPPT 采集功率 | 10 s |
| fault_status | uint16 | — | BMS REG_FAULT_STATUS [详见 RULE-BMS §寄存器] | 事件触发（立即）|
| energy_day | uint32 | Wh | 当日累计充放电能量 | 每 5 min |

**上报周期策略：**

```
正常状态：每 10 s 上报一次（常规遥测）
  → MQTT Topic: ecoflow/device/<uid>/telemetry
  → QoS: 0（允许丢失，减少网络开销）

故障状态（fault_status ≠ 0）：立即上报 + 每 1 s 连续上报直到故障清除
  → QoS: 1（确保送达）

离线缓存：网络断开时，遥测数据缓存至 NVRAM 事件队列 [详见 §RULE-IOT-008]
```

**遥测消息格式（JSON，UTF-8）：**

```json
{
  "uid": "EF-A1B2C3D4E5F6",
  "ts": 1751385600,
  "seq": 12345,
  "data": {
    "soc": 78,
    "vcell_avg": 3312,
    "vcell_min": 3305,
    "vcell_max": 3318,
    "temp_max": 32,
    "power_in": 1200,
    "power_out": 850,
    "power_solar": 2050,
    "fault_status": 0
  }
}
```

[MUST] `seq` 字段单调递增（uint32，溢出后从 0 重新计数），云端用于检测丢包和去重。  
[MUST NOT] 在 QoS 0 消息中携带 fault_status ≠ 0 的告警数据（告警必须用 QoS 1 确保送达）。

### RULE-IOT-004：云端指令下发

**指令 Topic：** `ecoflow/device/<uid>/cmd`（设备订阅，QoS 1）

**指令格式：**

```json
{
  "cmd_id": "CMD-20260701-001",
  "ts": 1751385600,
  "type": "set_mode",
  "params": {
    "mode": "backup_priority"
  }
}
```

**设备处理流程：**

```
收到指令 → 校验 cmd_id 格式（前缀 CMD- + 日期 + 序号）
  → 查重：若 cmd_id 已在 REG_CMD_LOG 中存在 → 返回 ACK（幂等处理，不重复执行）
  → 校验 params 参数合法性（越界值返回 NACK）
  → 执行指令 → 发布执行结果到 ecoflow/device/<uid>/cmd/ack
  → 写入 REG_CMD_LOG（最近 32 条指令记录，环形缓冲）[详见 §寄存器-CMD_LOG]
```

**ACK 消息格式：**

```json
{
  "cmd_id": "CMD-20260701-001",
  "ts": 1751385612,
  "result": "ok",
  "error": null
}
```

[MUST] 指令执行超时（> 30 s 无法完成）→ 返回 `{"result": "timeout"}`，不静默失败。  
[MUST NOT] 同一 cmd_id 的指令执行超过一次（幂等保证）[详见 §寄存器-CMD_LOG]。  
[CONSTRAINT:timing] 设备收到指令后 ACK 响应时间 ≤ 2 s（执行可异步，但接收确认需立即）。

### RULE-IOT-005：OTA 固件升级

**触发方式：** 云端下发 OTA 指令（type: "ota_upgrade"）或设备主动轮询（每 24 h 一次 [CONSTRAINT:timing]）。

**升级流程：**

```
云端下发 OTA 指令，携带：
  {
    "fw_url": "https://ota.ecoflow.com/delta_pro_ultra/v2.4.0/full.bin",
    "fw_version": "2.4.0",
    "fw_size": 2097152,       // 2 MB
    "fw_md5": "a1b2c3d4...",
    "patch_from": "2.3.x"    // 差分升级基础版本（null=全量升级）
  }

Step 1: 预检查
  → 当前 SoC ≥ 20%（[MUST NOT] 低电量时升级，防止升级中断）[详见 RULE-BMS §RULE-BMS-006]
  → OTA 分区剩余空间 ≥ fw_size [详见 §Flash分区-OTA]
  → 不在充放电保护状态（BMS fault_status = 0）

Step 2: 分片下载
  → HTTPS 下载，分片大小 64 KB（每片 = 1 个 Flash 扇区）
  → 每片下载后立即写入 OTA 分区并校验 CRC32 [详见 §Flash分区-OTA]
  → REG_OTA_PROGRESS 更新进度（0–100%）[详见 §寄存器-REG_OTA_PROGRESS]
  → 下载中断可从最后成功分片恢复（断点续传，偏移量保存在 REG_OTA_RESUME_OFFSET）

Step 3: 校验
  → 下载完成 → 计算整个固件 MD5 → 与 fw_md5 比对
  → MD5 不匹配 → 清除 OTA 分区，上报失败，不进入下一步

Step 4: 切换 + 回滚保护
  → 更新 OTA 状态寄存器 REG_OTA_STATE = READY [详见 §寄存器-REG_OTA_STATE]
  → 重启设备（写 REG_SYS_CTRL ← 0xAA 触发软重启）
  → Bootloader 检测 REG_OTA_STATE = READY → 从 OTA 分区启动
  → 新固件启动后 60 s 内自检通过：写 REG_OTA_STATE = CONFIRMED → 正式切换
  → 60 s 内自检失败：Bootloader 回滚到 App 分区原固件 [详见 §Flash分区-APP]
```

[MUST] OTA 过程中保持 MQTT 连接（可降低遥测频率至 60 s/次，节省带宽）。  
[MUST NOT] 在升级过程中关闭电源或拔除 USB 连接（App 需在 OTA 期间显示"正在升级，请勿断电"）。  
[CONSTRAINT:safety] 回滚机制必须在 Bootloader 实现（不依赖新固件自身），确保固件损坏时仍可恢复。

### RULE-IOT-006：MCU Flash 分区管理

Flash 总大小：16 MB（W25Q128，SPI NOR Flash，擦除单位 4 KB 扇区，写入单位 256 B 页）

[详见 §附录-Flash分区表]

**分区访问规则：**

```
Bootloader 分区：[MUST NOT] 应用固件直接写入（由 Bootloader 自身维护）
App 分区：      应用固件运行时只读；OTA 完成后由 Bootloader 切换
OTA 分区：      仅在 OTA 下载期间由应用写入，写入完成后由 Bootloader 接管
Cert 分区：     [MUST NOT] 任何途径可读出私钥（只读出证书公钥）
NVS 分区：      应用读写（Wi-Fi 配置、用户设置、命令日志等）
Event 分区：    应用追加写（环形，离线事件缓存）
```

**版本号寄存器（内存映射，启动后从 Flash 加载）：**

| 寄存器 | 地址（SRAM 映射）| 说明 |
|--------|----------------|------|
| REG_FW_VER_MAIN | 0x20001000 | 主固件版本（uint32，格式 0xAABBCCDD = A.B.C.D）|
| REG_BL_VER | 0x20001004 | Bootloader 版本（只读，出厂固化）|
| REG_HW_VER | 0x20001008 | 硬件版本（从 EFUSE 加载，只读）|
| REG_OTA_STATE | 0x20001010 | OTA 状态（0=无 1=READY 2=CONFIRMED 3=ROLLBACK）→ AC-11 |
| REG_OTA_PROGRESS | 0x20001014 | OTA 下载进度（0–100，uint8）→ AC-10 |
| REG_OTA_RESUME_OFFSET | 0x20001018 | 断点续传偏移（uint32，已下载字节数）|

### RULE-IOT-007：TLS 证书管理

**设备证书体系：**

```
EcoFlow Root CA（自签，离线保存，不联网）
  └── EcoFlow Intermediate CA（在线，每年轮换）
        └── 设备证书（每台设备唯一，有效期 5 年）
              ├── 证书公钥（存储在 Flash Cert 分区，可读）
              └── 证书私钥（存储在 Flash Cert 分区，[MUST NOT] 可读出）
```

**证书轮换流程（到期前 30 天触发）：**

```
设备检测证书到期时间（从证书 notAfter 字段解析）
  → 到期前 30 天：发起证书轮换请求（MQTT Topic: ecoflow/device/<uid>/cert/renew）
  → 服务器生成新证书 → 通过当前 TLS 连接安全传输新证书（DER 格式，AES-256 加密）
  → 设备校验新证书由 EcoFlow Intermediate CA 签发 → 写入 Flash Cert 分区备份位置
  → 重启后 Bootloader 检测到备份证书有效期更长 → 切换为主证书
  → 旧证书保留 7 天（用于应急回滚）后自动清除
```

[MUST] TLS 版本 ≥ 1.3（禁止 TLS 1.0/1.1/1.2，防止 BEAST/POODLE 攻击）。  
[MUST NOT] 设备证书私钥通过任何接口（UART/JTAG/OTA/MQTT）暴露到设备外部。  
[CONSTRAINT:timing] 证书轮换请求服务器响应超时：60 s，超时后重试间隔 24 h。

### RULE-IOT-008：离线事件补传

**离线缓存机制：**

```
设备检测到网络断开（MQTT 连接丢失 > 5 s）：
  → 切换到离线模式（REG_NETWORK_MODE = 0x00）
  → 所有遥测数据改为写入 Event 分区环形缓冲（[详见 §Flash分区-EVENT]）
  → 写入格式：[4字节RTC时间戳][2字节事件类型][N字节数据][2字节CRC16]
  → 缓冲区满（255 条）时，丢弃最旧数据（LRU 策略），记录丢弃计数
```

**网络恢复后补传：**

```
网络恢复 → MQTT 重连成功
  → 读取 Event 分区中所有待补传事件
  → 按时间戳升序排列
  → 批量发布到 MQTT Topic: ecoflow/device/<uid>/events/offline
      每批最多 50 条，每批间隔 1 s（防止 Broker 过载）
  → 每批发布后等待 PUBACK（QoS 1）确认，超时 10 s 则重发
  → 全部补传完成后清除 Event 分区已传事件（保留未传事件）
```

**RTC 时间戳校准：**

```
设备上电 → 发送 NTP 查询（SNTP，UDP 123 端口，服务器：pool.ntp.org）
  → NTP 响应 → 与 DS3231 RTC 时间比对
  → 偏差 > 1 s：更新 DS3231 RTC 时间（写 REG_RTC_EPOCH [详见 §寄存器-RTC]）
  → 偏差 ≤ 1 s：不更新（防止频繁写 RTC 寄存器）
  → NTP 同步间隔：正常情况每 24 h 一次 [CONSTRAINT:timing]
  → 网络不可用时：使用 DS3231 RTC 时间（精度 ±2 ppm ≈ ±5 s/月）
```

[MUST] 离线事件时间戳来源于 DS3231 RTC（非系统 uptime），确保断电重启后时间戳连续。  
[MUST NOT] 丢弃 0 级（紧急）和 1 级（严重）故障事件（即使缓冲区满，优先保留高优先级事件）。  
[CONSTRAINT:timing] 网络恢复后 30 s 内开始补传，补传完成后才恢复实时遥测。

---

## 运行态状态机

```
                       设备上电
                           │
                           ▼
                     ┌──────────┐
                     │  BOOT    │──── Flash 校验失败 ──────────────────┐
                     └────┬─────┘                                       ▼
                          │ 固件自检通过                          ┌──────────┐
                          ▼                                       │ RECOVERY │
                    ┌──────────┐                                  │(回滚模式) │
                    │  INIT    │─── 激活状态检查 ──────┐           └──────────┘
                    └────┬─────┘                      │
                         │ 已激活                      ▼
                         │                     ┌──────────────┐
                         │                     │ PROVISIONING │
                         ▼                     │（首次配网激活）│
                   ┌──────────┐                └──────────────┘
                   │ OFFLINE  │◀─── 网络断开 ──────────────────────────┐
                   │（离线缓存）│                                         │
                   └────┬─────┘                                         │
                        │ 网络恢复                                       │
                        ▼                                               │
                  ┌──────────┐          ┌──────────┐                   │
                  │  ONLINE  │──────────▶│ OTA_MODE │─── OTA 完成 ─────┘
                  │（正常运行）│          │（升级中）  │
                  └──────────┘          └──────────┘
                        │                    │
                        │                    │ 升级失败 → ROLLBACK → ONLINE
                        │ 云端指令
                        ▼
                  ┌──────────┐
                  │ CMD_EXEC │
                  │（执行指令）│
                  └──────────┘
```

---

## 异常处理

| 场景 | 检测方式 | 动作 | 恢复条件 | 告警级别 | 对应 AC |
|------|---------|------|---------|---------|---------|
| MQTT 连接断开（KeepAlive 超时）| PINGRESP 超时 | 指数退避重连；失败 3 次后切 4G | MQTT 重连成功 | 2-一般 | AC-3 |
| OTA 下载中断 | HTTP 响应超时（30 s）| 保存断点偏移，从断点恢复 | 网络恢复后自动续传 | 2-一般 | AC-10 |
| OTA MD5 校验失败 | MD5 对比 | 清除 OTA 分区，上报失败，保留原固件 | 用户手动重新触发 OTA | 1-严重 | AC-11 |
| 新固件 60 s 自检失败 | Bootloader 计时 | 回滚至原 App 分区固件，上报 ROLLBACK | 云端下发修复版固件 | 1-严重 | AC-12 |
| OTA 升级时 SoC < 20% | BMS REG_SOC 检查 | 拒绝升级，返回 NACK + 原因码 | SoC ≥ 20% 后可重新触发 | 2-一般 | AC-9 |
| 证书到期（< 30 天）| 证书 notAfter 解析 | 发起轮换请求，期间维持 TLS 连接 | 新证书写入并生效 | 2-一般 | AC-13 |
| 离线事件缓冲区满（255 条）| Event 分区写指针检查 | 丢弃最旧的 3 级（信息）事件 | 网络恢复后补传 | 2-一般 | AC-15 |
| NTP 同步失败 | SNTP 请求超时（5 s）| 使用 RTC 本地时间，记录 NTP_FAIL | NTP 同步成功后更新 RTC | 3-信息 | AC-16 |
| 重复指令（cmd_id 已执行）| REG_CMD_LOG 查重 | 返回 ACK（成功），不重复执行 | — | — | AC-7 |
| 4G 模组启动超时（> 15 s）| SIM7600G-H AT 命令响应 | 上报 4G_TIMEOUT，继续重试 Wi-Fi | 4G 模组恢复 | 2-一般 | AC-4 |

---

## 验收标准

**RULE-IOT-001（设备激活）：**

AC-1: 设备 UID 写入 EFUSE 后无法通过任何方式修改，Flash 擦除不影响 EFUSE  
AC-2: 激活请求发出后服务器 30 s 内未响应 → 重试 3 次，3 次后维持 AP 模式，不自动关机

**RULE-IOT-002（MQTT 连接）：**

AC-3: MQTT 连接断开后重试间隔符合指数退避：0 s → 5 s → 20 s → 60 s（稳定）  
AC-4: Wi-Fi 连续失败 3 次（180 s）后启动 4G，4G + MQTT 连接在 30 s 内建立

**RULE-IOT-003（遥测上报）：**

AC-5: 故障状态（fault_status ≠ 0）时遥测消息使用 QoS 1，正常状态时使用 QoS 0  
AC-6: 遥测消息 seq 字段单调递增，云端收到乱序消息时以 seq 排序（不丢弃，但标记乱序）

**RULE-IOT-004（指令下发）：**

AC-7: 相同 cmd_id 的指令发送两次 → 第二次收到 ACK 且指令只执行一次（幂等验证）  
AC-8: 指令执行时间 > 30 s → 返回 `{"result": "timeout"}`，不静默失败；2 s 内发送接收 ACK

**RULE-IOT-005（OTA 升级）：**

AC-9: SoC < 20% 时发起 OTA → 设备返回 NACK，reason = "soc_too_low"，不开始下载  
AC-10: 下载中断后网络恢复 → 从 REG_OTA_RESUME_OFFSET 断点续传，已下载分片不重复下载  
AC-11: MD5 校验失败 → OTA 分区清除，原固件继续运行，不重启，上报 OTA_VERIFY_FAIL  
AC-12: 新固件 60 s 自检失败 → Bootloader 回滚至原固件，上报 OTA_ROLLBACK（不循环升级）

**RULE-IOT-007（证书管理）：**

AC-13: 证书到期前 30 天发起轮换请求，轮换完成后 TLS 连接不中断（使用旧证书维持连接直到重启）  
AC-14: 设备证书私钥 [MUST NOT] 出现在 MQTT 消息、UART 日志或任何可读接口中

**RULE-IOT-008（离线补传）：**

AC-15: 离线期间 0 级和 1 级故障事件 [MUST NOT] 被丢弃（即使缓冲区满也保留，丢弃 3 级事件）  
AC-16: 网络恢复后 30 s 内开始补传，补传按时间戳升序，每批 50 条，QoS 1 确认

---

## 附录 A：MCU Flash 分区表（W25Q128，16 MB）

| 分区名 | 起始地址 | 大小 | 类型 | 访问权限 | 说明 |
|--------|---------|------|------|---------|------|
| Bootloader | 0x000000 | 64 KB | 代码 | 只读（应用不可写）| 引导程序 + 分区切换逻辑 + 回滚保护 [→ AC-12] |
| NVS（用户配置）| 0x010000 | 256 KB | 数据 | 读写 | Wi-Fi 配置、用户偏好、峰谷电价时间表 |
| Cert（证书）| 0x050000 | 128 KB | 数据 | 证书公钥可读，私钥不可读 | 设备 X.509 证书（主 + 备份）[→ AC-14] |
| App（当前固件）| 0x070000 | 6 MB | 代码 | 运行时只读 | 当前运行固件分区 |
| OTA（升级固件）| 0x670000 | 6 MB | 代码 | OTA 下载时可写 | 待升级固件分区 [→ AC-10, AC-11] |
| Event（事件日志）| 0xC70000 | 1 MB | 数据 | 追加写 | 离线事件环形缓冲（≤ 255 条）[→ AC-15] |
| Reserved | 0xD70000 | ~2.6 MB | — | — | 预留（未来扩展）|

---

## 附录 B：关键寄存器映射（SRAM 内存映射 + Flash 持久化寄存器）

### B.1 网络与状态寄存器（SRAM 内存映射，重启后从 NVS 加载）

| 地址 | 寄存器名 | R/W | 默认值 | 说明 |
|------|---------|-----|--------|------|
| 0x20002000 | REG_NETWORK_MODE | R/W | 0x00 | 网络模式（0=离线 1=Wi-Fi 2=4G）|
| 0x20002004 | REG_MQTT_STATE | R | 0x00 | MQTT 状态（0=断开 1=连接中 2=已连接）|
| 0x20002008 | REG_ACTIVATION_STATE | R/W | 0x00 | 激活状态（0=未激活 1=已激活）[→ AC-1] |
| 0x2000200C | REG_NETWORK_RETRY_CNT | R/W | 0x00 | 当前网络重试次数（超过 3 次切换 4G）[→ AC-4] |

### B.2 OTA 寄存器（NVS 持久化，重启保留）

| 寄存器名 | NVS Key | 类型 | 说明 |
|---------|---------|------|------|
| REG_OTA_STATE | `ota_state` | uint8 | 0=无 1=READY 2=CONFIRMED 3=ROLLBACK [→ AC-11, AC-12] |
| REG_OTA_PROGRESS | `ota_progress` | uint8 | 0–100，百分比 [→ AC-10] |
| REG_OTA_RESUME_OFFSET | `ota_offset` | uint32 | 断点续传偏移（字节）[→ AC-10] |
| REG_OTA_FW_MD5 | `ota_md5` | char[33] | 目标固件 MD5（下载开始时写入）[→ AC-11] |

### B.3 指令日志（NVS 持久化，最近 32 条）

| NVS Key | 类型 | 说明 |
|---------|------|------|
| `cmd_log_ptr` | uint8 | 写指针（0–31，环形）|
| `cmd_log_0` ~ `cmd_log_31` | char[64] | 指令 ID（字符串，最长 63 字节）[→ AC-7] |

### B.4 RTC 寄存器（DS3231 I2C，设备地址 0x68）

| 地址 | 寄存器名 | 位宽 | R/W | 说明 |
|------|---------|------|-----|------|
| 0x00 | REG_RTC_SEC | 8-bit | R/W | 秒（BCD 码，0–59）|
| 0x01 | REG_RTC_MIN | 8-bit | R/W | 分钟（BCD 码，0–59）|
| 0x02 | REG_RTC_HOUR | 8-bit | R/W | 小时（BCD 码，0–23，24h 模式）|
| 0x04 | REG_RTC_DAY | 8-bit | R/W | 日（BCD 码，1–31）|
| 0x05 | REG_RTC_MON | 8-bit | R/W | 月（BCD 码，1–12）|
| 0x06 | REG_RTC_YEAR | 8-bit | R/W | 年（BCD 码，0–99，加 2000 为实际年份）|
| 0x0E | REG_RTC_CTRL | 8-bit | R/W | 控制寄存器（bit2=INTCN 1=SQW 方波输出）|
| 0x11 | REG_RTC_TEMP_H | 8-bit | R | 温度高字节（有符号整数，°C）|
| 0x12 | REG_RTC_TEMP_L | 8-bit | R | 温度低字节（bit[7:6] = 0.25°C 分辨率）|

[CONSTRAINT:timing] DS3231 I2C 通信速率 100 kHz（Standard Mode），RTC 读取时间 ≤ 1 ms。  
[MUST] NTP 同步后的时间写入 DS3231 前必须进行格式转换（Unix 时间戳 → BCD 格式）[→ AC-16]。

### B.5 EFUSE 布局（ESP32-S3 片内 EFUSE，一次性可编程）

| EFUSE Block | 字节范围 | 内容 | 编程时间 |
|-------------|---------|------|---------|
| BLOCK0 | 0–3 | 系统配置位（保留给 Espressif）| 出厂 |
| BLOCK1 | 0–31 | EcoFlow 设备 UID（96-bit）+ 硬件版本（4-bit）| 出厂 [→ AC-1] |
| BLOCK2 | 0–31 | 证书指纹（SHA256，256-bit）| 出厂 |
| BLOCK3 | 0–7 | 安全启动 key（256-bit）| 出厂 |

[MUST NOT] 在量产固件中开放 EFUSE 写接口（仅出厂刷机工具可写）[→ AC-1]。

---

## 附录 C：MQTT Topic 命名规范

所有 Topic 使用 UTF-8 编码，`<uid>` 为设备唯一 ID（格式：`EF-` + 12 位大写十六进制）。

| Topic | 方向 | QoS | Retain | 说明 |
|-------|------|-----|--------|------|
| `ecoflow/device/<uid>/status` | 设备 → 云端 | 1 | true | 设备上线/离线状态 |
| `ecoflow/device/<uid>/telemetry` | 设备 → 云端 | 0（正常）/ 1（告警）| false | 遥测数据（[→ AC-5]）|
| `ecoflow/device/<uid>/events/offline` | 设备 → 云端 | 1 | false | 离线事件补传（[→ AC-16]）|
| `ecoflow/device/<uid>/cmd` | 云端 → 设备 | 1 | false | 指令下发（设备订阅）|
| `ecoflow/device/<uid>/cmd/ack` | 设备 → 云端 | 1 | false | 指令执行结果（[→ AC-8]）|
| `ecoflow/device/<uid>/cert/renew` | 设备 → 云端 | 1 | false | 证书轮换请求（[→ AC-13]）|
| `ecoflow/device/<uid>/ota/status` | 设备 → 云端 | 1 | false | OTA 进度上报（[→ AC-10]）|
| `ecoflow/device/<uid>/lwt` | Broker 代发 | 1 | true | 遗嘱消息（设备离线时发布）|

[MUST] 所有 Topic 中的 `<uid>` 必须与设备证书中的 CN（Common Name）一致（Broker 侧校验，防止设备冒用他人 Topic）。
