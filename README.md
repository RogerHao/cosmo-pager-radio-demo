# Cosmo Pager Radio

可穿梭于平行宇宙的 Radio 接收器

## 项目简介

本项目是一个硬件改装项目，将安卓平板改造为具有复古 Radio 外观的桌面交互设备。设备造型参考 iMac G3 的斜面站立式设计，通过 3D 打印外壳和自定义输入系统，打造独特的交互体验。

用户可以通过旋转旋钮来调节频率、切换模式，仿佛在不同的平行宇宙间搜索信号。

## 产品形态

![外壳设计稿](docs/E5Ultra/design-draft.png)

- **外观风格**: iMac G3 斜面站立式
- **显示设计**: 三圆形遮罩（一个矩形屏幕通过开孔分割为三个圆形显示区）
  - 中间大圆：主显示区
  - 左侧小圆：模式指示
  - 右侧小圆：频率指示
- **输入方式**: 两个 EC11 旋钮 + 顶部条状按钮
- **状态指示**: WS2812 RGB LED

## 硬件组成

| 组件 | 规格 | 用途 |
|------|------|------|
| 安卓平板 | 任意支持 BLE/USB HID 的安卓设备 | 主机，运行 Web 应用 |
| XIAO ESP32S3 | ESP32-S3/BLE 5.0/USB OTG/8MB Flash | HID 控制器 |
| EC11 旋钮 x2 | 旋转编码器 | 频率调节/模式切换 |
| 微动开关 x1 | 顶部条状按钮 | 确认操作 |
| WS2812 LED x1 | RGB LED | 状态指示 |

## 连接方案

项目支持两种 HID 连接方案：

| 方案 | 固件目录 | 连接方式 | 特点 |
|------|----------|----------|------|
| BLE HID | `firmware/` | 蓝牙无线 | 无需线缆，电池供电 |
| USB HID | `tusb_hid/` | USB 有线 | 更稳定，延迟更低，即插即用 |

## 交互设计

输入设备通过 ESP32 HID 协议（蓝牙或 USB）连接到安卓系统，模拟键盘按键：

| 输入 | 映射 | 功能 |
|------|------|------|
| 顶部按钮 | Enter 键 | 确认选择 |
| EC11 #1 旋转 | 上/下方向键 | 调节频率 |
| EC11 #2 旋转 | 左/右方向键 | 切换模式 |

### LED 状态指示

| 事件 | LED 颜色 |
|------|----------|
| 按钮按下 | 红色 |
| 按钮释放 | 熄灭 |
| 连接成功 | 蓝色闪烁 |
| 启动完成 | 绿色闪烁 |

## 项目结构

```
cosmo-pager-radio-demo/
├── README.md                           # 本文档
├── CLAUDE.md                           # Claude Code 开发指南
├── docs/
│   ├── design/
│   │   └── hardware-architecture.md    # 硬件架构设计
│   ├── E5Ultra/                        # E5 Ultra 设备资料
│   └── references/                     # 参考资料
├── firmware/                           # BLE HID 固件
│   ├── main/
│   │   ├── esp_hid_device_main.c       # BLE HID 主程序
│   │   ├── esp_hid_gap.c               # BLE 连接管理
│   │   ├── input_handler.c/h           # GPIO 输入处理
│   │   └── led_indicator.c/h           # WS2812 LED 控制
│   └── sdkconfig.defaults
├── tusb_hid/                           # USB HID 固件
│   ├── main/
│   │   ├── tusb_hid_example_main.c     # USB HID 主程序
│   │   ├── input_handler.c/h           # GPIO 输入处理（共享）
│   │   └── led_indicator.c/h           # WS2812 LED 控制（共享）
│   └── sdkconfig.defaults
└── test/
    └── hid-test.html                   # HID 输入测试页面
```

## 相关项目

- [cosmo-pager-web-nextjs-vercel](https://github.com/RogerHao/cosmo-pager-web-nextjs-vercel) - Web 应用前端（由软件团队开发）

## 项目状态

- [x] 硬件方案设计
- [x] 外壳 3D 建模（进行中）
- [x] ESP32 供电方案验证
- [x] ESP32 BLE HID 固件开发
- [x] ESP32 USB HID 固件开发
- [x] WS2812 LED 状态指示
- [x] 硬件迁移：HUZZAH32 → XIAO ESP32S3
- [x] 硬件接线与功能测试
- [ ] 外壳 3D 打印与组装
- [ ] 整机调试

## 固件功能

### BLE HID 固件 (`firmware/`)

- NimBLE 协议栈蓝牙 HID 键盘
- 自动配对与重连
- GPIO 中断驱动的输入处理
- WS2812 LED 状态指示
- 15 秒长按强制重启

### USB HID 固件 (`tusb_hid/`)

- TinyUSB 协议栈 USB HID 键盘
- 即插即用，无需配对
- GPIO 中断驱动的输入处理（与 BLE 版共享）
- WS2812 LED 状态指示（与 BLE 版共享）
- 15 秒长按强制重启

## 构建与烧录

```bash
# 激活 ESP-IDF 环境
get_idf

# 选择固件（二选一）
cd firmware      # BLE HID
cd tusb_hid      # USB HID

# 设置目标芯片（首次）
idf.py set-target esp32s3

# 构建
idf.py build

# 烧录并监控
idf.py -p /dev/cu.usbmodem* flash monitor
```

## GPIO 引脚分配

| GPIO | XIAO 引脚 | 功能 |
|------|-----------|------|
| 1 | D0 | 按钮 |
| 2 | D1 | 旋钮1 CLK |
| 3 | D2 | 旋钮1 DT |
| 4 | D3 | 旋钮2 CLK |
| 5 | D4 | 旋钮2 DT |
| 6 | D5 | WS2812 LED |

## 文档索引

- [硬件架构设计](docs/design/hardware-architecture.md)
- [E5 Ultra 设备参考](docs/E5Ultra/README.md)
- [Adafruit HUZZAH32 参考](docs/references/adafruit-huzzah32.md)
- [ESP-IDF 蓝牙 HID 参考](docs/references/esp-idf-bluetooth-hid.md)
