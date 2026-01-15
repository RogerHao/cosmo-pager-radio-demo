# Cosmo Pager Radio - ESP32 BLE HID Firmware

基于 ESP-IDF 的 BLE HID 键盘固件，用于 Cosmo Pager Radio 项目。

## 硬件要求

| 组件 | 规格 | 连接 |
|------|------|------|
| XIAO ESP32S3 | Seeed Studio | 主控 |
| EC11 旋转编码器 x2 | 增量式编码器 | D1/D2, D3/D4 |
| 按钮 x1 | 常开按钮 | D0 |

## GPIO 引脚映射

| 功能 | GPIO | XIAO 引脚 | HID 按键 |
|------|------|----------|----------|
| 按钮 | 1 | D0 | Enter |
| 编码器1 CLK | 2 | D1 | Up |
| 编码器1 DT | 3 | D2 | Down |
| 编码器2 CLK | 4 | D3 | Right |
| 编码器2 DT | 5 | D4 | Left |

所有输入 GPIO 使用内部上拉电阻，低电平有效（接 GND 触发）。

## 电源接线

XIAO ESP32S3 背面有电池焊盘，支持 3.7V 锂电池直接供电：

- **B+**: 电池正极（远离 USB 口）
- **B-**: 电池负极（靠近 USB 口）

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

退出监控：`Ctrl+]`

## 配置说明

配置文件：
- `sdkconfig.defaults` - 通用配置
- `sdkconfig.defaults.esp32s3` - ESP32-S3 特定配置

关键配置项：
| 配置 | 值 | 说明 |
|------|-----|------|
| `CONFIG_BT_NIMBLE_ENABLED` | y | 使用 NimBLE 协议栈 |
| `CONFIG_EXAMPLE_KBD_ENABLE` | y | HID 键盘模式 |
| `CONFIG_ESPTOOLPY_FLASHSIZE_8MB` | y | 8MB Flash |

## 预期输出

```
I (367) HID_DEV_DEMO: setting hid gap, mode:2
I (457) HID_DEV_DEMO: GPIO input task started
I (457) HID_DEV_DEMO: GPIO input initialized: BTN=1, ENC1=2/3, ENC2=4/5
I (457) HID_DEV_BLE: START
```

按下按钮或转动旋钮时：
```
I (xxxxx) HID_DEV_DEMO: BTN -> ENTER
I (xxxxx) HID_DEV_DEMO: ENC1 CW -> UP
I (xxxxx) HID_DEV_DEMO: ENC2 CCW -> LEFT
```

## 蓝牙配对

设备名称：`cosmo-radio-input`

配对方式：Just Works（无需 PIN 码）

## 故障排除

1. **看不到 GPIO 日志**：确认 `mode:2`（键盘模式），如果是 `mode:1` 说明配置错误
2. **按钮无反应**：检查接线是否正确（按钮一端接 D0，另一端接 GND）
3. **无法烧录**：按住 BOOT 按钮再插入 USB 进入下载模式
