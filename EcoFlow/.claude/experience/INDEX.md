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
