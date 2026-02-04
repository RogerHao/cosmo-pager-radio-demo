# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hardware mod project: Building a desktop "Parallel Universe Radio" device using an Android tablet with custom input controls via ESP32 HID (BLE or USB).

**Architecture**: Android Tablet <-- HID (BLE/USB) --> XIAO ESP32S3 <-- GPIO --> EC11 rotary encoders + button + WS2812 LED

## Firmware Options

The project supports two HID implementations:

| Firmware | Directory | Connection | Use Case |
|----------|-----------|------------|----------|
| BLE HID | `firmware/` | Bluetooth Low Energy | Wireless, battery-powered |
| USB HID | `tusb_hid/` | USB cable | Wired, more stable, lower latency |

## Build Commands

All firmware commands require ESP-IDF environment active:

```bash
# Initialize ESP-IDF environment (if using get_idf alias)
get_idf

# For BLE HID firmware
cd firmware

# For USB HID firmware
cd tusb_hid

# Set target chip (first time only)
idf.py set-target esp32s3

# Build firmware
idf.py build

# Flash to device
idf.py -p /dev/cu.usbmodem* flash

# Monitor serial output
idf.py -p /dev/cu.usbmodem* monitor

# Build + Flash + Monitor combined
idf.py -p /dev/cu.usbmodem* flash monitor

# Clean build
idf.py fullclean
```

## Code Architecture

```
firmware/                          # BLE HID implementation
├── main/
│   ├── esp_hid_device_main.c      # Entry point, BLE HID + input handling
│   ├── esp_hid_gap.c              # BLE GAP/GATT, pairing, connection
│   ├── input_handler.c/h          # GPIO interrupt-based input
│   └── led_indicator.c/h          # WS2812 LED control
├── sdkconfig.defaults
└── CMakeLists.txt

tusb_hid/                          # USB HID implementation
├── main/
│   ├── tusb_hid_example_main.c    # Entry point, USB HID + input handling
│   ├── input_handler.c/h          # GPIO interrupt-based input (shared)
│   └── led_indicator.c/h          # WS2812 LED control (shared)
├── sdkconfig.defaults
└── CMakeLists.txt
```

**Shared modules**: `input_handler` and `led_indicator` are protocol-agnostic and identical in both firmware projects.

## GPIO Pin Assignments

| GPIO | XIAO Pin | Function | Module |
|------|----------|----------|--------|
| 1 | D0 | Button | input_handler |
| 2 | D1 | Encoder 1 CLK | input_handler |
| 3 | D2 | Encoder 1 DT | input_handler |
| 4 | D3 | Encoder 2 CLK | input_handler |
| 5 | D4 | Encoder 2 DT | input_handler |
| 6 | D5 | WS2812 LED | led_indicator |
| 19 | — | USB D- | TinyUSB (native) |
| 20 | — | USB D+ | TinyUSB (native) |

All input GPIOs use internal pull-up resistors. Active low (connect to GND when triggered).

## HID Key Mappings

| Input | HID Key | Description |
|-------|---------|-------------|
| Button press | Enter | Confirm action |
| Button release | (key up) | |
| Encoder 1 CW | ↑ Up arrow | Frequency up |
| Encoder 1 CCW | ↓ Down arrow | Frequency down |
| Encoder 2 CW | → Right arrow | Mode next |
| Encoder 2 CCW | ← Left arrow | Mode previous |

## LED Indicator Behavior

| Event | LED Color |
|-------|-----------|
| Button pressed | Red |
| Button released | Off |
| USB/BLE connected | Blue flash |
| Startup | Green flash |

## VS Code Workspace

Use the multi-root workspace for proper ESP-IDF extension support:
```bash
code cosmo-pager-radio.code-workspace
```

## Hardware Target

- **Board**: Seeed Studio XIAO ESP32S3
- **Power**: USB or 3.7V Li-battery → XIAO B+/B- pads
- **Flash**: 8MB
- **LED**: WS2812 RGB on GPIO6 (D5)

## HID Input Test Tool

A retro-futuristic test page for verifying HID input functionality:

```
test/hid-test.html
```

**Features:**
- Three-circle layout matching physical mask (1280x720 screen)
- Left dial: Frequency display (88.0-108.0 MHz), controlled by ↑↓ keys
- Right dial: Mode selector (FM/AM/SW/LW/MW), controlled by ←→ keys
- Center: Confirm button, controlled by Enter key
- Smooth continuous scroll animation (retro radio dial style)
- Amber/cyan glow effects with CRT aesthetic

**Usage:** Transfer to device and open in browser for HID input testing.

## Special Features

### Force Restart
Hold the button for 15 seconds to trigger a device restart. Useful for recovery from stuck states.

## Known Limitations / Technical Debt

### HID Key Report: No Multi-key Support

Current `send_key_up()` releases ALL keys (sends empty report), not a specific key. This is fine for current single-button use case, but will cause issues if:
- User holds button while rotating encoder
- Future features require modifier keys (Shift+Enter, etc.)

**Fix when needed**: Maintain a `pressed_keys[6]` state array, add/remove individual keycodes, and send updated report on each change.

## Documentation Language

- Code comments: English
- Project docs (README, docs/): Chinese
