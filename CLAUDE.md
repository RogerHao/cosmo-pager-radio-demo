# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hardware mod project: Converting E5 Ultra Android handheld into a desktop "Parallel Universe Radio" device with custom input controls via ESP32 BLE HID.

**Architecture**: E5 Ultra (Android host) <-- BLE HID --> ESP32 HUZZAH32 <-- GPIO --> EC11 rotary encoders + button

## Build Commands

All firmware commands must be run from the `firmware/` directory with ESP-IDF environment active:

```bash
# Initialize ESP-IDF environment (if using get_idf alias)
get_idf

# Set target chip (first time only)
idf.py set-target esp32

# Build firmware
idf.py build

# Flash to device
idf.py -p /dev/cu.usbserial-0001 flash

# Monitor serial output
idf.py -p /dev/cu.usbserial-0001 monitor

# Build + Flash + Monitor combined
idf.py -p /dev/cu.usbserial-0001 flash monitor

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
| `CONFIG_BTDM_CTRL_MODE_BLE_ONLY` | y | BLE only, no Classic BT |
| `CONFIG_EXAMPLE_KBD_ENABLE` | y | HID Keyboard mode |
| `CONFIG_BT_NIMBLE_MAX_CONNECTIONS` | 1 | Single device connection |

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

| Input | HID Key | GPIO | Notes |
|-------|---------|------|-------|
| Top button | Enter | 27 | Directly above encoder GPIOs |
| EC11 #1 CW | Up arrow | 33 (CLK) | |
| EC11 #1 CCW | Down arrow | 15 (DT) | |
| EC11 #2 CW | Right arrow | 32 (CLK) | |
| EC11 #2 CCW | Left arrow | 14 (DT) | |

All input GPIOs use internal pull-up resistors. Active low (connect to GND when triggered).

## VS Code Workspace

Use the multi-root workspace for proper ESP-IDF extension support:
```bash
code cosmo-pager-radio.code-workspace
```

This allows the ESP-IDF extension to recognize `firmware/` as a separate ESP-IDF project.

## Hardware Target

- **Board**: Adafruit HUZZAH32 (ESP32 WROOM32)
- **Power**: 3.5-3.7V from E5 Ultra mainboard → HUZZAH32 BAT pin
- **Flash**: 4MB

## Documentation Language

- Code comments: English
- Project docs (README, docs/): Chinese
