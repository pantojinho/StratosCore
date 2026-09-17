# Digital support parts review

Status: exact engineering candidates reviewed through 2026-09-17. These selections reduce the pre-KiCad queue but remain subject to the recorded footprint/process gates, factory availability and board-level bring-up.

## RP2040 boot flash

`W25Q128JVSIQ` is the preferred RP2040 boot-flash candidate. Raspberry Pi's current *Hardware design with RP2040* uses the Winbond `W25Q128JVS` family in its minimal design, and RP2040 supports up to 16 MB of external QSPI flash. The exact `W25Q128JVSIQ` provides 128 Mbit/16 MB, 2.7-3.6 V operation, industrial -40 to 85 °C rating and an 8-SOIC package. The larger package is deliberate for Rev A inspectability and rework; a smaller suffix would require a separate footprint and availability review.

The project footprint now transcribes Winbond Rev-M package/pin data and `AN0000009` Rev 2.1 copper/stencil geometry. Its corrected 1.90 x 0.80 mm copper and distinct 1.80 x 0.70 mm paste apertures passed an independent dimensional second pass and KiCad 10 export on 2026-09-17. Assembler mask/courtyard approval and boot/reset/program/temperature bring-up remain.

Route the six QSPI signals directly between RP2040 and flash, keep them short, follow the Raspberry Pi reference pullup/decoupling arrangement and expose the documented BOOTSEL recovery path. The final schematic review must confirm the exact Winbond status-register defaults, RP2040 boot-ROM compatibility and maximum XIP clock. Bring-up must prove cold boot, repeated reset, full-image programming, checksum and operation across the accepted temperature and voltage range.

## RP2040 reference clock

`ABM8-272-T3` is the preferred 12 MHz crystal. Raspberry Pi explicitly recommends this exact Abracon part at 3.3 V and documents 30 ppm tolerance/stability, 50 ohm maximum ESR and 10 pF load capacitance. Its reference circuit uses two 15 pF load capacitors and a 1 kohm series damping resistor. Preserve that starting circuit and keep XIN/XOUT traces short and symmetric; any part/value or IOVDD change requires oscillator startup and drive-level requalification.

The project footprint now uses the exact Abracon 1.30 x 0.70 mm lands at X = +/-1.15 mm and Y = +/-0.875 mm; the earlier generic 1.4 x 1.2 mm land was rejected. The 1:1 mask/paste remains an assembler-approved process starting point. This clock is required for deterministic ADS-B capture timing and reliable USB/debug behavior. Test startup at voltage and temperature corners and compare the RP2040 timebase against GNSS PPS before accepting timing performance.

## microSD socket

`DM3AT-SF-PEJM5` is the preferred socket candidate. Hirose's May 2026 DM3 catalog identifies the exact part as an eight-contact, top-board, right-angle SMT, push-push microSD socket with a card-detection switch. The official product page gives a 13.85 x 15.95 mm body, 1.68 mm height, 0.5 A rating, gold-plated contacts and 10,000 mating cycles; official 2D/3D files are available.

Use the already budgeted shared SPI interface for Rev A. Route card detect to a slow I2C-expander input; no safety function depends on it. Add separately selected ESD protection, required SD pullups and a reviewed load switch if power cycling is retained. The exact drawing `0000947170 / EDC-325165-00-00` Rev 4 was compared on 2026-09-15. Electrical contacts, card detect and shell-land placement match. The drawing's C0.15 +/-0.05 terminal feature lies inside the correct rectangular PCB land. The footprint now marks the 11.0 mm operational card envelope, 0.8 mm inward overstroke edge at Y = 8.925, locked edge at Y = 9.725 and ejected edge at Y = 13.725 on `Cmts.User`. The socket must sit at the enclosure edge; assembler paste approval and final enclosure access/clearance remain before KiCad release.

## Availability snapshots

Checked 2026-09-14 for prototype planning only:

| Part | Snapshot | Consequence |
| --- | --- | --- |
| `W25Q128JVSIQ` | DigiKey displayed 57,555 in stock at USD 4.21 quantity one | Strong prototype availability; recheck reel/PCBA sourcing |
| `ABM8-272-T3` | DigiKey displayed 29,393 in stock at USD 0.71 quantity one | Exact Raspberry Pi recommendation remains practical |
| `DM3AT-SF-PEJM5` | DigiKey regional pages displayed about 29,700 in stock and about USD 5.20 quantity one | Mechanically robust but relatively expensive; do not substitute without controlled-drawing review |

Primary evidence: [Raspberry Pi hardware design guide](https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf), [Winbond W25Q128JV Rev M](https://www.winbond.com/resource-files/W25Q128JV%20RevM%2012242024%20Plus.pdf), [Winbond AN0000009 Rev 2.1](https://www.winbond.com/resource-files/AN0000009%20SpiFlash%20PCB%20Layout%20Guideline%20v2.1%2006122020.pdf), [Hirose exact product page](https://www.hirose.com/product/p/CL0609-0031-0-00) and [Hirose DM3 May 2026 catalog](https://www.hirose.com/en/product/document?documentid=D49662_en&documenttype=Catalog&lang=en&series=DM3). Distributor snapshots: [DigiKey flash](https://www.digikey.com/en/products/detail/winbond-electronics/W25Q128JVSIQ/5803943), [DigiKey crystal](https://www.digikey.com/en/products/detail/abracon-llc/ABM8-272-T3/22472366) and [DigiKey socket](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/DM3AT-SF-PEJM5/2533565).

## Related support selections

Preferred candidates for the microphone/translator, USB-C/signal ESD, expansion connector, buttons, slow-control expander and rail regulators are now recorded in [the audio review](AUDIO_ARCHITECTURE.md), [connector review](CONNECTOR_ARCHITECTURE.md), [control-I/O review](CONTROL_IO_REVIEW.md) and [power rail plan](POWER_RAIL_PLAN.md). Their exact footprints, applications and board-level tests remain open. microSD media, USB VBUS protection and several power-safety parts still have no selected MPN.
