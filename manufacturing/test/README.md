# Verification and production-test planning

No electrical tests have been executed. Before Astra placement, freeze the DFT coverage matrix: required nets, pad family and minimum dimensions, permitted face, fixture pitch, current limits, programming access, RF injection points, instrumentation and planned acceptance values. Astra assigns test-point references and coordinates during CAD execution. After placement/routing, review physical probe access and fixture feasibility; after PCBA, execute and record the electrical tests.

## DFT coverage matrix (DFT-01, frozen 2026-09-22)

Pre-placement freeze required by O28: every access point below exists in an accepted task deliverable (DIG-01/02/03, PWR-02/04, GNSS-01, AUD-01, PWR-02 USB input, P25 RF ports). **Astra assigns reference designators and coordinates; nothing here releases a footprint.** Pad family defaults: signal/test pads 1.0 x 0.6 mm SMD test pad (probe class >= 100 mil pitch fixture access), rail measure points 1.2 mm round pad with 0.3 ohm-class shunt resistor optional where current measurement needs it; all access **top face unless noted**; fixture target pitch 1.27 mm between access points (real fixturing feasibility is reviewed after layout, as O28 requires).

| # | Net / access | Type | Pad / face | Purpose and measured quantity | Acceptance basis |
| --: | --- | --- | --- | --- | --- |
| 1 | SWCLK + SWDIO (RP2040) | Programming/debug pads (Tag-Connect-class footprint, board edge) | per DIG-01 footprint; top | Full-image programming, checksum, reset-reason readback; 24 MHz max clock per datasheet | DIG-01 corner plan step 3 |
| 2 | RUN (RP2040 reset) | Test pad | 1.0 mm pad; top | Controlled reset cycling with flash-write quiesce verified | DIG-01 corner plan step 2 |
| 3 | USB_BOOT (RP2040 QSPI_SS strap) | Test pad | 1.0 mm pad; top | BOOTSEL entry via grounding while toggling RUN | DIG-01 corner plan step 4 |
| 4 | ESP32 UART0 console (GPIO43/44) + 3V3/GND | 4-pad programming strip, board edge | 1.27 mm pitch strip; top | Boot log, recovery without USB, serial/console access | GPIO map recovery contract |
| 5 | ESP32 native USB | Connector (no extra pads) | USB4105 at board edge | Firmware flash, console, enumeration tests | PWR-02 attach policy |
| 6 | GNSS_TX / GNSS_RX / GNSS_PPS | 3 test pads | 1.0 mm pads; top | UBX bring-up at 9600->115200, PPS qualification | GNSS-01 host interface plan |
| 7 | SD_CD + 3V3_SD measure point | 2 pads | 1.0 mm + 1.2 mm round; top | Card-detect state; switched-rail current for PWR-04/O13 | DIG-02 DFT hook |
| 8 | `3V3_MAIN` measure point | Rail pad pair (rail + GND) | 1.2 mm round; top | Simultaneous-peak verification against the PWR-04 envelope; droop scope point | PWR-04 measurement plan |
| 9 | `3V0_RF_QUIET` measure point | Rail pad pair | 1.2 mm round; top | ADS-B analog chain current (85 mA class) and noise supply check | PWR-04 LDO row |
| 10 | `1V8_LOGIC` measure point | Rail pad pair | 1.2 mm round; top | Display/audio 1.8 V load and sequencing check | PWR-04 LDO row |
| 11 | Protected 2S bus B+/B- measure points | Rail pad pair, **near battery holder** | 1.2 mm round; top | Pack voltage under charge/load; cell fault tests | POWER_INPUT_EVIDENCE O05 matrix |
| 12 | MID (2S midpoint via BQ25887 CBSET/MID path) | Test pad | 1.0 mm pad; top | Per-cell voltage split, balance verification | PWR-03/O05 review row |
| 13 | Charger input (eFuse output side) | Rail pad pair | 1.2 mm round; top | USB/charge input current verification vs 500 mA policy floor and 1.97 A breaker | PWR-02 network |
| 14 | RF conducted ports (GNSS U.FL, ADS-B SMA via CAB.721, optional LoRa SMA) | Existing antenna connectors - no added pads | connectors | Conducted TX/RX, sensitivity, spurious, coexistence per the RF validation plans | LORA-03/ADSB-03/GNSS-03 plans |
| 15 | RF injection: GNSS RF_IN and ADS-B input | Injected at the U.FL/SMA ports (no separate pads) | connectors | Blocker/coexistence injection (915 MHz into GNSS per the recorded -17 dBm immunity row) | GNSS-01/GNSS-03 |
| 16 | `AUD_SW_EN_N` domain + PDM_CLK/PDM_DATA | 2 test pads + rail pad | 1.0 mm pads; top | 1V8 domain toggle recovery; PDM levels/duty | AUD-01 recovery row |
| 17 | I2C SDA/SCL (shared bus) | 2 test pads | 1.0 mm pads; top | Rise-time/VOL post-PCBA validation of the 100 kHz window; stuck-bus recovery drill | SYS-01/I2C budget closure criterion 6 |

**Current limits for probing:** rail measure points sized for the PWR-04 envelope (3V3_MAIN worst ~1.4 A class: pad pair supports clamp-probe or shunt method; no measurement method that adds >0.1 ohm in the 3V3_MAIN path at load). Battery/charge paths (11/13) support the O05 fault-test instrumentation; the exact fault-matrix instrumentation remains with the qualified battery review.

**Deliberately not frozen here:** production screening limits (they need measured data), fixture pin-out wiring (post-layout), and any access to the 2S protection FET nodes (PWR-03/O05 territory - not invented here).



| Area | Planned evidence |
| --- | --- |
| Power and battery | Short/leakage, rails under transient load, USB/charge limits, either cell reversed/missing/removed, 2S mismatch/balance and thermal protection |
| Compute | Boot/recovery, exact Flash/PSRAM capacity, RP2040 programming/watchdog |
| Sensors/GNSS | IDs, axes, calibration sanity, pressure/temperature response, GNSS fix/UTC and antenna behavior |
| UI | Pixel/touch tests, orientation mapping, two buttons, dim/sleep/wake |
| Logging/audio | Sustained writes, bounded latency, full/removed card, reset/power-loss behavior, synchronized sample timestamps |
| LoRa | Conducted RF power/frequency and RX, BUSY/IRQ handling, regional configuration gating |
| ADS-B | Known-frame acceptance/rejection, capture timing, analog dynamic range, queue/host saturation and contact validity |
| Complete assembly | RF coexistence, thermal drift, both cell populations, long-duration FLIGHT/BALLOON/DESKTOP and measured runtime |

Separate design qualification from fast production screening. Production records should identify serial/board revision, BOM variant, firmware hash, fixture/instrument calibration and measured pass/fail limits. ERC/DRC are design checks, not substitutes for these measurements.
