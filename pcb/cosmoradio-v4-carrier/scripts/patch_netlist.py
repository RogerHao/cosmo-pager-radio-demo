#!/usr/bin/env python3
"""
patch_netlist.py — 彻底重建 .net 的 (nets ... ) 块。

circuit-synth v0.12.1 在多节点 net 上行为不稳定（gotcha #19 + 变体）：
- 2-node 简单连接：正确（J→U 直连）
- ≥3-node 多节点 net：沉默失败 OR 合并到错误的 "3V3"/"GND" 大袋子
- 还会留下 "unconnected-(REF-PadN)" 占位 net 干扰

本脚本策略：保留 .net 的 (components ... ) 块（footprint/UUID 等元数据），
**彻底删除 (nets ... ) 块**，按 Python ground truth 重新生成所有 net。

Run:
    python3 scripts/patch_netlist.py
"""
import re
from pathlib import Path

NET_FILE = Path(__file__).parent.parent / "CosmoradioV4Carrier" / "CosmoradioV4Carrier.net"

# Ground truth：所有电气连接（17 个有效 net + 未连接 pin 留作 NC）
# 2026-05-18 v2 修正:
#   - U1A pin 2 改为 GND (实测 DevKitC user-LEFT 顶部连续两个都是 GND, 5V 只在 U1B pin 2)
#   - J1/J2 改为实物 EC11 端子顺序 SW-GND-A-GND-B
NETS = [
    # ---- 2-node 信号 ----
    ("/BTN",       [("J3", "1"), ("U1A1", "19")]),
    ("/ENC1_SW",   [("J1", "1"), ("U1A1", "15")]),     # J1 pin 1 = SW
    ("/ENC2_SW",   [("J2", "1"), ("U1B1", "11")]),     # J2 pin 1 = SW
    ("/NFC_CS",    [("J4", "1"), ("U1B1", "14")]),
    ("/NFC_SCK",   [("J4", "2"), ("U1B1", "15")]),
    ("/NFC_MOSI",  [("J4", "3"), ("U1B1", "16")]),
    ("/NFC_MISO",  [("J4", "4"), ("U1B1", "17")]),
    ("/NFC_IRQ",   [("J4", "5"), ("U1B1", "18")]),
    ("/NFC_RST",   [("J4", "7"), ("U1B1", "19")]),
    ("/USB_DM",    [("J5", "2"), ("U1A1", "3")]),
    ("/USB_DP",    [("J5", "3"), ("U1A1", "4")]),
    # ---- 4-node EC11 A/B (J pin 3=A, J pin 5=B + U + R + C) ----
    ("/ENC1_A",    [("J1", "3"), ("U1A1", "17"), ("R1", "1"), ("C1", "1")]),
    ("/ENC1_B",    [("J1", "5"), ("U1A1", "16"), ("R2", "1"), ("C2", "1")]),
    ("/ENC2_A",    [("J2", "3"), ("U1B1", "13"), ("R3", "1"), ("C3", "1")]),
    ("/ENC2_B",    [("J2", "5"), ("U1B1", "12"), ("R4", "1"), ("C4", "1")]),
    # ---- 电源 net ----
    ("/5V",        [("U1B1", "2"), ("J5", "1")]),       # U1A pin 2 不接 5V 了!
    ("/3V3",       [("R1", "2"), ("R2", "2"), ("R3", "2"), ("R4", "2"),
                    ("J4", "8"), ("U1B1", "21"), ("U1B1", "22")]),
    # ---- GND: J1/J2 pin 2+pin 4 现在是 GND (EC11 SW-GND-A-GND-B), U1A pin 2 加入 ----
    ("/GND",       [("U1A1", "1"), ("U1A1", "2"), ("U1A1", "22"), ("U1B1", "1"),
                    ("J1", "2"), ("J1", "4"), ("J2", "2"), ("J2", "4"),
                    ("J3", "2"), ("J4", "6"), ("J5", "4"),
                    ("C1", "2"), ("C2", "2"), ("C3", "2"), ("C4", "2")]),
]

# 所有出现在 NETS 里的 pin（用于判定哪些 pin 是"已连接"）
CONNECTED_PINS = set()
for _, nodes in NETS:
    for ref, pin in nodes:
        CONNECTED_PINS.add((ref, pin))

# 全部组件的 pin 数（用于补 unconnected）
ALL_PINS = {
    "U1A1": 22, "U1B1": 22,
    "J1": 5, "J2": 5, "J3": 2, "J4": 8, "J5": 4,
    "R1": 2, "R2": 2, "R3": 2, "R4": 2,
    "C1": 2, "C2": 2, "C3": 2, "C4": 2,
}


def render_net(code: int, name: str, nodes: list) -> str:
    parts = [f'\t\t(net\n\t\t\t(code "{code}")\n\t\t\t(name "{name}")\n\t\t\t(class "Default")']
    for ref, pin in nodes:
        parts.append(
            f'\t\t\t(node\n\t\t\t\t(ref "{ref}")\n\t\t\t\t(pin "{pin}")\n\t\t\t\t(pintype "passive")\n\t\t\t)'
        )
    parts.append('\t\t)')
    return "\n".join(parts)


def main():
    text = NET_FILE.read_text()

    # 找到 (nets ... ) 段，整个删除
    # 用括号深度跟踪精确定位
    nets_start = text.find("\t(nets")
    if nets_start < 0:
        raise SystemExit("找不到 (nets 段")

    depth = 0
    i = nets_start
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                nets_end = i + 1
                break
        i += 1
    else:
        raise SystemExit("找不到 (nets 段的结尾")

    # 生成新的 (nets ... ) 块
    new_blocks = ["\t(nets"]
    next_code = 1
    for name, nodes in NETS:
        new_blocks.append(render_net(next_code, name, nodes))
        next_code += 1

    # 加上 unconnected pin（每个 1-node 一个 net）
    unconnected_count = 0
    for ref, pin_count in sorted(ALL_PINS.items()):
        for p in range(1, pin_count + 1):
            if (ref, str(p)) not in CONNECTED_PINS:
                uc_name = f"unconnected-({ref}-Pad{p})"
                new_blocks.append(
                    render_net(next_code, uc_name, [(ref, str(p))])
                )
                next_code += 1
                unconnected_count += 1

    new_blocks.append("\t)")
    new_nets_section = "\n".join(new_blocks)

    new_text = text[:nets_start] + new_nets_section + text[nets_end:]
    NET_FILE.write_text(new_text)

    print(f"✅ 重建 .net 的 (nets ...) 块")
    print(f"   - {len(NETS)} 个有效 net (3 power + 14 signal)")
    print(f"   - {unconnected_count} 个 unconnected pin (NC)")
    print(f"   - 总 net code 数: {next_code - 1}")


if __name__ == "__main__":
    main()
