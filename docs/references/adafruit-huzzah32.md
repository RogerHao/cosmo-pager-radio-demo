# Adafruit HUZZAH32 - ESP32 Feather 参考

## 概述

Adafruit HUZZAH32 是基于 ESP32 的 Feather 开发板，集成了 USB 转串口、锂电池充电管理和完整的 GPIO 引出。本项目使用它作为蓝牙 HID 控制器。

## 核心规格

| 参数 | 规格 |
|------|------|
| 芯片 | ESP32 WROOM32 模块 |
| CPU | 240MHz 双核 Tensilica LX6 |
| Flash | 4MB SPI Flash |
| 无线 | WiFi 802.11 b/g/n + 蓝牙 4.2 (Classic + BLE) |
| 工作电压 | 3.3V |
| 输入电压 | USB 5V 或 BAT 3.7V |

## 关键引脚

### 电源引脚

| 引脚 | 说明 |
|------|------|
| **BAT** | 锂电池正极输入/输出（3.5V - 4.2V） |
| **USB** | USB 5V 输入 |
| **3V** | 3.3V 稳压输出（可用容量约 250mA） |
| **GND** | 公共地 |
| **EN** | 3.3V 稳压器使能（拉低可关闭稳压器） |

### GPIO 引脚

可用于输入的引脚：
- 模拟输入：A0-A5, A9, A10, A12, A13
- 通用 GPIO：4, 12, 13, 14, 15, 21, 25, 26, 27, 32, 33, 34, 35, 36, 39

**注意**：
- 引脚 34, 36, 39 只能作为输入，不能作为输出
- 引脚 12 有内置下拉电阻
- 所有 GPIO 为 3.3V 逻辑，不支持 5V

## 本项目使用

### 供电方案
- 从 E5 Ultra 主板取电（3.5~3.7V）
- 接入 HUZZAH32 的 **BAT** 引脚
- 共地连接

### 输入设备连接
（具体引脚分配待固件开发时确定）

| 设备 | 接口类型 | 预估引脚需求 |
|------|----------|--------------|
| EC11 #1 | 旋转编码器 A/B 相 | 2 个 GPIO |
| EC11 #2 | 旋转编码器 A/B 相 | 2 个 GPIO |
| 顶部按钮 | 微动开关 | 1 个 GPIO |

总计需要 5 个 GPIO 引脚，HUZZAH32 完全满足需求。

## 开发环境

本项目使用 **ESP-IDF** 进行固件开发（非 Arduino）。

ESP-IDF 安装：
```bash
# macOS
get_idf  # 如已配置 ESP-IDF 环境别名
```

## 官方资源

- [产品页面](https://www.adafruit.com/product/3405)
- [引脚定义文档](https://learn.adafruit.com/adafruit-huzzah32-esp32-feather/pinouts)
- [完整学习指南](https://learn.adafruit.com/adafruit-huzzah32-esp32-feather/overview)
- [完整文档 PDF](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-huzzah32-esp32-feather.pdf)
- [PCB 设计文件 (GitHub)](https://github.com/adafruit/Adafruit-HUZZAH32-ESP32-Feather-PCB)
