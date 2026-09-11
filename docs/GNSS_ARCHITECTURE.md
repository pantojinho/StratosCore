# GNSS architecture

Baseline remains **ATGM332D-5NR32 via UART**. Exact pinout, ordering variant documentation, command manual and antenna implementation must be verified before schematic entry.

## Capability discrepancy

The [manufacturer's exact product page](https://www.icofchina.com/daohang/danpin/2441.html), checked 2026-09-11 UTC, lists GPS/QZSS and BeiDou by default, GLONASS as optional/configuration-dependent, 1 Hz output, NMEA0183, default 9600 baud, and a ROM variant without saved commands. It does **not list Galileo**. Its table gives 2.7-3.6 V supply and a 16.0 x 12.2 x 2.4 mm module envelope.

The prior conversation's broader constellation/update-rate claims are therefore not accepted as verified specifications. GPS/Galileo/BeiDou and GLONASS where supported remain desired capabilities, but Galileo and configurable higher update rates are unresolved for this exact part. Keep the chosen MPN; request a manufacturer command manual and ordering-code confirmation, then test a sample. If a requirement cannot be met, create a replacement proposal with all comparisons required by [AGENTS.md](../AGENTS.md).

## Antenna options (separate decision)

| Option | Benefit | Required work |
| --- | --- | --- |
| External active antenna | Flexible sky view and separation from board noise | Bias voltage/current, RF DC blocking, short/open protection, connector and cable loss |
| Passive patch in enclosure | Compact integrated user experience | Ground-plane size, patch orientation, housing clearance, body/battery/display detuning |
| External passive antenna | Removes internal antenna volume without bias power | Receiver noise budget and cable-loss limit |

No antenna position or ground-plane dimension is locked. Select passbands only after constellations are confirmed. Reserve space for protection/matching and, if needed, a controlled antenna-bias network; do not blindly feed a module RF pin with DC. Compare internal antenna reception in both UI orientations and with the second cell installed.

## Integration and validation

Use a quiet supply compatible with verified VCC/VIO/backup limits. Determine whether backup power, enable and PPS are supported by the exact module, then reserve only verified signals. Level shifting, pullups, boot commands and unpowered-UART behavior require review. A ROM module may need configuration replay after every boot.

Parse NMEA with checksum, bounded line lengths and timeouts. Log fix quality, satellites, time validity, altitude datum and age; distinguish geometric GNSS altitude from barometric altitude. Verify cold/warm start, no-sky recovery, command persistence, rate, constellations and PPS/UTC relationship where available. Compare C/N0 and fix stability during LoRa TX, Wi-Fi, display refresh, SD writes and charging. Confirm dynamics/altitude limits for balloon missions; no high-altitude guarantee is assumed.
