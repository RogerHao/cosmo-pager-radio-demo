/*
 * Device Identity Module Implementation
 */

#include <stdio.h>
#include <string.h>
#include "device_identity.h"
#include "esp_log.h"
#include "esp_mac.h"
#include "nvs_flash.h"
#include "nvs.h"

static const char *TAG = "DEVICE_ID";

// Static storage for device identity strings
static char s_device_name[DEVICE_NAME_MAX_LEN + 1] = {0};
static char s_serial_number[16] = {0};  // "CR-" + 12 hex chars + null
static bool s_initialized = false;

// MAC address storage
static uint8_t s_mac_addr[6] = {0};

esp_err_t device_identity_init(void)
{
    if (s_initialized) {
        return ESP_OK;
    }

    esp_err_t ret;

    // Read base MAC address
    ret = esp_read_mac(s_mac_addr, ESP_MAC_BT);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to read MAC address: %d", ret);
        return ret;
    }

    ESP_LOGI(TAG, "MAC: %02X:%02X:%02X:%02X:%02X:%02X",
             s_mac_addr[0], s_mac_addr[1], s_mac_addr[2],
             s_mac_addr[3], s_mac_addr[4], s_mac_addr[5]);

    // Generate serial number: CR-XXXXXXXXXXXX (full MAC)
    snprintf(s_serial_number, sizeof(s_serial_number),
             "CR-%02X%02X%02X%02X%02X%02X",
             s_mac_addr[0], s_mac_addr[1], s_mac_addr[2],
             s_mac_addr[3], s_mac_addr[4], s_mac_addr[5]);

    // Generate default name: cosmo-XXXX (last 2 bytes of MAC)
    snprintf(s_device_name, sizeof(s_device_name),
             "cosmo-%02X%02X", s_mac_addr[4], s_mac_addr[5]);

    // Try to load custom name from NVS
    nvs_handle_t nvs_handle;
    ret = nvs_open(DEVICE_NVS_NAMESPACE, NVS_READONLY, &nvs_handle);
    if (ret == ESP_OK) {
        size_t name_len = sizeof(s_device_name);
        ret = nvs_get_str(nvs_handle, DEVICE_NVS_KEY_NAME, s_device_name, &name_len);
        if (ret == ESP_OK) {
            ESP_LOGI(TAG, "Loaded custom name from NVS: %s", s_device_name);
        } else if (ret == ESP_ERR_NVS_NOT_FOUND) {
            ESP_LOGI(TAG, "No custom name in NVS, using default");
        } else {
            ESP_LOGW(TAG, "NVS read error: %d, using default name", ret);
        }
        nvs_close(nvs_handle);
    } else if (ret != ESP_ERR_NVS_NOT_FOUND) {
        ESP_LOGW(TAG, "NVS open failed: %d, using default name", ret);
    }

    ESP_LOGI(TAG, "Device name: %s", s_device_name);
    ESP_LOGI(TAG, "Serial: %s", s_serial_number);

    s_initialized = true;
    return ESP_OK;
}

const char* device_identity_get_name(void)
{
    if (!s_initialized) {
        ESP_LOGW(TAG, "Not initialized, returning default");
        return "cosmo-radio";
    }
    return s_device_name;
}

const char* device_identity_get_serial(void)
{
    if (!s_initialized) {
        ESP_LOGW(TAG, "Not initialized, returning default");
        return "CR-000000000000";
    }
    return s_serial_number;
}

esp_err_t device_identity_set_name(const char* name)
{
    if (name == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    size_t len = strlen(name);
    if (len == 0 || len > DEVICE_NAME_MAX_LEN) {
        ESP_LOGE(TAG, "Invalid name length: %d (max %d)", (int)len, DEVICE_NAME_MAX_LEN);
        return ESP_ERR_INVALID_ARG;
    }

    nvs_handle_t nvs_handle;
    esp_err_t ret = nvs_open(DEVICE_NVS_NAMESPACE, NVS_READWRITE, &nvs_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "NVS open failed: %d", ret);
        return ret;
    }

    ret = nvs_set_str(nvs_handle, DEVICE_NVS_KEY_NAME, name);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "NVS write failed: %d", ret);
        nvs_close(nvs_handle);
        return ret;
    }

    ret = nvs_commit(nvs_handle);
    nvs_close(nvs_handle);

    if (ret == ESP_OK) {
        strncpy(s_device_name, name, DEVICE_NAME_MAX_LEN);
        s_device_name[DEVICE_NAME_MAX_LEN] = '\0';
        ESP_LOGI(TAG, "Custom name set: %s", s_device_name);
    }

    return ret;
}

esp_err_t device_identity_reset_name(void)
{
    nvs_handle_t nvs_handle;
    esp_err_t ret = nvs_open(DEVICE_NVS_NAMESPACE, NVS_READWRITE, &nvs_handle);
    if (ret != ESP_OK) {
        if (ret == ESP_ERR_NVS_NOT_FOUND) {
            // Already no custom name
            goto reset_to_default;
        }
        ESP_LOGE(TAG, "NVS open failed: %d", ret);
        return ret;
    }

    nvs_erase_key(nvs_handle, DEVICE_NVS_KEY_NAME);  // Ignore error if not exists
    nvs_commit(nvs_handle);
    nvs_close(nvs_handle);

reset_to_default:
    // Reset to MAC-based name
    snprintf(s_device_name, sizeof(s_device_name),
             "cosmo-%02X%02X", s_mac_addr[4], s_mac_addr[5]);
    ESP_LOGI(TAG, "Name reset to default: %s", s_device_name);

    return ESP_OK;
}
