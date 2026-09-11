# ESP32 firmware plan

Own display/touch/buttons, GNSS, sensors/fusion, LoRa, optional MeshCore roles, microSD, audio, power/profile control and networking. All features are plans, not working firmware.

Suggested service boundaries: board support, timebase, GNSS, sensors, navigation/vario, radio, ADS-B transport/contact store, logger, audio, UI, power and diagnostics. State includes units/validity/age. SD has one owner; UI/network clients consume snapshots so they cannot block acquisition. Use raw and derived data with source/calibration/version tags.

Before implementing: approve [bus/GPIO allocation](../../docs/SYSTEM_ARCHITECTURE.md), firmware framework and third-party license inventory. Root [MeshCore](https://github.com/meshcore-dev/MeshCore) is MIT at the reviewed revision; verify the chosen target's transitive dependencies, radio configuration, BLE/Wi-Fi use and scheduler requirements. Companion/repeater behavior is a porting objective, not a claim of compatibility.
