"""
CosmoradioV4Carrier — circuit-synth source

CosmoRadio V4 PCB 载板（Plan v2，2026-05-18）。
ESP32-S3 DevKitC N16R8 通过两条 1×22 单排母插入，5 路 XH2.54 连接器即插即用。
EC11 A/B 信号各加 10kΩ 上拉 + 10nF 对 GND RC 去抖（τ=100µs）。

Run with circuit-synth's bundled Python:
    /Users/dehonghao/.local/share/uv/tools/circuit-synth/bin/python3 src/circuit.py

Outputs:
    CosmoradioV4Carrier/CosmoradioV4Carrier.kicad_sch    schematic with real symbols
    CosmoradioV4Carrier/CosmoradioV4Carrier.kicad_pro    project file
    CosmoradioV4Carrier/CosmoradioV4Carrier.pdf          rendered schematic PDF
    CosmoradioV4Carrier/CosmoradioV4Carrier.csv          BOM

Then extract netlist:
    kicad-cli sch export netlist --format kicadsexpr \\
        --output CosmoradioV4Carrier/CosmoradioV4Carrier.net \\
        CosmoradioV4Carrier/CosmoradioV4Carrier.kicad_sch

Critical rules (see ~/.claude/skills/pcb/SKILL.md):
- ALWAYS set both `value` AND `footprint` on every Component (else 422 error)
- Wipe stale output before re-running: `rm -rf CosmoradioV4Carrier/`
- Don't use circuit-synth's PCB generator (paywalled). Hand-build via pcbnew API.

DevKitC 物理引脚分布权威表见 /CLAUDE.md "GPIO Pin Assignments"。
U1A/U1B 引脚顺序按 PCB 物理位置（pin 1 = 顶部 = 近 USB-C 端）。
"""

from circuit_synth import Component, Net, circuit


@circuit(name="CosmoradioV4Carrier")
def cosmoradio_v4_carrier():
    # ====================================================================
    # COMPONENTS
    # ====================================================================

    # ----- U1A: DevKitC 左列插座 (PCB 左侧, 1×22 排母) -----
    # 物理映射 (pin 1 = 顶部 = 近 USB-C 端，pin 22 = 底部 = 远端):
    #  1=GND, 2=GND (! 不是 5V — 实测 user-LEFT 顶部两个都是 GND, 5V 在 U1B pin2)
    #  3=GPIO19(USB D-), 4=GPIO20(USB D+), 5=GPIO21, 6=GPIO47,
    #  7=GPIO48, 8=GPIO45, 9=GPIO0, 10=GPIO35, 11=GPIO36, 12=GPIO37,
    #  13=GPIO38, 14=GPIO39, 15=GPIO40(ENC1 SW), 16=GPIO41(ENC1 B),
    #  17=GPIO42(ENC1 A), 18=GPIO2, 19=GPIO1(BTN), 20=GPIO44(RX0),
    #  21=GPIO43(TX0), 22=GND
    u1a = Component(
        symbol="Connector_Generic:Conn_01x22",
        ref="U1A1",
        value="DevKitC-Left-Socket",
        footprint="Connector_PinSocket_2.54mm:PinSocket_1x22_P2.54mm_Vertical",
    )

    # ----- U1B: DevKitC 右列插座 (PCB 右侧, 1×22 排母) -----
    # 物理映射:
    #  1=GND, 2=5V, 3=GPIO14, 4=GPIO13, 5=GPIO12, 6=GPIO11, 7=GPIO10, 8=GPIO9,
    #  9=GPIO46, 10=GPIO3, 11=GPIO8(ENC2 SW), 12=GPIO18(ENC2 B), 13=GPIO17(ENC2 A),
    #  14=GPIO16(NFC CS), 15=GPIO15(NFC SCK), 16=GPIO7(NFC MOSI),
    #  17=GPIO6(NFC MISO), 18=GPIO5(NFC IRQ), 19=GPIO4(NFC RST), 20=RST(CHIP_PU),
    #  21=3V3, 22=3V3
    u1b = Component(
        symbol="Connector_Generic:Conn_01x22",
        ref="U1B1",
        value="DevKitC-Right-Socket",
        footprint="Connector_PinSocket_2.54mm:PinSocket_1x22_P2.54mm_Vertical",
    )

    # ----- J1: EC11-L (用户左旋钮) 5P XH2.54, PCB 左侧中段 -----
    # 端子线序 (实物 EC11 顺序): pin 1=SW(GPIO40), 2=GND, 3=A(GPIO42), 4=GND, 5=B(GPIO41)
    j1 = Component(
        symbol="Connector_Generic:Conn_01x05",
        ref="J1",
        value="EC11-L-5P",
        footprint="Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical",
    )

    # ----- J2: EC11-R (用户右旋钮) 5P XH2.54, PCB 右侧中段 -----
    # 端子线序 (实物 EC11 顺序): pin 1=SW(GPIO8), 2=GND, 3=A(GPIO17), 4=GND, 5=B(GPIO18)
    j2 = Component(
        symbol="Connector_Generic:Conn_01x05",
        ref="J2",
        value="EC11-R-5P",
        footprint="Connector_JST:JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical",
    )

    # ----- J3: Action Button 2P XH2.54, PCB 左侧靠前 -----
    # pin: 1=SIG(GPIO1), 2=GND
    j3 = Component(
        symbol="Connector_Generic:Conn_01x02",
        ref="J3",
        value="BTN-2P",
        footprint="Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical",
    )

    # ----- J4: RC522 NFC 8P XH2.54, PCB 右侧 -----
    # pin: 1=CS(16), 2=SCK(15), 3=MOSI(7), 4=MISO(6), 5=IRQ(5), 6=GND,
    #      7=RST(4), 8=3V3
    j4 = Component(
        symbol="Connector_Generic:Conn_01x08",
        ref="J4",
        value="NFC-8P",
        footprint="Connector_JST:JST_XH_B8B-XH-A_1x08_P2.50mm_Vertical",
    )

    # ----- J5: OTG dongle USB 数据 4P XH2.54, PCB 左侧靠后 -----
    # pin: 1=VBUS(5V), 2=D-(GPIO19), 3=D+(GPIO20), 4=GND
    j5 = Component(
        symbol="Connector_Generic:Conn_01x04",
        ref="J5",
        value="USB-DONGLE-4P",
        footprint="Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
    )

    # ----- R1-R4: 10kΩ 0805, EC11 A/B 上拉到 3V3 -----
    r1 = Component(
        symbol="Device:R", ref="R1", value="10k",
        footprint="Resistor_SMD:R_0805_2012Metric",
    )  # ENC1_A pull-up
    r2 = Component(
        symbol="Device:R", ref="R2", value="10k",
        footprint="Resistor_SMD:R_0805_2012Metric",
    )  # ENC1_B pull-up
    r3 = Component(
        symbol="Device:R", ref="R3", value="10k",
        footprint="Resistor_SMD:R_0805_2012Metric",
    )  # ENC2_A pull-up
    r4 = Component(
        symbol="Device:R", ref="R4", value="10k",
        footprint="Resistor_SMD:R_0805_2012Metric",
    )  # ENC2_B pull-up

    # ----- C1-C4: 10nF 0805, EC11 A/B 对 GND RC 去抖 (τ=100µs) -----
    c1 = Component(
        symbol="Device:C", ref="C1", value="10nF",
        footprint="Capacitor_SMD:C_0805_2012Metric",
    )  # ENC1_A debounce
    c2 = Component(
        symbol="Device:C", ref="C2", value="10nF",
        footprint="Capacitor_SMD:C_0805_2012Metric",
    )  # ENC1_B debounce
    c3 = Component(
        symbol="Device:C", ref="C3", value="10nF",
        footprint="Capacitor_SMD:C_0805_2012Metric",
    )  # ENC2_A debounce
    c4 = Component(
        symbol="Device:C", ref="C4", value="10nF",
        footprint="Capacitor_SMD:C_0805_2012Metric",
    )  # ENC2_B debounce

    # ====================================================================
    # NETS
    # ====================================================================
    # Power
    p5v = Net("5V")
    p3v3 = Net("3V3")
    gnd = Net("GND")

    # EC11-L 信号 (用户左旋钮)
    enc1_a = Net("ENC1_A")    # GPIO42
    enc1_b = Net("ENC1_B")    # GPIO41
    enc1_sw = Net("ENC1_SW")  # GPIO40

    # EC11-R 信号 (用户右旋钮)
    enc2_a = Net("ENC2_A")    # GPIO17
    enc2_b = Net("ENC2_B")    # GPIO18
    enc2_sw = Net("ENC2_SW")  # GPIO8

    # Action Button
    btn = Net("BTN")          # GPIO1

    # NFC SPI + control
    nfc_cs = Net("NFC_CS")      # GPIO16
    nfc_sck = Net("NFC_SCK")    # GPIO15
    nfc_mosi = Net("NFC_MOSI")  # GPIO7
    nfc_miso = Net("NFC_MISO")  # GPIO6
    nfc_irq = Net("NFC_IRQ")    # GPIO5
    nfc_rst = Net("NFC_RST")    # GPIO4

    # USB OTG (走 J5 到 dongle)
    usb_dm = Net("USB_DM")    # GPIO19
    usb_dp = Net("USB_DP")    # GPIO20

    # ====================================================================
    # CONNECTIONS — U1A (DevKitC 左列插座)
    # ====================================================================
    u1a[1] += gnd         # GND (pin 1)
    u1a[2] += gnd         # GND (pin 2 — 不是 5V! 实测 user-LEFT 顶部连续两个 GND)
    u1a[3] += usb_dm      # GPIO19 (USB D-)
    u1a[4] += usb_dp      # GPIO20 (USB D+)
    # u1a[5-14]: GPIO 21/47/48/45/0/35-39 — 未使用,不接 net
    u1a[15] += enc1_sw    # GPIO40 (ENC1 SW)
    u1a[16] += enc1_b     # GPIO41 (ENC1 B)
    u1a[17] += enc1_a     # GPIO42 (ENC1 A)
    # u1a[18]: GPIO2 — 未使用
    u1a[19] += btn        # GPIO1 (BTN SIG)
    # u1a[20-21]: GPIO44/43 (UART0) — 不接,留给烧录调试
    u1a[22] += gnd        # GND

    # ====================================================================
    # CONNECTIONS — U1B (DevKitC 右列插座)
    # ====================================================================
    u1b[1] += gnd         # GND
    u1b[2] += p5v         # 5V — 主供电（U1A pin 2 是 GND，5V 只在这里）
    # u1b[3-10]: GPIO 14/13/12/11/10/9/46/3 — 未使用
    u1b[11] += enc2_sw    # GPIO8 (ENC2 SW)
    u1b[12] += enc2_b     # GPIO18 (ENC2 B)
    u1b[13] += enc2_a     # GPIO17 (ENC2 A)
    u1b[14] += nfc_cs     # GPIO16 (NFC CS)
    u1b[15] += nfc_sck    # GPIO15 (NFC SCK)
    u1b[16] += nfc_mosi   # GPIO7 (NFC MOSI)
    u1b[17] += nfc_miso   # GPIO6 (NFC MISO)
    u1b[18] += nfc_irq    # GPIO5 (NFC IRQ)
    u1b[19] += nfc_rst    # GPIO4 (NFC RST)
    # u1b[20]: RST (CHIP_PU/EN) — 不接,DevKitC 自有 RST 按钮
    u1b[21] += p3v3       # 3V3
    u1b[22] += p3v3       # 3V3 (双 3V3 pin 并联,降阻)

    # ====================================================================
    # CONNECTIONS — J1 (EC11-L 5P) + R1/R2 + C1/C2
    # 实物 EC11 端子顺序: SW-GND-A-GND-B
    # ====================================================================
    j1[1] += enc1_sw      # SW
    j1[2] += gnd          # GND
    j1[3] += enc1_a       # A
    j1[4] += gnd          # GND
    j1[5] += enc1_b       # B

    # R1: ENC1_A 上拉到 3V3
    r1[1] += enc1_a
    r1[2] += p3v3
    # R2: ENC1_B 上拉到 3V3
    r2[1] += enc1_b
    r2[2] += p3v3
    # C1: ENC1_A 对 GND
    c1[1] += enc1_a
    c1[2] += gnd
    # C2: ENC1_B 对 GND
    c2[1] += enc1_b
    c2[2] += gnd

    # ====================================================================
    # CONNECTIONS — J2 (EC11-R 5P) + R3/R4 + C3/C4
    # 实物 EC11 端子顺序: SW-GND-A-GND-B
    # ====================================================================
    j2[1] += enc2_sw
    j2[2] += gnd
    j2[3] += enc2_a
    j2[4] += gnd
    j2[5] += enc2_b

    # R3: ENC2_A 上拉到 3V3
    r3[1] += enc2_a
    r3[2] += p3v3
    # R4: ENC2_B 上拉到 3V3
    r4[1] += enc2_b
    r4[2] += p3v3
    # C3: ENC2_A 对 GND
    c3[1] += enc2_a
    c3[2] += gnd
    # C4: ENC2_B 对 GND
    c4[1] += enc2_b
    c4[2] += gnd

    # ====================================================================
    # CONNECTIONS — J3 (Action Button 2P)
    # ====================================================================
    j3[1] += btn          # SIG (GPIO1)
    j3[2] += gnd          # GND

    # ====================================================================
    # CONNECTIONS — J4 (NFC 8P, 顺序与 RC522 mini 模块 1:1)
    # ====================================================================
    j4[1] += nfc_cs       # CS  (GPIO16)
    j4[2] += nfc_sck      # SCK (GPIO15)
    j4[3] += nfc_mosi     # MOSI(GPIO7)
    j4[4] += nfc_miso     # MISO(GPIO6)
    j4[5] += nfc_irq      # IRQ (GPIO5, 固件未用但接线预留)
    j4[6] += gnd          # GND
    j4[7] += nfc_rst      # RST (GPIO4)
    j4[8] += p3v3         # 3V3

    # ====================================================================
    # CONNECTIONS — J5 (OTG dongle USB 数据 4P, 与 USB-A 物理顺序一致)
    # ====================================================================
    j5[1] += p5v          # VBUS
    j5[2] += usb_dm       # D- (GPIO19)
    j5[3] += usb_dp       # D+ (GPIO20)
    j5[4] += gnd          # GND


if __name__ == "__main__":
    c = cosmoradio_v4_carrier()
    # generate_pcb=False: circuit-synth open source 不含 PCB 引擎;
    # PCB layout 由 scripts/build_pcb.py 用 pcbnew API 手工搭建
    c.generate_kicad_project(
        project_name="CosmoradioV4Carrier",
        placement_algorithm="hierarchical",
        generate_pcb=False,
    )
    c.generate_pdf_schematic(project_name="CosmoradioV4Carrier")
    c.generate_bom(project_name="CosmoradioV4Carrier")
    print("✅ schematic + PDF + BOM generated")
    print("Next: extract netlist via kicad-cli, then run scripts/build_pcb.py")
