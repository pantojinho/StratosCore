# GNSS architecture

Rev A baseline is **u-blox MAX-M10S-00B via UART**, accepted by the owner on 2026-09-13. The previous ATGM332D-5NR32 baseline remains comparison evidence only because its 18 km altitude ceiling conflicts with balloon use.

## Verified capability and mission conflict

The [full ATGM332D-5NR32 manual](https://datasheet.lcsc.com/lcsc/2206231830_ZHONGKEWEI-ATGM332D-5NR32_C3037611.pdf), checked 2026-09-11 UTC, lists BDS/GPS/GLONASS/Galileo/QZSS/SBAS, 1 Hz default with 10 Hz maximum, NMEA0183, 2.7-3.6 V supply, less than 26 mA at 3.3 V and a 15.9 x 12.1 x 2.4 mm module. It also specifies a maximum altitude of 18,000 m.

Galileo and the higher update rate are documented for the previous module, but high-altitude balloon compatibility is not. [Component evidence](COMPONENT_EVIDENCE.md) records the accepted u-blox `MAX-M10S-00B`, whose manufacturer documents airborne modes to 80,000 m, explicit multi-GNSS support and configurable higher rates. Do not place its symbol or footprint until the exact ordering code, pad drawing, supply/backup application and antenna circuit have been checked against the current manufacturer documents.

## Antenna options (separate decision)

| Option | Benefit | Required work |
| --- | --- | --- |
| External active antenna | Flexible sky view and separation from board noise | Bias voltage/current, RF DC blocking, short/open protection, connector and cable loss |
| Passive patch in enclosure | Compact integrated user experience | Ground-plane size, patch orientation, housing clearance, body/battery/display detuning |
| External passive antenna | Removes internal antenna volume without bias power | Receiver noise budget and cable-loss limit |

No antenna position or ground-plane dimension is locked. Select passbands only after constellations are confirmed. Reserve space for protection/matching and, if needed, a controlled antenna-bias network; do not blindly feed a module RF pin with DC. Compare internal antenna reception in both UI orientations and with the second cell installed.

## Integration and validation

Use a quiet supply compatible with verified VCC/VIO/backup limits. Verify backup power, enable and timepulse behavior for MAX-M10S-00B, then reserve only documented signals. Level shifting, pullups, boot commands and unpowered-UART behavior require review. Firmware must explicitly configure the appropriate airborne dynamic model and verify configuration persistence.

Parse NMEA with checksum, bounded line lengths and timeouts. Log fix quality, satellites, time validity, altitude datum and age; distinguish geometric GNSS altitude from barometric altitude. Verify cold/warm start, no-sky recovery, command persistence, rate, constellations and PPS/UTC relationship where available. Compare C/N0 and fix stability during LoRa TX, Wi-Fi, display refresh, SD writes and charging. Confirm dynamics/altitude limits for balloon missions; no high-altitude guarantee is assumed.
