# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hardware mod project: Converting E5 Ultra Android handheld into a desktop "Parallel Universe Radio" device with custom input controls via ESP32 BLE HID.

**Architecture**: E5 Ultra (Android host) <-- BLE HID --> XIAO ESP32S3 <-- GPIO --> EC11 rotary encoders + button

## Build Commands

All firmware commands must be run from the `firmware/` directory with ESP-IDF environment active:

```bash
# Initialize ESP-IDF environment (if using get_idf alias)
get_idf

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

# Open menuconfig for configuration
idf.py menuconfig

# Clean build
idf.py fullclean
```

## Key Configuration

Configuration is driven by `firmware/sdkconfig.defaults`. Key settings:

| Setting | Value | Purpose |
|---------|-------|---------|
| `CONFIG_BT_NIMBLE_ENABLED` | y | Use NimBLE stack (lighter than Bluedroid) |
| `CONFIG_EXAMPLE_KBD_ENABLE` | y | HID Keyboard mode |
| `CONFIG_BT_NIMBLE_MAX_CONNECTIONS` | 1 | Single device connection |
| `CONFIG_ESPTOOLPY_FLASHSIZE_8MB` | y | XIAO ESP32S3 flash size |

To change HID device role, modify `CONFIG_EXAMPLE_*_ENABLE` in sdkconfig.defaults or use menuconfig: `HID Example Configuration > HID Device Role`.

## Code Architecture

```
firmware/
├── main/
│   ├── esp_hid_device_main.c   # Entry point, HID report maps, input handling
│   ├── esp_hid_gap.c           # BLE GAP/GATT, pairing, connection management
│   └── esp_hid_gap.h           # HID mode definitions (BLE/BTDM)
├── sdkconfig.defaults          # Source of truth for build config
└── CMakeLists.txt              # IDF project setup
```

**Conditional compilation**: Code supports both Bluedroid (`CONFIG_BT_BLE_ENABLED`) and NimBLE (`CONFIG_BT_NIMBLE_ENABLED`) stacks. Current config uses NimBLE only.

## HID Key Mappings

| Input | HID Key | GPIO | XIAO Pin |
|-------|---------|------|----------|
| Top button | Enter | 1 | D0 |
| EC11 #1 CW | Up arrow | 2 (CLK) | D1 |
| EC11 #1 CCW | Down arrow | 3 (DT) | D2 |
| EC11 #2 CW | Right arrow | 4 (CLK) | D3 |
| EC11 #2 CCW | Left arrow | 5 (DT) | D4 |

All input GPIOs use internal pull-up resistors. Active low (connect to GND when triggered).

## VS Code Workspace

Use the multi-root workspace for proper ESP-IDF extension support:
```bash
code cosmo-pager-radio.code-workspace
```

This allows the ESP-IDF extension to recognize `firmware/` as a separate ESP-IDF project.

## Hardware Target

- **Board**: Seeed Studio XIAO ESP32S3
- **Power**: 3.7V Li-battery → XIAO B+/B- pads (on back)
- **Flash**: 8MB

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

## Documentation Language

- Code comments: English
- Project docs (README, docs/): Chinese
