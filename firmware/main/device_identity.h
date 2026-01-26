/*
 * Device Identity Module
 * Provides unique device naming based on MAC address with NVS customization support
 */

#ifndef _DEVICE_IDENTITY_H_
#define _DEVICE_IDENTITY_H_

#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

// Maximum length for device name (BLE limit is 29 bytes for name in adv data)
#define DEVICE_NAME_MAX_LEN 20

// NVS namespace and key for custom device name
#define DEVICE_NVS_NAMESPACE "device_id"
#define DEVICE_NVS_KEY_NAME "custom_name"

/**
 * Initialize device identity system
 * Reads MAC address and loads custom name from NVS if available
 * Must be called after nvs_flash_init()
 *
 * @return ESP_OK on success
 */
esp_err_t device_identity_init(void);

/**
 * Get device name for BLE advertising
 * Priority: 1) NVS custom name, 2) MAC-based name (cosmo-XXXX)
 *
 * @return Pointer to static device name string
 */
const char* device_identity_get_name(void);

/**
 * Get device serial number (full MAC address)
 * Format: CR-XXXXXXXXXXXX
 *
 * @return Pointer to static serial number string
 */
const char* device_identity_get_serial(void);

/**
 * Set custom device name (persisted to NVS)
 *
 * @param name Custom device name (max DEVICE_NAME_MAX_LEN chars)
 * @return ESP_OK on success, ESP_ERR_INVALID_ARG if name too long
 */
esp_err_t device_identity_set_name(const char* name);

/**
 * Reset device name to MAC-based default (removes custom name from NVS)
 *
 * @return ESP_OK on success
 */
esp_err_t device_identity_reset_name(void);

#ifdef __cplusplus
}
#endif

#endif /* _DEVICE_IDENTITY_H_ */
