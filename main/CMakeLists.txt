idf_component_register(
    SRCS "tusb_hid_example_main.c"
         "input_handler.c"
         "led_indicator.c"
         "nfc_handler.c"
    INCLUDE_DIRS "."
    # esp_psram is required (even though we don't call its API) so that under
    # MINIMAL_BUILD its Kconfig is loaded — otherwise CONFIG_SPIRAM and friends
    # silently get dropped from sdkconfig.defaults as "unknown symbols".
    PRIV_REQUIRES esp_driver_gpio esp_driver_spi esp_timer led_strip esp_psram
)
