# IoT 模块 — 任务经验

> 加载时机：开始执行 IoT 相关任务前（MQTT / Shadow / OTA / 遥测 / 离线补传）。  
> 背景：以下陷阱均在 EcoFlow 设备 IoT 网关实际研发中出现，Agent 多次在同类任务中重复触发。

---

## 新增/修改 MQTT 连接逻辑 — 执行检查清单

每次修改 `mqtt_client.c`（RULE-IOT-002 相关代码）时：

1. 重连退避 → **确认使用指数退避 + 随机抖动**，不是固定间隔（见陷阱 1）
2. Wi-Fi 切 4G → **确认切换逻辑不重复发布遥测**（SEQ_NUM 去重，见 `device-management.md` RULE-IOT-002 [MUST]）
3. 重连成功后 → **确认主动发布一次 `shadow/get` 做全量同步**（见 `iot-system.md` §Device Shadow 同步）

## 新增/修改 OTA 逻辑 — 执行检查清单

每次修改 `ota_manager.c`（RULE-IOT-005 相关代码）时：

1. 差分升级（`patch_from` 非 null）→ **必须校验当前固件版本与 `patch_from` 完全匹配**（见陷阱 2）
2. 分片写入前 → **确认 OTA 分区剩余空间已预检查**（`fw_size` 对照 Flash 分区表）
3. MD5 校验失败 → **确认清除 OTA 分区后原固件继续运行，不触发重启**

## 新增/修改指令处理逻辑 — 执行检查清单

每次修改 `cmd_handler.c`（RULE-IOT-004 相关代码）时：

1. 收到指令 → **必须先查 `REG_CMD_LOG` 去重，再校验参数**（见陷阱 3）
2. `set_mode` 指令 → **必须调用 `ems_mode_switch()`，不得直接写 `ems_setpoint_queue`**（见 `iot-system.md` §模块边界约束）
3. 执行超时 > 30s → **必须返回 `{"result": "timeout"}`，不静默失败**

---

## 陷阱 1：区域性断网恢复后的"上线风暴"压垮 Broker

**已触发次数：** 1 次（2025-Q3，某区域 ISP 光纤中断 40 分钟，恢复瞬间约 1.2 万台设备同时重连）

**症状：** 网络恢复后 5 秒内，MQTT Broker 连接请求速率激增至平时的 200 倍，AWS IoT Core 触发限流（`ThrottlingException`），大量设备重连失败又立即重试，形成正反馈风暴，实际恢复时间超过 25 分钟（预期应在设备侧 30s 退避窗口内平滑恢复）。

**根因：** 重连退避实现是固定的指数退避（0s → 5s → 20s → 60s），**所有设备在同一时刻断网，也几乎在同一时刻走到同一退避阶段**，重试请求高度同步，没有随机抖动打散。

**正确实现：**

```c
// ✅ 正确：退避基础值 + 随机抖动（抖动幅度 = 基础值的 ±30%）
static uint32_t mqtt_reconnect_backoff_ms(uint8_t retry_count) {
    static const uint32_t base_ms[] = { 0, 5000, 20000, 60000 };
    uint32_t base = base_ms[retry_count < 4 ? retry_count : 3];
    if (base == 0U) { return 0U; }

    // 设备 UID 派生的伪随机种子，保证同一设备每次抖动值不同，但可复现调试
    uint32_t jitter_range = base * 30U / 100U;
    uint32_t jitter = (device_uid_hash() ^ xTaskGetTickCount()) % (2U * jitter_range);
    return base - jitter_range + jitter;   // base ± 30%
}

// ❌ 错误：固定退避，无抖动
static uint32_t mqtt_reconnect_backoff_ms_WRONG(uint8_t retry_count) {
    static const uint32_t base_ms[] = { 0, 5000, 20000, 60000 };
    return base_ms[retry_count < 4 ? retry_count : 3];
}
```

**规则：** 第 2 次重试起（1s 以上的退避）**必须**叠加 ±30% 随机抖动；第 60s 及以后的长期重试**必须**保持抖动，防止长时间断网场景下设备仍然同步。  
**参考规格：** `knowledge/domain/iot-cloud/device-management.md` RULE-IOT-002

---

## 陷阱 2：差分 OTA 应用到错误基础版本导致设备变砖

**已触发版本：** 2025-Q4 灰度发布 v2.4.0 差分包（`patch_from: "2.3.x"`）

**症状：** 约 300 台设备（固件版本为 v2.2.x，跳过了 v2.3.0 更新）应用差分包后启动失败，Bootloader 60s 自检失败触发回滚，但由于差分包本身已破坏 App 分区数据，回滚后固件仍无法正常启动，需现场 USB 刷机恢复。

**根因：** `ota_manager.c` 在下载差分包前，只检查了 `fw_version` 目标版本号，**没有校验设备当前运行版本是否与 `patch_from` 声明的基础版本一致**：

```c
// ❌ 问题代码：只查目标版本，不查基础版本匹配
bool ota_precheck_WRONG(const ota_cmd_t *cmd) {
    if (g_bms_status.soc < 20U) { return false; }
    if (ota_partition_free_space() < cmd->fw_size) { return false; }
    return true;   // 漏掉 patch_from 校验
}
```

**正确实现：**

```c
// ✅ 正确：差分包必须校验当前版本落在 patch_from 声明的兼容范围内
bool ota_precheck(const ota_cmd_t *cmd) {
    if (g_bms_status.soc < 20U) { return false; }
    if (ota_partition_free_space() < cmd->fw_size) { return false; }

    if (cmd->patch_from != NULL) {
        char current_ver[16] = {0};
        fw_version_get_string(current_ver, sizeof(current_ver));
        if (!fw_version_matches_pattern(current_ver, cmd->patch_from)) {
            // 版本不匹配：拒绝差分包，上报云端要求下发全量包
            iot_publish_ota_status(OTA_STATUS_PATCH_BASE_MISMATCH);
            return false;
        }
    }
    return true;
}
```

**规则：** 差分 OTA（`patch_from` 非 null）**必须**校验当前固件版本落在声明的兼容范围内；不匹配时拒绝下载并上报 `PATCH_BASE_MISMATCH`，由云端改发全量包，**不得**静默尝试应用不兼容的差分包。  
**参考规格：** `knowledge/domain/iot-cloud/device-management.md` RULE-IOT-005

---

## 陷阱 3：云端指令重复投递导致模式切换被执行两次

**已触发版本：** 2025-Q2（MQTT QoS 1 消息在弱网环境下重复投递是协议允许行为，非 Bug）

**症状：** 用户通过 App 下发一次 `set_mode: backup_priority` 指令，设备收到两条内容相同、`cmd_id` 相同的 MQTT 消息（Broker 侧重传），`cmd_handler.c` 对两条消息都执行了 `ems_mode_switch()`，导致模式切换在极短时间内被触发两次，第二次切换与第一次的握手时序冲突，EMS 侧短暂进入异常状态并上报误报故障。

**根因：** `cmd_handler.c` 的去重检查写在参数校验和执行**之后**，而不是收到消息的**第一步**：

```c
// ❌ 问题代码：先执行，后记录，去重检查形同虚设
void cmd_handler_on_message_WRONG(const cmd_msg_t *msg) {
    if (!cmd_validate_params(msg)) { return; }
    ems_mode_switch(msg->params.mode);          // 先执行
    cmd_log_append(msg->cmd_id);                // 后记录，中间窗口内的重复消息会绕过去重
}
```

**正确实现：**

```c
// ✅ 正确：去重检查是收到消息后的第一个动作
void cmd_handler_on_message(const cmd_msg_t *msg) {
    if (cmd_log_contains(msg->cmd_id)) {
        // 已执行过：直接返回 ACK，不重复执行（幂等）
        iot_publish_cmd_ack(msg->cmd_id, "ok", NULL);
        return;
    }
    if (!cmd_validate_params(msg)) {
        iot_publish_cmd_ack(msg->cmd_id, "error", "invalid_params");
        return;
    }
    // 先记录 cmd_id 再执行：确保执行过程中收到的重复消息也能被挡住
    cmd_log_append(msg->cmd_id);
    ems_mode_switch(msg->params.mode);
    iot_publish_cmd_ack(msg->cmd_id, "ok", NULL);
}
```

**规则：** `REG_CMD_LOG` 去重检查**必须**是消息处理的第一步（先查重、再校验参数、再执行），且 `cmd_log_append()` 必须在调用执行逻辑**之前**完成，防止执行期间到达的重复消息绕过去重窗口。  
**参考规格：** `knowledge/domain/iot-cloud/device-management.md` RULE-IOT-004 [MUST NOT]

---

## 参考

- 业务规则与 AC：`knowledge/domain/iot-cloud/device-management.md`
- 架构与模块边界：`knowledge/structure/iot-system.md`
- 固件编码规范：`knowledge/coding-standard/firmware.md`
