/*
 * NFC Handler Module
 * RC522 SPI scanner integration for NTAG / Mifare tag detection.
 * Reads NDEF Text Record payload when present; falls back to UID on parse failure.
 */

#ifndef _NFC_HANDLER_H_
#define _NFC_HANDLER_H_

#include "esp_err.h"

#ifdef __cplusplus
extern "C" {
#endif

// Maximum NDEF Text payload length we'll surface (longer payloads truncated).
// Keep small enough that HID typing latency stays under ~1s.
#define NFC_PAYLOAD_MAX_LEN 32

// Invoked when a tag is detected.
//   payload: NDEF Text Record content, NULL-terminated, or NULL if no parseable
//            Text record was found on the tag.
//   uid_hex: always non-NULL; the card's UID as continuous uppercase hex.
// Both buffers are owned by the caller — copy if you need them past the callback.
typedef void (*nfc_tag_callback_t)(const char *payload, const char *uid_hex);

esp_err_t nfc_handler_init(void);
void nfc_handler_set_callback(nfc_tag_callback_t cb);
esp_err_t nfc_handler_start(void);

#ifdef __cplusplus
}
#endif

#endif /* _NFC_HANDLER_H_ */
