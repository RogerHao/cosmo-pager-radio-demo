# CosmoRadio V4 — PCB 载板规格 (v2.0)

> **版本**：v2.0（2026-05-18 整理，对应 PCB Plan v2）
> **范围**：技术方案验证 + 单套原型制作；JLCPCB 免费打样 5 片
> **设计文档**：详细执行步骤见 `~/.claude/plans/iridescent-snuggling-planet.md`
> **GPIO 权威表**：`/CLAUDE.md` "GPIO Pin Assignments"

---

## 设计理念

**Carrier Board（载板）** — ESP32-S3 DevKitC N16R8 通过两条 1×22 单排母插入 PCB，所有外设通过 5 路 XH2.54 JST 连接器即插即用。**整块板的本质是"连接器转接板 + EC11 RC 去抖网络"**——零有源元件，只有 8 个 0805 贴片被动件 + 6 个 THT 连接器。

### 为什么是 DevKitC N16R8 + carrier board

| 对比项 | ESP32-S3 SuperMini (V3) | ESP32-S3 DevKitC N16R8 (V4) |
|--------|------------------------|----------------------|
| USB HID | TinyUSB ✓ | TinyUSB ✓（同一套代码）|
| BLE | 有（未用）| 无（不需要）|
| GPIO 数量 | 11 可用 | 36+ 可用 |
| 价格 (1688) | ¥15 | ¥8-10 |
| 尺寸 | 25×18mm | 70×27mm |
| Flash / PSRAM | 4MB / 0 | 16MB / 8MB Octal |
| 固件迁移量 | — | 仅改 GPIO 编号 + sdkconfig |

ESP32-S3 有原生 USB OTG，TinyUSB HID 代码直接跑。GPIO 多 3 倍，方便加 NFC。N16R8 的 16MB Flash + 8MB PSRAM 足够 NFC 大缓冲。

### V3 问题 → V4 解决

| V3 问题 | V4 方案 |
|---------|---------|
| 飞线杂乱，杜邦线无锁扣 | PCB 走线 + JST-XH 带卡扣连接器 |
| 万能板空间局促 + 容易脱焊 | 100×100mm 双面 PCB，机械稳定 |
| 组装需焊接技能 | 全插拔 + 螺丝固定，附图文指南 |
| SuperMini GPIO 不够 | DevKitC 36+ GPIO，充裕 |
| 旋钮一格一格不准 | EC11 A/B 加 10kΩ + 10nF RC 去抖 |
| USB-C 母座焊接难 + 充电方案不稳 | OTG dongle (YK16-09E V1) 内置子板，主 PCB 不上 USB-C |

---

## 原理图

### GPIO 引脚分配（V4 终版）

> 完整权威表见 [/CLAUDE.md](../../CLAUDE.md)。下表为 PCB 视角概览。

| 功能 | GPIO | 连接器 | PCB 位置 |
|------|------|--------|---------|
| EC11-L (用户左旋钮) A/B/SW | 42 / 41 / 40 | J1 (5P) | **PCB 左侧中段** |
| EC11-R (用户右旋钮) A/B/SW | 17 / 18 / 8 | J2 (5P) | **PCB 右侧中段** |
| Action Button | 1 | J3 (2P) | **PCB 左侧靠前** |
| RC522 NFC RST/IRQ/MISO/MOSI/SCK/CS | 4 / 5 / 6 / 7 / 15 / 16 | J4 (8P) | **PCB 右侧** |
| OTG USB D-/D+ | 19 / 20 | J5 (4P) | **PCB 左侧靠后** (near USB-C 端) |
| 板载 RGB LED | 48 | DevKitC 板载 | — |

> "PCB 位置" 列基于 DevKitC 安装朝向（USB-C OTG 朝外壳后侧 = PCB 顶部）。`pcb/asset/ESP32-S3-DevKitC-N16R8.png` 是 datasheet 标准视角（USB-C 在下），用户安装 = 180° 旋转后视角。

### 连接器定义（5 路 XH2.54）

| 连接器 | 类型 | 引脚定义（从 pin 1 顺序）| 线缆长度 | 方向 |
|--------|------|----------|---------|------|
| J1 | XH2.54 5P 立式直针 | A=GPIO42, B=GPIO41, SW=GPIO40, GND, GND | 20cm | → 左旋钮 (EC11) |
| J2 | XH2.54 5P 立式直针 | A=GPIO17, B=GPIO18, SW=GPIO8, GND, GND | 20cm | → 右旋钮 (EC11) |
| J3 | XH2.54 2P 立式直针 | SIG=GPIO1, GND | 25cm | → Kailh BOX 按钮 |
| J4 | XH2.54 8P 立式直针 | CS=16, SCK=15, MOSI=7, MISO=6, IRQ=5, GND, RST=4, 3V3 | 15cm | → RC522 NFC mini |
| J5 | XH2.54 4P 立式直针 | VBUS, D-=19, D+=20, GND | <10cm | → OTG dongle USB-A 拆后 4 飞线 |

> **J4 引脚顺序与 RC522 mini 模块物理排针 1:1**，端子线直压无需交叉。详见 [docs/hardware/nfc.md](../hardware/nfc.md)。
> **J5 引脚顺序与 USB-A 公头物理引脚顺序一致**（VBUS, D-, D+, GND），方便 dongle 拆解后直焊。详见 [docs/hardware/otg-adapter.md](../hardware/otg-adapter.md)。

### DevKitC 插座（两条 1×22 单排母）

| Ref | 类型 | 间距 |
|-----|------|------|
| U1A | 1×22P 排母 2.54mm 立式 | — |
| U1B | 1×22P 排母 2.54mm 立式 | — |
| U1A ↔ U1B 中心距 | **22.86mm** (= 9 × 2.54mm pitch) | breadboard 兼容 |

**为什么用两条单排母而非一条 2×22 双排母**：
- 单排母可独立对齐，安装时容差大、不会因双排"一边歪导致整体插不进"
- 单排零件 LCSC 可选范围更大，本身更便宜
- 焊接工艺更简单（每条 22 个焊点串行做完再做下一条）

### EC11 RC 去抖网络（关键设计）

每个 EC11 旋钮的 A/B 信号各加：
- **10kΩ 上拉电阻**到 3V3（增强边沿陡度，比内部 ~45kΩ 强 4.5×）
- **10nF 电容**对 GND（与上拉电阻形成 RC 低通滤波器，τ = 100µs）

**工作原理**：EC11 机械触点抖动通常在 µs 级；10nF 电容把高频抖动吸收掉，但用户手转的 ~10 detent/s 信号（频率 <100Hz）原封通过。这是 Ben Buxton 1998 年《Rotary encoders》经典文档里的标准接法。

**布局要求**：R/C 紧贴各自的 J1/J2 连接器（A/B pin 旁 ≤5mm），电容对 GND 走线尽量短。

```
J1.1 (A=GPIO42) ──┬──── 10kΩ ──── 3V3
                  ├──── 10nF ──── GND
                  └─── 走线到 DevKitC GPIO42

J1.2 (B=GPIO41) ──┬──── 10kΩ ──── 3V3
                  ├──── 10nF ──── GND
                  └─── 走线到 DevKitC GPIO41

(J2 同结构，A=17 / B=18)
```

**不加去抖网络的 pin**：
- EC11 SW（按下事件慢，软件 debounce 足够）
- Action Button (J3 SIG, GPIO1)
- NFC SPI 信号（模块板载已有去耦）

### 电路要点

1. **USB HID 通路**：DevKitC native USB → 排针 GPIO19/20 → J5 4P → dongle USB-A 拆后 4 飞线 → dongle 输出 Type-C plug → 平板
2. **供电**：外部充电器 → dongle Type-C 母座 → dongle 内部 CC IC 协商 → 平板 (充电) + dongle 输出 5V 给 DevKitC (USB 通路)
3. **3V3 来源**：DevKitC 板载 AMS1117-3.3 LDO
4. **EC11 上拉**：A/B 各 10KΩ 上拉到 3V3，A/B 各 10nF 对 GND（共 8 个 0805 贴片件）
5. **NFC SPI**：SPI2 经 GPIO Matrix 走 GPIO 4/5/6/7/15/16（不是 FSPICLK 硬件 pin，因为那些 pin 在 octal PSRAM 占用范围内）
6. **板载 LED**：DevKitC GPIO48 板载 WS2812B RGB，不外接

---

## PCB 物理规格

| 参数 | 值 |
|------|-----|
| 尺寸 | **100mm × 100mm**（JLCPCB 免费打样上限）|
| 层数 | 2 层 |
| 板厚 | 1.6mm |
| 铜厚 | 1oz |
| 表面处理 | HASL（无铅）|
| 阻焊 | 黑色 |
| 丝印 | 白色，每个连接器标注接口名 + 引脚功能 + **"OTG USB-C: DO NOT PLUG"** 警示 |
| 安装孔 | 4× M2.5（四角，孔径 2.7mm）|

### 布局建议

```
                ↑ BACK (远离用户, USB-C 朝外)
   ┌────────────────────────────────────────────┐
   │ ⊙ H1                                ⊙ H2  │
   │                                            │
   │  ┌──────────┐                              │
   │  │ J5 USB   │  ◄── GPIO 19/20 + 5V/GND     │
   │  │   4P     │                              │
   │  └──────────┘                              │
   │                                            │
   │  ┌──────┐ ┌──────┐                         │
   │  │ U1A  │ │ U1B  │            ┌──────────┐ │
   │  │ 1×22 │ │ 1×22 │            │ J4 NFC   │ │
   │  │      │ │      │            │   8P     │ │
   │  │ 左列  │ │ 右列  │            └──────────┘ │
   │  │      │ │      │                         │
   │  │      │ │      │            ┌────────┐   │
   │  │      │ │      │            │ J2     │   │
   │  │      │ │      │            │ EC11-R │   │
   │  │      │ │      │            │  5P    │   │
   │  └──────┘ └──────┘            └────────┘   │
   │                                            │
   │   R3,R4,C3,C4 (10k/10n for ENC2)           │
   │                                            │
   │  ┌────────┐                                │
   │  │ J1     │ ◄── GPIO 42/41/40              │
   │  │ EC11-L │                                │
   │  │   5P   │                                │
   │  └────────┘                                │
   │                                            │
   │  R1,R2,C1,C2 (10k/10n for ENC1)            │
   │                                            │
   │  ┌────────┐                                │
   │  │ J3 BTN │ ◄── GPIO 1 + GND               │
   │  │   2P   │                                │
   │  └────────┘                                │
   │                                            │
   │   CosmoRadio V4 r1.0      OTG USB-C:       │
   │   dehonghao.com           DO NOT PLUG      │
   │ ⊙ H4                                ⊙ H3  │
   └────────────────────────────────────────────┘
                ↓ FRONT (朝向用户)
```

### 丝印标注

- 每个 JST 连接器旁标注：**接口名 + pin 顺序的信号名**（如 J4 旁标 `NFC | CS SCK MOSI MISO IRQ G RST 3V3`）
- 顶部丝印：`CosmoRadio V4 r1.0` + `dehonghao.com`
- **底部丝印警示**：`⚠ OTG USB-C: DO NOT PLUG`（必须，避免误插烧端口）
- 安装孔旁不丝印（避免遮挡螺丝）
- 所有丝印高 ≥ 1.0mm（JLC DFM 最小 0.8mm，留余量）

---

## 配套线缆（预压 JST-XH 端子）

| 线缆 | 规格 | JST 端 | 外设端 | 数量/套 |
|------|------|--------|--------|--------|
| EC11 线缆 ×2 | 5P × 20cm | JST-XH 5P 公 | 直焊 EC11 引脚 | 2 |
| Action Button 线缆 | 2P × 25cm | JST-XH 2P 公 | 焊到 Kailh BOX 轴 | 1 |
| NFC 线缆 | 8P × 15cm | JST-XH 8P 公 | 8P 排针压接到 RC522 | 1 |
| OTG dongle 线缆 | 4P × <10cm | JST-XH 4P 公 | 焊到 dongle 拆 USB-A 后的 4 焊盘 | 1 |
| dongle Type-C 输出 | Type-C plug + 短缆 | （dongle 自带）| 插入平板 | 1 |
| dongle Type-C 充电输入 | Type-C 母座 | （dongle 自带）| 接外部充电器 USB-C | 1 |

> 单套原型阶段：JST 端预压好，外设端预焊好，用户只需插 JST 到主板。

---

## 制造

| 项目 | 方案 | 成本 |
|------|------|------|
| PCB 打样 | JLCPCB 免费打样 5 片 | ¥0 + 国内运费 ~¥20 |
| SMT 贴片 | **不上**——单套原型，8 个 0805 手焊 ~5min | ¥0 |
| 手焊部分 | 2× 1×22 排母 + 5× JST 母座 + 8× 0805 (R+C) | ~15min/板 |

### 生产流程

```
KiCad 设计完成
  → JLCPCB 下单（仅打板，不贴片）
  → 5 片裸板到货（国内 ~3-5 天）

焊接元件（我们做，~15min/板）
  → R1-R4 (10kΩ 0805) × 4
  → C1-C4 (10nF 0805) × 4
  → U1A + U1B (1×22 排母) × 2
  → J1-J5 (XH2.54 母座) × 5

预压 JST 线缆（5 根）
  → EC11 5P × 2 / BTN 2P × 1 / NFC 8P × 1 / OTG dongle 4P × 1

质检
  → 万用表通断（5V/3V3/GND 到 J5/J4/U1 各 pin）
  → 插入 DevKitC，UART USB-C 烧固件，逐一测试各端口
  → 旋钮转动测试（验证 RC 去抖效果，每格一个事件）

打包
  → PCB + DevKitC + dongle + 线缆 + 螺丝 = 1 套电子件
```

---

## 工具需求

| 工具 | 用途 |
|------|------|
| KiCad 10+ | 原理图 + PCB layout |
| circuit-synth + Freerouting | AI 驱动的设计 + 自动布线（见 `~/.claude/skills/pcb`）|
| JLCPCB | 打板下单 |
| 万用表 | 通断测试 |
| JST-XH 压线钳 | 预压端子线缆 |
| 烙铁 + 助焊剂 + 加热台 | 焊接 0805 + 直插件 |

---

## 设计追溯

- 完整设计计划 + 风险评估：`~/.claude/plans/iridescent-snuggling-planet.md`
- DevKitC 物理引脚分布权威表：`/CLAUDE.md` + `pcb/asset/ESP32-S3-DevKitC-N16R8.png`
- OTG dongle 集成方案：`docs/hardware/otg-adapter.md`
- NFC 模块接口：`docs/hardware/nfc.md`
- 飞线万能板实证：`pcb/asset/飞线测试版本-顶视图.JPG` + `飞线测试版本-飞线图.JPG`

---

## 历史归档

v1.0（2026-04-01 出稿，对应 V4 启动期）已被本 v2.0 取代。v1.0 的主要差异：
- 板尺寸 80×50mm → 100×100mm
- 连接器 4 路 → 5 路（新增 J5 OTG USB）
- 包含 USB-C 母座 J5/J6 → 移除（OTG dongle 接管充电）
- 包含 SS34 防倒灌 + 4× 5.1k CC 下拉 → 全移除
- 包含 LED 4P 顶部模块连接器 → 移除（用 DevKitC GPIO48 板载 RGB）
- GPIO 编号是 V3 残留（顺序 1-8）→ 更新为 V4 终版（与固件实测一致）
- 单排母 vs 双排母未定 → **确定两条 1×22 单排母**
- 旋钮稳定性未涉及 → **新增 10kΩ + 10nF RC 去抖网络**

如需查阅 v1.0 内容，请 `git log -- docs/project/CosmoRadio-V4-PCB-Spec.md`。
