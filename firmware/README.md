# Firmware foundation

Original firmware will use MIT. No code has been imported and no build/toolchain is configured. ESP-IDF/FreeRTOS is a proposal; MeshCore port and dependency compatibility require review before selection.

- [ESP32 responsibilities](esp32/README.md)
- [RP2040 ADS-B responsibilities](rp2040_adsb/README.md)
- [Bring-up sequence](bringup/README.md)

Keep drivers, board configuration, time/data model and services separate. Do not copy legacy pins. Use bounded queues, validity/age, explicit errors and independent watchdog recovery. Avoid embedding regional RF assumptions in universal defaults.
