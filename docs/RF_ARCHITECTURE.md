# RF architecture before layout

Status: mandatory pre-layout concept; no antenna placement or matching network is frozen. Four independent RF functions must coexist within a very small device.

| System | RF path | Constraints |
| --- | --- | --- |
| Wi-Fi / BLE | ESP32-S3-WROOM-1 module PCB antenna, 2.4 GHz | Preserve exact module antenna keepout in all relevant layers and enclosure materials; no external-antenna module substitution |
| GNSS | P20 passive FXP611/U.FL/TPD1E0B04 proposal for accepted MAX-M10S-00B | Separate no-bias receive path; RF/PDN review, fit, calculated geometry and VNA/coexistence tests remain |
| LoRa | SX1262, reference matching/filter/switch network, U.FL, 915 MHz class antenna | Direct IC integration; oscillator/TCXO and RF switch policy chosen with Semtech reference; region-specific transmission |
| ADS-B | Separate 1090 MHz antenna, preselection, LNA/filtering, detector/comparator, RP2040 | Receiver blocker tolerance and analog bandwidth must be demonstrated; never shared with SX1262 |

Start SX1262 work from [Semtech's SX1262 product/reference-design library](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262), including the 915 MHz-capable SX1262MB1LDCS reference. Select the exact reference revision, RF switch/clock topology and corresponding matching BOM before copying values. Manufacturer references outrank hobby modules. Do not assume a regional development-board frequency/power configuration is lawful everywhere.

For the ESP antenna, use [Espressif hardware layout guidance](https://documentation.espressif.com/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html) and exact module drawings. A nominally isolated corner can still be detuned by the battery can, display metal, screws, hands and SMA pigtails. No universal keepout distance is assigned here.

## Placement and stackup study

First place volume/keepout envelopes for module antenna, display FPC, cell holder, connectors and all RF zones. Keep high-current loops and fast display/SD clocks away from receive inputs and their matching networks. Use short controlled-impedance RF paths over continuous return planes, stitching as determined by RF frequency and geometry, and local decoupling/rail filtering. Shield cans and partitions are options; leave area until coexistence is measured. The current spatial proposal and section view are in [the mechanical/RF floorplan](MECHANICAL_RF_FLOORPLAN.md).

L2 is proposed solid ground. L1 RF referenced to L2 is a starting point. L3 power/signal allocation must also provide coherent return paths for L4 signals; the conceptual stack is not automatically suitable for high-speed routing on every layer. Ask the manufacturer for dielectric thickness, copper, soldermask and impedance capability; calculate 50-ohm geometries from that stack. No trace width is specified before then. See [manufacturing](MANUFACTURING_STRATEGY.md).

## Coexistence tests and remedies

| Aggressor | Victim / observation | Evidence and mitigation candidates |
| --- | --- | --- |
| LoRa TX at allowed power/duty settings | ADS-B compression/packet loss; GNSS C/N0/fix degradation | Sweep channels/power and physical antennas; measure blocking, filtering, shielding, coupling and recovery |
| Wi-Fi traffic / BLE | GNSS, ADS-B; pressure/IMU supply noise | Compare receiver metrics and sensor noise with radios idle/active |
| LCD/SD/USB clocks and DC/DC switching | Receive sensitivity and spurious response | Max refresh/write/charge state, near-field scan, conducted noise checks |
| Battery/holder/magnets/current loops | MMC5983MA heading bias; antenna detuning | Test both cell populations and charge currents, final enclosure and user grip |

Use conducted input first, known ADS-B messages and known GNSS signal/sky conditions, then assembled radiated comparison. Record baseline and delta, not just "works." Simultaneous LoRa TX and reception are not guaranteed. If blanking receivers is necessary, explicitly log blind intervals and evaluate the FLIGHT impact before acceptance.

Power the analog RF path from a domain with noise and headroom verified against selected components. Add low-capacitance ESD appropriate to RF ports; select its parasitics in matching analysis. Reserve instrument access and antenna strain relief. P25 proposes one exact Hirose U.FL receptacle for all three board RF paths and Taoglas CAB.721 for ADS-B plus optional LoRa SMA bulkheads. These remain RF/CAD/test gates as detailed in [RF connector selection](RF_CONNECTOR_SELECTION.md).
