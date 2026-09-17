# ADS-B frontend and RP2040 validation plan

Status: independent Rev A candidate; no ADSBee circuit or source code copied. Review date: 2026-09-11 UTC. Exact-part and bias evidence updated 2026-09-14.

## Candidate signal chain

`1090 MHz antenna -> ESD/bias option -> BLB01 LNA -> TA2003A SAW -> BLB01 LNA -> TA2003A SAW -> ADL5513 log detector -> MCP6566 comparator -> RP2040 PIO/DMA`

| Part | Evidence and role | Planning contribution |
| --- | --- | --- |
| BeRex `BLB01`, two | 500-1500 MHz internally matched 50-ohm GaAs E-pHEMT LNA in a DFN-8 2 x 2 mm package; datasheet V6.6 documents Id at Vd = 3.0 V as 22/27/32 mA (min/typ/max), gain 21/22.5 dB, NF 0.43/0.63 dB, and a 100 pF/12 pF/12 pF/100 pF 0603 evaluation BOM | About 34 dB gross gain and 0.162 W for two stages at the documented 27 mA typical current. The manufacturer evaluation circuit shows no discrete RF matching network, but bias, decoupling, layout and board-level S-parameter verification remain design work |
| TAI-SAW `TA2003A`, two | 1090 MHz SAW (datasheet Rev 1.0): Fc 1090 MHz, insertion loss 3.2/4.0 dB typical/maximum in 1087-1093 MHz, VSWR 2.4 maximum, stopband 45-62 dB typical across DC-970 MHz, 1046 MHz and 1150-1300 MHz regions | Up to 8 dB cascaded in-band loss; first-stage placement chosen to preserve noise figure while limiting blockers |
| ADI `ADL5513ACPZ-R7` | 1 MHz-4 GHz log detector, -70 dBm sensitivity, 20/21 ns pulse response, 31 mA | Better current product/cost evidence than AD8313; roughly 0.102 W at 3.3 V |
| Microchip `MCP6566` | 1.8-5.5 V open-drain comparator, 56 ns typical high-to-low delay at 1.8 V/100 mV overdrive, 4 MHz maximum toggle at 5.5 V; electrical characteristics table: IQ 60/100/130 uA typical/maximum | Adequate on paper for 0.5 us pulse positions; pull-up RC, delay spread and hysteresis need measurement |

MCP6566 ordering-code closure (DS20002143G Rev G, March 2020, Product Identification System page 47; reviewed 2026-09-17): `LT` = 5-lead SC70 (Microchip package drawing C04-2061-LT Rev E), `OT` = 5-lead SOT-23 (drawing C04-2091-OT Rev F), `E` = -40 to +125 °C; there is no "DBV" suffix (that is TI nomenclature). Preferred candidate **`MCP6566T-E/OT`** (SOT-23-5) for Rev A inspectability/rework, consistent with the flash-package philosophy; **`MCP6566T-E/LT`** (SC70-5) is the smaller alternative, and `MCP6566RT-E/OT` / `MCP6566UT-E/OT` are pin-map routing conveniences (same die, SOT-23 only). Final base-vs-R-vs-U choice is a layout routing input; distributor stock recheck at purchase. The open-drain output may be pulled above VDD (abs max VSS + 10.5 V, section 1.1 note 4), so the comparator can run from the 3.0 V ADS-B quiet rail with its output pulled directly to the RP2040 3.3 V bank — no level translator in the pulse path. Hysteresis is 1.0-5.0 mV internal; the pull-up value (starting point 1-10 kΩ) remains a bench measurement gate.

The two-stage arithmetic suggests the detector can see roughly -96 dBm at the antenna after a conservative 26 dB net gain. This is a screening estimate, not a receiver sensitivity claim. The 1090 MHz S-parameter check on the selected production stack remains a design and prototype RF review item, including the BLB01 bias network, decoupling, launches and interstage paths.

Primary sources: [BeRex BLB01 data sheet V6.6](https://documents.berex.com/BLB01-V6.6.pdf), [TAI-SAW TA2003A data sheet Rev 1.0](https://www.taisaw.com/assets/PDF/TA2003A%20_Rev.1.0_.pdf), [ADI ADL5513](https://www.analog.com/en/products/adl5513.html), and [Microchip MCP6566 data sheet DS20002143G](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6566-6R-6U-7-9-1.8V-Low-Power-Open-Drain-Output-Comparator-DS20002143G.pdf).

## Capture proof completed in repository

The clean-room host model in `firmware/rp2040_adsb/tools/validate_capture.py` generates an 8 MHz sampled pulse stream from a known valid 112-bit DF17 frame, finds the standard 8 us preamble, decodes pulse-position bits and checks the Mode S CRC polynomial. Its unit tests cover a valid frame, a corrupted frame and sample-level timing jitter.

The RP2040 UART transport behavior is tested on the host side: `firmware/rp2040_adsb/tools/framing.py` implements length-delimited records (SYNC/version/type/sequence/32-bit sample timestamp/length/payload/CRC16-CCITT) with 20 passing framing tests. They cover fixed payload shapes, 64-bit timestamp reconstruction across the sample-clock wrap, declared overflow plus sequence-gap detection, recovery after garbage/corrupt headers/CRC and a fragmented 200-contact stream. They do not model UART timing, PIO, DMA or sustained silicon throughput; those remain bench gates described in [the GPIO map](INTERFACE_GPIO_MAP.md).

RP2040 implementation target:

- sample/edge timing equivalent to at least 8 samples per microsecond, with PIO clock derived from the ABM8-272-T3 12 MHz reference and its PLL configuration;
- DMA ring with monotonic capture timestamps and explicit overrun counters, emitting OVERFLOW records per the framing contract;
- 56/112-bit length classification and parity status before host transfer;
- 921600 baud UART with RTS/CTS emitting the proven record format; resynchronize on any framing error without dropping the stream;
- no dependency on GPL ADSBee source. The pinned ADSBee design remains architectural research only.

## Prototype measurements required

1. Characterize each RF stage with VNA/spectrum analysis and the chosen JLC stack; verify the two BLB01 stages at the ADL5513 input stay below its compression under strong-blocker conditions.
2. Inject legal laboratory Mode S pulse fixtures through attenuation; sweep input level, threshold, temperature and supply.
3. Measure missed/false frames, pulse-width error, comparator delay distribution and recovery after strong blockers.
4. Stress with display refresh, SD writes, Wi-Fi and permitted LoRa transmissions; record blind intervals and RP2040 FIFO/DMA overflow (the host decoder exposes every declared drop).
5. Do not claim range or sensitivity until a conducted sensitivity curve and repeatable radiated comparison exist.
