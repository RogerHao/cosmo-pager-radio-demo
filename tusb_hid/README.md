# Cosmo Pager Radio - USB HID 固件

基于 TinyUSB 的 USB HID 键盘实现，用于 Cosmo Pager Radio 项目。

## 概述

本固件将 XIAO ESP32S3 作为 USB HID 键盘设备，将物理输入（旋钮、按钮）转换为键盘按键事件。相比 BLE HID 方案，USB 方案具有更低延迟和更稳定的连接。

## 特性

- **USB HID 键盘**: 即插即用，无需配对
- **输入处理**: GPIO 中断驱动，支持两个旋转编码器和一个按钮
- **LED 指示**: WS2812 RGB LED 状态反馈
- **强制重启**: 长按按钮 15 秒触发设备重启

## 输入映射

| 输入 | HID 按键 | GPIO |
|------|----------|------|
| 按钮按下 | Enter (按下) | GPIO1 (D0) |
| 按钮释放 | Enter (释放) | GPIO1 (D0) |
| 旋钮1 顺时针 | ↑ 上箭头 | GPIO2/3 (D1/D2) |
| 旋钮1 逆时针 | ↓ 下箭头 | GPIO2/3 (D1/D2) |
| 旋钮2 顺时针 | → 右箭头 | GPIO4/5 (D3/D4) |
| 旋钮2 逆时针 | ← 左箭头 | GPIO4/5 (D3/D4) |

## LED 行为

| 事件 | 颜色 |
|------|------|
| 启动完成 | 绿色闪烁 |
| USB 连接 | 蓝色闪烁 |
| 按钮按下 | 红色常亮 |
| 按钮释放 | 熄灭 |

## 构建与烧录

```bash
# 激活 ESP-IDF 环境
get_idf

# 设置目标芯片（首次）
idf.py set-target esp32s3

# 构建
idf.py build

# 烧录并监控
idf.py -p /dev/cu.usbmodem* flash monitor
```

## 串口输出示例

```
I (xxx) USB_HID: Cosmo Pager Radio - USB HID Keyboard
I (xxx) USB_HID: USB initialization DONE
I (xxx) LED: LED indicator initialized on GPIO6
I (xxx) INPUT: Input handler initialized (GPIO interrupts)
I (xxx) INPUT:   Button: GPIO1, ENC1: GPIO2/3, ENC2: GPIO4/5
I (xxx) USB_HID: USB connected
I (xxx) USB_HID: BTN -> ENTER (pressed)
I (xxx) USB_HID: BTN -> ENTER (released)
I (xxx) USB_HID: ENC1 CW -> UP
I (xxx) USB_HID: ENC2 CCW -> LEFT
```

## USB 描述符

- **制造商**: Cosmo
- **产品名**: Pager Radio Input
- **设备类型**: HID 键盘

## 硬件要求

- Seeed Studio XIAO ESP32S3
- EC11 旋转编码器 x2
- 微动开关 x1
- WS2812 RGB LED x1

## 与 BLE HID 的对比

| 方面 | BLE HID | USB HID |
|------|---------|---------|
| 连接方式 | 蓝牙配对 | 即插即用 |
| 延迟 | 7-20ms | 1-10ms |
| 稳定性 | 易受干扰 | 稳定可靠 |
| 供电 | 电池 | USB 供电 |
| 适用场景 | 无线需求 | 固定安装 |

## 文件结构

```
tusb_hid/
├── main/
│   ├── tusb_hid_example_main.c    # 主程序
│   ├── input_handler.c/h          # 输入处理模块
│   ├── led_indicator.c/h          # LED 控制模块
│   ├── CMakeLists.txt
│   └── idf_component.yml
├── sdkconfig.defaults
├── CMakeLists.txt
└── README.md                      # 本文档
```
