---
type: structure
scope: system
module: iot
updated: 2026-07-04
---

# IoT 网关 — 系统架构

## 系统定位

IoTGateway 是 EcoFlow PowerStation Pro / PowerHub 产品线的云端通信枢纽，运行于 ESP32-S3 主控 MCU（`src/iot/`），负责设备与 AWS IoT Core 之间的全部数据交换：MQTT 长连接、Device Shadow 同步、遥测上报、云端指令下发、OTA 升级、离线补传。业务规则与验收标准的唯一事实来源见 `knowledge/domain/iot-cloud/device-management.md`；本文档只描述**代码如何组织**。

## 内部组件

```
                        ┌─────────────────────────────┐
iot_telemetry_queue ───►│                             │
(EMS/BMS 产生)          │                             │──► MQTT Broker
                        │       IoTGateway            │    (AWS IoT Core)
MQTT Broker ───────────►│   (Task_IoT_Main 调度)      │
(cmd / shadow delta)    │                             │──► ems_mode_switch()
                        │                             │    (仅此一条写路径)
                        └─────────────────────────────┘
```

| 组件 | 文件 | 职责 |
|------|------|------|
| MQTT Client | `src/iot/mqtt_client.c` | 连接/心跳/指数退避重连/Wi-Fi↔4G 切换（RULE-IOT-002） |
| Shadow Sync | `src/iot/shadow_sync.c` | Device Shadow desired/reported 协调、版本冲突处理 |
| OTA Manager | `src/iot/ota_manager.c` | OTA 状态机、分片下载、断点续传（RULE-IOT-005） |
| Telemetry Publisher | `src/iot/telemetry_pub.c` | 消费 `iot_telemetry_queue`，按 QoS 策略发布遥测 |
| Cmd Handler | `src/iot/cmd_handler.c` | 云端指令去重（REG_CMD_LOG）、执行结果 ACK |
| Offline Queue | `src/iot/offline_queue.c` | 网络断开时写 Event 分区，网络恢复后批量补传（RULE-IOT-008） |

**入口：** `iot_core_start()` → 创建 `Task_IoT_Main`（FreeRTOS 优先级 `PRIO_TELEMETRY=2`，栈 `STACK_IOT_WORDS=2048`，见 `knowledge/coding-standard/firmware.md`）。

## 模块边界约束

**IoT 只做协议翻译，不直接操作任何寄存器或其他模块内部状态。**

| 交互对象 | 方向 | 接口 | 自主负责范围外 |
|---------|------|------|--------------|
| EMS/BMS 遥测 | 读 | `iot_telemetry_queue`（消息队列，EMS 侧产生，见 `ems-system.md`） | 不反向读取 `bms_status_t`/`mppt_status_t` 共享内存 |
| 云端模式切换指令 | 写 | `ems_mode_switch(target_mode)`（EMS 对外 API，见 `ems-system.md` §模式切换规则） | **不得**直接写 `ems_setpoint_queue` 或继电器 GPIO |
| Bootloader | 间接 | `REG_OTA_STATE` / `REG_OTA_PROGRESS`（NVS 持久化寄存器） | 不实现回滚逻辑（Bootloader 自身职责） |

[MUST NOT] IoT 任务直接写 `ems_setpoint_queue`：云端下发 `set_mode` 指令时，`cmd_handler.c` 必须调用 `ems_mode_switch()` 并等待 `ems_get_mode_status()` 返回 `MODE_SWITCH_DONE`，再发布 ACK。这与 EMS 侧"禁止直接写继电器 GPIO"的约束是同一条边界的两端。

## Device Shadow 同步

AWS IoT Device Shadow 用于云端与设备之间的状态镜像，解决 App 离线下发配置、设备离线恢复后追平配置的场景（遥测数据走 RULE-IOT-003 的独立通道，不经过 Shadow）。

**Shadow 文档结构：**

```json
{
  "state": {
    "desired":  { "mode": "backup_priority", "reserve_soc": 20 },
    "reported": { "mode": "grid_tied",       "reserve_soc": 20 }
  },
  "version": 42
}
```

**同步流程：**

```
设备订阅 ecoflow/device/<uid>/shadow/update/delta（QoS 1）
  → 收到 delta（desired 与 reported 的差集）
  → 逐字段校验合法性（超出范围的字段拒绝，不静默丢弃整条 delta）
  → 合法字段调用对应本地 API（如 mode 字段 → ems_mode_switch()）
  → 执行成功 → 发布 reported 状态到 shadow/update（QoS 1），version + 1
  → 执行失败 → 不更新 reported，发布 shadow/get 请求最新 desired 重新比对
```

**版本冲突处理：**

[MUST] 设备本地维护 `shadow_local_version`，仅接受 `version` 大于本地记录的 delta，防止网络乱序导致状态回退。  
[MUST NOT] 设备主动覆盖云端 `desired` 字段（`desired` 只能由 App/规则引擎写入，设备只写 `reported`）。  
**上线时全量同步：** 设备每次 MQTT 重连后主动发布 `shadow/get` 请求当前 Shadow 全量文档一次，而非仅依赖增量 delta（防止断线期间的 delta 丢失导致本地状态与云端永久不一致）。

## 数据流全图

```
[遥测输入]                                    [云端指令输入]
  ems_telemetry_t ──► iot_telemetry_queue        MQTT cmd topic
        │                    │                        │
        ▼                    ▼                        ▼
  Task_IoT_Main (100ms 轮询队列 / 事件驱动 MQTT 回调)
        │                    │                        │
        ▼                    ▼                        ▼
  telemetry_pub.c      shadow_sync.c            cmd_handler.c
        │                    │                        │
        ▼                    ▼                        ▼
  MQTT publish         ems_mode_switch()        REG_CMD_LOG 去重
  (telemetry topic)    (仅当 delta 通过校验)         │ ACK
        │                                             ▼
        ▼                                       MQTT publish
  网络断开时 ──► offline_queue.c ──► Event 分区   (cmd/ack topic)
                       │
                       ▼
              网络恢复后批量补传
              (events/offline topic)
```

## 参考

- 业务规则与 AC：`knowledge/domain/iot-cloud/device-management.md`
- EMS 对外 API 与边界：`knowledge/structure/ems-system.md`
- 固件编码规范：`knowledge/coding-standard/firmware.md`
- 历史陷阱：`src/iot/EXPERIENCE.md`
