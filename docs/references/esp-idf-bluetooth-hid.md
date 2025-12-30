# ESP-IDF 蓝牙 HID 参考

## 概述

本项目需要将 ESP32 作为蓝牙 HID 设备（键盘），连接到 E5 Ultra 的 Android 系统。ESP-IDF 提供了完整的蓝牙 HID API 支持。

## 蓝牙协议选择

ESP-IDF 支持两种蓝牙协议栈：

| 协议栈 | 特点 | 适用场景 |
|--------|------|----------|
| **Bluedroid** | 支持 Classic BT + BLE，功能完整 | 需要兼容传统蓝牙设备 |
| **NimBLE** | 仅 BLE，轻量级，内存占用小 | 资源受限或仅需 BLE |

**建议**：优先尝试 BLE HID（NimBLE），如果 Android 兼容性有问题，再切换到 Classic BT（Bluedroid）。

## ESP-IDF 官方示例

### BLE HID 设备
```
esp-idf/examples/bluetooth/esp_hid_device
```
- 支持 Classic BT 和 BLE 双模
- 可模拟鼠标或遥控器
- 根据用户设置切换模式

### Classic BT HID 鼠标
```
esp-idf/examples/bluetooth/bluedroid/classic_bt/bt_hid_mouse_device
```
- 演示如何实现 Classic BT HID 设备
- 周期性发送 HID 报告

## 关键 API

### HID Device API

头文件：
```c
#include "esp_hidd_api.h"
```

主要函数：
- `esp_hidd_dev_init()` - 初始化 HID 设备
- `esp_hidd_dev_input_set()` - 发送 HID 输入报告
- `esp_hidd_dev_event_handler_register()` - 注册事件回调

### HID 报告描述符

键盘需要定义正确的 HID 报告描述符，包含：
- 键盘按键报告
- 修饰键状态
- LED 状态（可选）

## 开源参考项目

### 1. NimBLE Keyboard/Mouse Example
- 仓库：[olegos76/nimble_kbdhid_example](https://github.com/olegos76/nimble_kbdhid_example)
- 特点：
  - 基于 NimBLE 协议栈
  - 支持键盘和鼠标
  - GPIO 按钮触发输入
  - 代码简洁，适合参考

### 2. ESP32 Mouse Keyboard
- 仓库：[asterics/esp32_mouse_keyboard](https://github.com/asterics/esp32_mouse_keyboard)
- 特点：
  - HID over GATT 实现
  - 串口 API 控制
  - 兼容 Adafruit EZKey HID

## 本项目实现要点

### 输入映射

| 输入 | HID 键码 |
|------|----------|
| EC11 #1 顺时针 | Up Arrow (0x52) |
| EC11 #1 逆时针 | Down Arrow (0x51) |
| EC11 #2 顺时针 | Right Arrow (0x4F) |
| EC11 #2 逆时针 | Left Arrow (0x50) |
| 顶部按钮 | Enter (0x28) |

### EC11 编码器处理

EC11 旋转编码器输出 A/B 两相信号，通过检测相位关系判断旋转方向：
- A 相上升沿时 B 相为低：顺时针
- A 相上升沿时 B 相为高：逆时针

可使用 ESP-IDF 的 GPIO 中断或 PCNT（脉冲计数器）外设处理。

## 官方文档

- [ESP-IDF HID Device API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/bluetooth/esp_hidd.html)
- [ESP-IDF HID Host API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/bluetooth/esp_hidh.html)
- [ESP-IDF Bluetooth API 总览](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/bluetooth/index.html)
- [NimBLE 移植指南](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/bluetooth/nimble/index.html)
