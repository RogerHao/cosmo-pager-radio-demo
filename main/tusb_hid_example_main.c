/*
 * Cosmo Pager Radio - USB HID Keyboard
 *
 * Converts rotary encoder and button inputs to USB HID keyboard events.
 * Replaces the BLE HID implementation for improved reliability.
 *
 * Input mapping:
 *   - Button press/release -> Enter key press/release
 *   - Encoder 1 CW/CCW -> Up/Down arrow key pulse
 *   - Encoder 2 CW/CCW -> Right/Left arrow key pulse
 */

#include <stdlib.h>
#include <string.h>
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "tinyusb.h"
#include "tinyusb_default_config.h"
#include "class/hid/hid_device.h"

#include "input_handler.h"
#include "led_indicator.h"
#include "nfc_handler.h"

static const char *TAG = "USB_HID";

// HID key codes
#define KEY_ENTER       0x28  // HID_KEY_ENTER
#define KEY_UP_ARROW    0x52  // HID_KEY_ARROW_UP
#define KEY_DOWN_ARROW  0x51  // HID_KEY_ARROW_DOWN
#define KEY_LEFT_ARROW  0x50  // HID_KEY_ARROW_LEFT
#define KEY_RIGHT_ARROW 0x4F  // HID_KEY_ARROW_RIGHT
#define KEY_F1          0x3A  // HID_KEY_F1 — placeholder for ENC1 SW
#define KEY_F2          0x3B  // HID_KEY_F2 — placeholder for ENC2 SW

// HID modifier byte
#define HID_MOD_LSHIFT  0x02

// Key pulse duration (ms) for rotary encoder events
#define KEY_PULSE_MS    20

// Per-character pulse duration when typing strings (NFC UID, etc.)
#define STRING_KEY_DOWN_MS  15
#define STRING_KEY_UP_MS    15

/************* TinyUSB descriptors ****************/

#define TUSB_DESC_TOTAL_LEN (TUD_CONFIG_DESC_LEN + CFG_TUD_HID * TUD_HID_DESC_LEN)

// HID report descriptor - keyboard only (no mouse)
const uint8_t hid_report_descriptor[] = {
    TUD_HID_REPORT_DESC_KEYBOARD(HID_REPORT_ID(HID_ITF_PROTOCOL_KEYBOARD)),
};

// String descriptor
const char *hid_string_descriptor[5] = {
    (char[]){0x09, 0x04},      // 0: Supported language is English (0x0409)
    "Cosmo",                   // 1: Manufacturer
    "Pager Radio Input",       // 2: Product
    "000001",                  // 3: Serial number
    "HID Keyboard",            // 4: HID interface
};

// Configuration descriptor
static const uint8_t hid_configuration_descriptor[] = {
    // Configuration number, interface count, string index, total length, attribute, power in mA
    TUD_CONFIG_DESCRIPTOR(1, 1, 0, TUSB_DESC_TOTAL_LEN, TUSB_DESC_CONFIG_ATT_REMOTE_WAKEUP, 100),

    // Interface number, string index, boot protocol, report descriptor len, EP In address, size & polling interval
    TUD_HID_DESCRIPTOR(0, 4, false, sizeof(hid_report_descriptor), 0x81, 16, 10),
};

/********* TinyUSB HID callbacks ***************/

// Invoked when received GET HID REPORT DESCRIPTOR request
uint8_t const *tud_hid_descriptor_report_cb(uint8_t instance)
{
    (void)instance;
    return hid_report_descriptor;
}

// Invoked when received GET_REPORT control request
uint16_t tud_hid_get_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t report_type,
                               uint8_t *buffer, uint16_t reqlen)
{
    (void)instance;
    (void)report_id;
    (void)report_type;
    (void)buffer;
    (void)reqlen;
    return 0;
}

// Invoked when received SET_REPORT control request
void tud_hid_set_report_cb(uint8_t instance, uint8_t report_id, hid_report_type_t report_type,
                           uint8_t const *buffer, uint16_t bufsize)
{
    (void)instance;
    (void)report_id;
    (void)report_type;
    (void)buffer;
    (void)bufsize;
}

/********* HID Key Functions ***************/

// Send a key press (key down)
static void send_key_down(uint8_t keycode)
{
    if (!tud_mounted()) {
        return;
    }

    uint8_t keycodes[6] = {keycode, 0, 0, 0, 0, 0};
    tud_hid_keyboard_report(HID_ITF_PROTOCOL_KEYBOARD, 0, keycodes);
}

// Send key release (all keys up)
static void send_key_up(void)
{
    if (!tud_mounted()) {
        return;
    }

    tud_hid_keyboard_report(HID_ITF_PROTOCOL_KEYBOARD, 0, NULL);
}

// Send a key pulse (press + delay + release) - for encoder events
static void send_key_pulse(uint8_t keycode)
{
    send_key_down(keycode);
    vTaskDelay(pdMS_TO_TICKS(KEY_PULSE_MS));
    send_key_up();
}

// Send a key with modifier (e.g., shift for uppercase letters)
static void send_key_down_mod(uint8_t modifier, uint8_t keycode)
{
    if (!tud_mounted()) {
        return;
    }
    uint8_t keycodes[6] = {keycode, 0, 0, 0, 0, 0};
    tud_hid_keyboard_report(HID_ITF_PROTOCOL_KEYBOARD, modifier, keycodes);
}

// Translate ASCII to HID (modifier, keycode). Returns false if char not supported.
// Covers what the NFC tag protocols need: alphanumeric, the '#' / 'NFC:' prefixes,
// '\n' line terminator, plus a small set of separators safe for ID encoding
// ('-', '_', '.', '/'). Space and other punctuation are intentionally omitted —
// the tag-content encoding contract is "ASCII identifier characters only".
static bool ascii_to_hid(char c, uint8_t *modifier, uint8_t *keycode)
{
    *modifier = 0;
    if (c >= 'a' && c <= 'z') {
        *keycode = 0x04 + (c - 'a');
        return true;
    } else if (c >= 'A' && c <= 'Z') {
        *modifier = HID_MOD_LSHIFT;
        *keycode = 0x04 + (c - 'A');
        return true;
    } else if (c == '0') {
        *keycode = 0x27;
        return true;
    } else if (c >= '1' && c <= '9') {
        *keycode = 0x1E + (c - '1');
        return true;
    } else if (c == '#') {
        // '#' shares the '3' key (HID 0x20), needs Shift
        *modifier = HID_MOD_LSHIFT;
        *keycode = 0x20;
        return true;
    } else if (c == ':') {
        // ':' shares physical key with ';' (HID 0x33), needs Shift
        *modifier = HID_MOD_LSHIFT;
        *keycode = 0x33;
        return true;
    } else if (c == '-') {
        *keycode = 0x2D;
        return true;
    } else if (c == '_') {
        // Underscore = Shift + minus
        *modifier = HID_MOD_LSHIFT;
        *keycode = 0x2D;
        return true;
    } else if (c == '.') {
        *keycode = 0x37;
        return true;
    } else if (c == '/') {
        *keycode = 0x38;
        return true;
    } else if (c == '\n') {
        *keycode = KEY_ENTER;
        return true;
    }
    return false;
}

// Type a null-terminated string via HID keyboard. Skips unsupported chars.
static void send_string(const char *str)
{
    for (const char *p = str; *p; p++) {
        uint8_t mod, kc;
        if (!ascii_to_hid(*p, &mod, &kc)) {
            continue;
        }
        send_key_down_mod(mod, kc);
        vTaskDelay(pdMS_TO_TICKS(STRING_KEY_DOWN_MS));
        send_key_up();
        vTaskDelay(pdMS_TO_TICKS(STRING_KEY_UP_MS));
    }
}

/********* Input Event Handling ***************/

// Callback for input events from input_handler module
static void on_input_event(const input_event_t *event)
{
    switch (event->type) {
    case INPUT_EVENT_BUTTON_PRESS:
        ESP_LOGI(TAG, "BTN -> ENTER (pressed)");
        led_indicator_red();
        send_key_down(KEY_ENTER);
        break;

    case INPUT_EVENT_BUTTON_RELEASE:
        ESP_LOGI(TAG, "BTN -> ENTER (released)");
        led_indicator_off();
        send_key_up();
        break;

    case INPUT_EVENT_ENC1_CW:
        ESP_LOGI(TAG, "ENC1 CW -> UP");
        send_key_pulse(KEY_UP_ARROW);
        break;

    case INPUT_EVENT_ENC1_CCW:
        ESP_LOGI(TAG, "ENC1 CCW -> DOWN");
        send_key_pulse(KEY_DOWN_ARROW);
        break;

    case INPUT_EVENT_ENC1_SW_PRESS:
        ESP_LOGI(TAG, "ENC1 SW -> F1 (pressed)");
        send_key_down(KEY_F1);
        break;

    case INPUT_EVENT_ENC1_SW_RELEASE:
        ESP_LOGI(TAG, "ENC1 SW -> F1 (released)");
        send_key_up();
        break;

    case INPUT_EVENT_ENC2_CW:
        ESP_LOGI(TAG, "ENC2 CW -> RIGHT");
        send_key_pulse(KEY_RIGHT_ARROW);
        break;

    case INPUT_EVENT_ENC2_CCW:
        ESP_LOGI(TAG, "ENC2 CCW -> LEFT");
        send_key_pulse(KEY_LEFT_ARROW);
        break;

    case INPUT_EVENT_ENC2_SW_PRESS:
        ESP_LOGI(TAG, "ENC2 SW -> F2 (pressed)");
        send_key_down(KEY_F2);
        break;

    case INPUT_EVENT_ENC2_SW_RELEASE:
        ESP_LOGI(TAG, "ENC2 SW -> F2 (released)");
        send_key_up();
        break;

    default:
        break;
    }
}

// NFC tag scan callback — typed protocol depends on what's on the tag:
//   - NDEF Text payload present → "#<payload>\n" (product-content protocol)
//   - No NDEF / unparseable     → "NFC:<UID>\n"  (UID fallback for diagnostics)
// The Android app distinguishes the two by the leading character.
static void on_nfc_tag(const char *payload, const char *uid_hex)
{
    char buf[64];
    int n;
    if (payload != NULL) {
        n = snprintf(buf, sizeof(buf), "#%s\n", payload);
    } else {
        n = snprintf(buf, sizeof(buf), "NFC:%s\n", uid_hex);
    }
    if (n <= 0 || n >= (int)sizeof(buf)) {
        ESP_LOGW(TAG, "NFC HID buffer overflow, uid=%s", uid_hex);
        return;
    }

    // Strip trailing newline for cleaner log line
    char log_buf[64];
    strncpy(log_buf, buf, sizeof(log_buf) - 1);
    log_buf[sizeof(log_buf) - 1] = '\0';
    size_t L = strlen(log_buf);
    if (L > 0 && log_buf[L - 1] == '\n') log_buf[L - 1] = '\0';
    ESP_LOGI(TAG, "NFC -> typing '%s\\n'", log_buf);

    led_indicator_blue();
    send_string(buf);
    led_indicator_off();
}

/********* Main Application ***************/

void app_main(void)
{
    ESP_LOGI(TAG, "Cosmo Pager Radio - USB HID Keyboard");

    // Initialize USB
    ESP_LOGI(TAG, "USB initialization");
    tinyusb_config_t tusb_cfg = TINYUSB_DEFAULT_CONFIG();

    tusb_cfg.descriptor.device = NULL;
    tusb_cfg.descriptor.full_speed_config = hid_configuration_descriptor;
    tusb_cfg.descriptor.string = hid_string_descriptor;
    tusb_cfg.descriptor.string_count = sizeof(hid_string_descriptor) / sizeof(hid_string_descriptor[0]);
#if (TUD_OPT_HIGH_SPEED)
    tusb_cfg.descriptor.high_speed_config = hid_configuration_descriptor;
#endif

    ESP_ERROR_CHECK(tinyusb_driver_install(&tusb_cfg));
    ESP_LOGI(TAG, "USB initialization DONE");

    // Initialize LED indicator
    ESP_ERROR_CHECK(led_indicator_init());

    // Initialize input handler
    ESP_ERROR_CHECK(input_handler_init());
    input_handler_set_callback(on_input_event);
    input_handler_start();

    // Initialize NFC handler (RC522 on SPI2)
    ESP_ERROR_CHECK(nfc_handler_init());
    nfc_handler_set_callback(on_nfc_tag);
    ESP_ERROR_CHECK(nfc_handler_start());

    // Brief startup indication
    led_indicator_green();
    vTaskDelay(pdMS_TO_TICKS(200));
    led_indicator_off();

    // Main loop - monitor USB connection status
    bool was_mounted = false;
    while (1) {
        bool is_mounted = tud_mounted();

        if (is_mounted && !was_mounted) {
            ESP_LOGI(TAG, "USB connected");
            led_indicator_blue();
            vTaskDelay(pdMS_TO_TICKS(100));
            led_indicator_off();
        } else if (!is_mounted && was_mounted) {
            ESP_LOGW(TAG, "USB disconnected");
        }

        was_mounted = is_mounted;
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
