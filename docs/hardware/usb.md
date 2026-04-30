# CosmoRadio V4 — USB 接口方案设计

> 目标：单根 USB-C 线连接 PCB 与平板，同时实现 HID 数据通信 + 外部充电器给平板充电

## 2026-04-30 修正结论

本文件下面的方案分析保留为历史参考，但当前 V4 原型的 USB/充电判断已经调整：

1. 市面上低价可买到的通常是 OTG + 充电转接线/小扩展坞，不是可直接上板的裸模块。
2. 外置长线方案只能验证电气功能，不能满足产品形态。
3. 第一阶段应购买 3-5 个低价 OTG + 充电转接器，验证 Tab A9 + ESP32-S3 HID + 充电是否稳定。
4. 若稳定，拆解最小的一款，取内部 PCB 作为内置子板，用短线或焊点接入主 PCB。
5. 被动 VBUS 注入方案降级为实验项，不能作为最稳妥主路径。
6. CH224K、HUSB238 这类 PD Sink/诱骗芯片不能单独解决“平板做 USB Host，同时平板作为供电 Sink 充电”的完整问题。

当前权威记录以 [pcb/README.md](../../pcb/README.md) 为准。

## 目标设备

| 项目 | 规格 |
|------|------|
| 平板 | Samsung Galaxy Tab A9 8.7" (SM-X110, Wi-Fi) |
| USB | Type-C 2.0 |
| OTG | 支持 (USB OTG 2.0) |
| PD | 支持 (USB PD 2.0, Power Role Swap) |
| 充电 | 15W (5V/3A) |
| 电池 | 5100 mAh |
| 系统 | Android 13 / One UI 5.1 |

**关键特性**：
- **USB 2.0** → 只需 D+/D- 一对数据线，无需 USB 3.x 的 SS 高速对
- **USB PD 2.0** → 具备 Power Role Swap 能力，方案 C (PD 控制器) 的硬件基础已具备
- **15W / 5V3A** → 方案 B 的 SS34 二极管 (3A 额定) 刚好匹配最大充电电流

## 当前状态（已替换）

| 组件 | 规格 | 单价 |
|------|------|------|
| FPC Type-C 弯头线 | ESP32 → PCB USB-C 座 | ¥24.80 |
| Type-C 一分二数据线 | 充电 + OTG 分流 | ¥33.00 |
| **合计** | **占单套成本 43%** | **¥57.80** |

当前方案需要两根线 + 外部 Y 型分线器，成本高且走线复杂。

## 需求分析

```
                    ┌──────────────────────┐
  [USB-C 充电器] ──→│  J6 (充电输入)         │
     5V/2A+        │                      │
                    │    CosmoRadio PCB    │
                    │                      │
                    │  ESP32 GPIO19/20 ──→ │──→ [J5 (数据+供电输出)] ──→ [平板]
                    │  (USB HID D+/D-)     │     单根 USB-C 线
                    └──────────────────────┘
```

**数据流**：ESP32 (USB Device/HID) → D+/D- → 平板 (USB Host)
**电力流**：充电器 5V → J6 VBUS → PCB → J5 VBUS → 平板充电

## 核心技术挑战

USB-C 协议中，数据角色和供电角色默认绑定：
- **DFP (Host)** = 数据主机 = 供电方 (Source)
- **UFP (Device)** = 数据从机 = 受电方 (Sink)

我们需要的是：**平板做数据主机 (Host)，但同时接受外部供电 (Sink)**。这在标准 USB-C 中需要 PD Power Role Swap 才能实现。

但实际上，大多数 Android 平板的充电 IC 和 USB 数据通路是独立的——只要 VBUS 上有 ≥4.5V 电压，充电 IC 就会开始充电，不管 USB 控制器处于 Host 还是 Device 模式。这就是市面上大量 "OTG+充电" Y 型线能工作的原理。

---

## 方案对比

| | 方案 A：成品 OTG+充电模块 | 方案 B：PCB 被动 VBUS 注入 | 方案 C：PD 控制器 IC |
|---|---|---|---|
| **原理** | 购买成品 2-in-1 适配器 | 双 USB-C 座 + 肖特基二极管 | FUSB302/WUSB3801 IC |
| **物料成本** | ¥15-25/套 | ¥6-10/套 | ¥15-20/套 |
| **PCB 改动** | 无（外置模块） | 新增 J6 座 + 二极管 + 电阻 | 新增 IC + 外围电路 |
| **固件改动** | 无 | 无 | 需 I2C 驱动 + PD 协商 |
| **兼容性** | 高（模块已处理 PD） | 中（依赖平板充电 IC 行为） | 高（标准协议） |
| **复杂度** | 极低 | 低 | 高 |
| **推荐场景** | 首选，快速验证 | 成本敏感，已验证平板兼容 | 需要兼容所有设备 |

---

## 方案 A：成品 OTG+充电模块（推荐首选）

### 原理

购买现成 "USB-C OTG + PD 充电二合一" 适配器（内置 MCU + MOSFET 处理 PD 协商），安装在外壳内部。PCB 只需要一个 USB-C 座（J5）输出 HID 数据。

### 架构

```
[充电器] → [OTG+PD 适配器 充电口]
                    │
[PCB J5] → [OTG+PD 适配器 数据口] → [单根线] → [平板]
```

### 物料清单

| 组件 | 规格 | 参考价 | 采购关键词 |
|------|------|--------|-----------|
| OTG+充电适配器 | USB-C 二合一，PD 60W | ¥15-25 | "USB-C OTG 充电 二合一 转接器" |
| USB-C 短线 | PCB J5 → 适配器，15cm | ¥3-5 | "USB-C 公对公 短线 25cm" |

**单套成本：¥18-30（对比当前 ¥57.80，节省 48-69%）**

### 优点
- 零 PCB 设计改动，零固件改动
- PD 协商由模块内部 MCU 处理，兼容性最好
- 如模块坏了可直接更换

### 缺点
- 外壳内部需要给模块留空间
- 增加一个连接节点（可靠性略降）
- 外观不够整合

### 选型建议
淘宝搜索 "USB-C OTG 充电 二合一"，选择：
- 支持 PD 快充（至少 18W，最好 60W）
- 输出端为 USB-C（不是 USB-A）
- 体积小巧，适合内嵌

---

## 方案 B：PCB 被动 VBUS 注入（推荐量产）

### 原理

在 PCB 上增加第二个 USB-C 座（J6，充电输入），通过肖特基二极管将充电器 VBUS 注入到平板连接的 J5 VBUS 线上。利用 Android 平板充电 IC 独立于 USB Host 控制器的特性，实现 OTG 数据 + 外部充电同时工作。

### 电路原理图

```
J6 (充电输入 USB-C)              J5 (平板输出 USB-C)
┌─────────┐                     ┌─────────┐
│ VBUS  ──┼── SS34 ──┬───────── │ VBUS    │
│ CC1 ──┼── 5.1kΩ ─┤GND       │ CC1 ──┼── 5.1kΩ ── GND
│ CC2 ──┼── 5.1kΩ ─┤GND       │ CC2 ──┼── 5.1kΩ ── GND
│ D+   NC │         │          │ D+ ←────── ESP32 GPIO20
│ D-   NC │         │          │ D- ←────── ESP32 GPIO19
│ GND  ──┼─────────┴───────── │ GND     │
│ SHLD ──┼── GND              │ SHLD ──┼── GND
└─────────┘                     └─────────┘
                                     │
                              DevKitC 5V ←┘ (ESP32 供电)
```

### CC 引脚配置说明

| 端口 | CC 配置 | 电阻 | 作用 |
|------|---------|------|------|
| J6 (充电输入) | Rd pull-down | 2× 5.1kΩ to GND | 对充电器呈现为 Sink，充电器输出 5V |
| J5 (平板输出) | Rd pull-down | 2× 5.1kΩ to GND | 对平板呈现为 UFP Device，平板进入 Host 模式 |

### 供电路径

**无充电器时**：
```
平板 VBUS (5V) → J5 VBUS → DevKitC 5V → ESP32 供电
（二极管反偏，J6 不导通）
```

**接入充电器时**：
```
充电器 (5V~5.2V) → J6 VBUS → SS34 (Vf≈0.3V) → ~4.7-4.9V → J5 VBUS
平板充电 IC 检测到 VBUS 电压 → 开始充电
同时：ESP32 D+/D- 维持 HID 通信不中断
```

大多数充电器输出 5.0-5.2V，经肖特基二极管后约 4.7-4.9V，足以触发平板充电 IC（阈值通常 4.0-4.5V）。平板自身在 Host 模式也会输出约 5V VBUS，但当外部供电电流能力远大于平板 VBUS 输出时（充电器 2A+ vs 平板 OTG 输出 500mA），平板充电 IC 会净吸收电流，实现充电。

### 物料清单

| 组件 | 封装 | 数量 | 参考价 | 备注 |
|------|------|------|--------|------|
| USB-C 母座转接板 (DIP) | 2.54mm through-hole | 2 | ¥2-3/个 | "USB-C 母座 转接板 DIP 2.54" |
| SS34 肖特基二极管 | SMA/DO-214AC | 1 | ¥0.3 | Vf=0.3V@3A，防倒灌 |
| 5.1kΩ 电阻 | 0805 或直插 | 4 | ¥0.1 | CC 引脚配置 |
| **合计** | | | **¥5-7/套** | |

**单套成本：¥5-7（对比当前 ¥57.80，节省 88-91%）**

### 模块选型：USB-C 母座转接板

选择 DIP (2.54mm 间距) 直插模块，引出至少 VBUS / GND / D+ / D- / CC1 / CC2 六个引脚。

推荐选择条件：
- 引出全部引脚（至少 6P，最好 12P/16P）
- 2.54mm 排针间距，可直接插面包板或焊接排母
- 有固定孔（M2 或 M2.5）

淘宝搜索关键词：
- "USB Type-C 母座 转接板 DIP"
- "USB-C breakout board 2.54mm"
- "Type-C 测试板 引脚全引出"

### PCB 设计改动

在现有 80×50mm PCB 基础上：
1. **新增 J6 位置**：USB-C 充电输入座，放置在 PCB 边缘（与 J5 同侧或对侧）
2. **新增 SS34 二极管**：J6 VBUS → SS34 → J5 VBUS 路径
3. **新增 4× 5.1kΩ 电阻**：J5 和 J6 各两个 CC pull-down
4. **走线**：VBUS 走线宽度 ≥ 1mm（承载 2A）

如果使用 DIP 转接板模块，J5 和 J6 可以用排母座接口代替板载 USB-C 座，大幅降低 PCB 贴片复杂度。

### 兼容性注意

此方案依赖平板内部充电 IC 在 USB Host 模式下仍接受 VBUS 充电。需要实测验证：

**验证步骤**：
1. 用面包板搭建原型：两个 USB-C 转接板 + SS34 + 5.1kΩ 电阻
2. 接入充电器和平板，确认平板是否进入充电状态
3. 同时接入 ESP32 HID，确认数据通信不受影响
4. 测量 VBUS 电压、充电电流、温升

**已知兼容情况**：
- 三星 Galaxy Tab 系列：历史上对 OTG+充电支持较好
- 大部分 Android 10+ 设备：充电 IC 独立于 USB Host 模块

**不兼容的补救**：若平板在 Host 模式拒绝 VBUS 充电，回退到方案 A。

---

## 方案 C：PD 控制器 IC（参考，暂不推荐）

### 原理

使用 FUSB302 或 WUSB3801 等 USB PD 控制器 IC，在固件中实现 PD 协议协商，执行 Power Role Swap（将平板从 Source 切换为 Sink）和 Data Role Swap（保持平板为 Host），从而标准化地解决供电和数据角色分离问题。

### 关键 IC

| IC | 价格 | 接口 | 功能 | 备注 |
|----|------|------|------|------|
| FUSB302 | ¥3-5 | I2C | CC 检测 + PD BMC 通信 | 开源社区支持好，需 MCU 驱动 |
| WUSB3801 | ¥3-4 | I2C/GPIO | CC 检测 + DRP 自动切换 | 更简单，但不支持完整 PD |
| TPS65987 (TI) | ¥15+ | I2C | 完整 PD 3.0 控制器 | 贵，功能过剩 |

### 复杂度评估

- 需要 FUSB302 + 外围电路（10+ 被动元件）
- 需要 ESP32 I2C 驱动 + PD 协议栈固件（约 500-1000 行代码）
- 需要 MOSFET 做 VBUS 开关
- PCB 面积增加约 15×10mm
- 调试和验证周期长

**结论：复杂度远超项目需求，留作未来需要兼容所有设备时的升级路径。**

---

## 推荐实施路径

```
第一步：方案 B 原型验证（面包板，1-2 天）
  │
  ├── 成功 → 方案 B 集成到 PCB V4
  │          成本 ¥5-7/套，节省 ¥50+/套
  │
  └── 失败（平板不充电）→ 方案 A
                          成本 ¥18-30/套，仍节省 ¥28-40/套
```

### 第一步：面包板验证方案 B

所需材料：
- 2× USB-C 母座转接板（DIP）
- 1× SS34 肖特基二极管
- 4× 5.1kΩ 电阻
- 面包板 + 杜邦线
- ESP32-S3 DevKitC（现有）
- 充电器 + USB-C 线 + 平板

接线验证 VBUS 注入是否能触发平板充电，同时确认 HID 不中断。

### 第二步：PCB 集成

验证通过后，在 KiCad 原理图中：
1. 新增 J6 (USB-C 充电输入) 连接器符号
2. 新增 SS34 二极管符号
3. 新增 4× 5.1kΩ CC 电阻
4. 更新 PCB layout，J6 放置在板边缘
5. VBUS 走线加宽到 1mm+

---

## 附录 A：USB-C 引脚定义速查

```
USB-C 母座 (Receptacle) 引脚定义 — 简化 USB 2.0 用途

Pin  Name    用途
A1   GND     地
A4   VBUS    电源 5V
A5   CC1     Configuration Channel 1
A6   D+      USB 2.0 数据+
A7   D-      USB 2.0 数据-
A8   SBU1    (不用)
A9   VBUS    电源 5V
A12  GND     地

B1   GND     地
B4   VBUS    电源 5V
B5   CC2     Configuration Channel 2
B6   D+      USB 2.0 数据+ (连接到 A6)
B7   D-      USB 2.0 数据- (连接到 A7)
B8   SBU2    (不用)
B9   VBUS    电源 5V
B12  GND     地

USB 2.0 简化接法：
- VBUS: A4+A9+B4+B9 全部短接
- GND:  A1+A12+B1+B12 全部短接
- D+:   A6+B6 短接
- D-:   A7+B7 短接
- CC1:  A5 (独立)
- CC2:  B5 (独立)
```

## 附录 B：CC 引脚电阻配置速查

| 角色 | CC 电阻 | 阻值 | 效果 |
|------|---------|------|------|
| Sink (UFP/Device) | Rd pull-down to GND | 5.1kΩ | 告知对方"我是设备" |
| Source (DFP/Host) Default USB | Rp pull-up to VBUS | 56kΩ | 告知对方"我是主机，可提供默认电流" |
| Source 1.5A | Rp pull-up to VBUS | 22kΩ | 告知对方"可提供 1.5A" |
| Source 3A | Rp pull-up to VBUS | 10kΩ | 告知对方"可提供 3A" |

本项目 J5/J6 均使用 **Rd 5.1kΩ pull-down**（Sink 配置）。

## 附录 C：参考资料

- [All About USB-C: Example Circuits (Hackaday)](https://hackaday.com/2023/08/07/all-about-usb-c-example-circuits/)
- [USB Type-C Configuration Channel (Benson Leung)](https://medium.com/@leung.benson/usb-type-c-s-configuration-channel-31e08047677d)
- [Simultaneously Charging and OTG in Type C (TI E2E)](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/949928/simultaneously-charging-and-otg-in-type-c)
- [Teardown: USB-C OTG Adapter with PD Charging (Gough's Tech Zone)](https://goughlui.com/2023/10/29/teardown-t-tersely-usb-c-otg-adapter-with-pd-charging-pass-through/)
- [USB-C OTG + Charge Discussion (XDA Forums)](https://xdaforums.com/t/usb-otg-charge.3588019/page-2)
- [ESP32-S3-USB-OTG Dev Board (Espressif)](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32s3/esp32-s3-usb-otg/user_guide.html)
- [USB OTG Host Adapter with Charging (Elektroda)](https://www.elektroda.com/rtvforum/topic3449427.html)
