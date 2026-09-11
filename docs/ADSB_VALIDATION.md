# ADS-B frontend and RP2040 validation plan

Status: independent Rev A candidate; no ADSBee circuit or source code copied. Review date: 2026-09-11 UTC.

## Candidate signal chain

`1090 MHz antenna -> ESD/bias option -> BLB01 LNA -> TA2003A SAW -> BLB01 LNA -> TA2003A SAW -> ADL5513 log detector -> MCP6566 comparator -> RP2040 PIO/DMA`

| Part | Evidence and role | Planning contribution |
| --- | --- | --- |
| BeRex `BLB01`, two | 500-1500 MHz LNA; at 3 V the manufacturer publishes about 27 mA, roughly 17 dB gain around the band and sub-1 dB noise figure | About 34 dB gross gain and 0.162 W for two stages; exact 1090 MHz S-parameter simulation required |
| TAI-SAW `TA2003A`, two | 1090 MHz SAW, 1087-1093 MHz passband, 4.0 dB maximum insertion loss, at least 40-45 dB specified rejection in listed blocker regions | Up to 8 dB cascaded in-band loss; first-stage placement chosen to preserve noise figure while limiting blockers |
| ADI `ADL5513ACPZ-R7` | 1 MHz-4 GHz log detector, -70 dBm sensitivity, 20/21 ns pulse response, 31 mA | Better current product/cost evidence than AD8313; roughly 0.102 W at 3.3 V |
| Microchip `MCP6566` | 1.8-5.5 V open-drain comparator, 56 ns typical high-to-low delay at 1.8 V/100 mV overdrive, 4 MHz maximum toggle at 5.5 V | Adequate on paper for 0.5 us pulse positions; pull-up RC, delay spread and hysteresis need measurement |

The two-stage arithmetic suggests the detector can see roughly -96 dBm at the antenna after a conservative 26 dB net gain. This is a screening estimate, not a receiver sensitivity claim. Noise figure, filter mismatch, detector threshold, cable/ESD loss and blocker compression must be simulated and measured.

Primary sources: [BeRex BLB01 data sheet](https://documents.berex.com/BLB01-V6.6.pdf), [TAI-SAW TA2003A data sheet](https://www.taisaw.com/assets/PDF/TA2003A%20_Rev.1.0_.pdf), [ADI ADL5513](https://www.analog.com/en/products/adl5513.html), and [Microchip MCP6566 data sheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6566-6R-6U-7-9-1.8V-Low-Power-Open-Drain-Output-Comparator-DS20002143G.pdf).

## Capture proof completed in repository

The clean-room host model in `firmware/rp2040_adsb/tools/validate_capture.py` generates an 8 MHz sampled pulse stream from a known valid 112-bit DF17 frame, finds the standard 8 us preamble, decodes pulse-position bits and checks the Mode S CRC polynomial. Its unit tests cover a valid frame, a corrupted frame and sample-level timing jitter. This proves the proposed digital contract and test fixture; it does not prove RP2040 PIO timing or analog sensitivity.

RP2040 implementation target:

- sample/edge timing equivalent to at least 8 samples per microsecond, with PIO clock derived from a reviewed 12 MHz reference;
- DMA ring with monotonic capture timestamps and explicit overrun counters;
- 56/112-bit length classification and parity status before host transfer;
- 921600 baud UART with RTS/CTS as the first ESP32 transport, versioned COBS or length-delimited records, CRC and resynchronization;
- no dependency on GPL ADSBee source. The pinned ADSBee design remains architectural research only.

## Prototype measurements required

1. Characterize each RF stage with VNA/spectrum analysis and the chosen JLC stack.
2. Inject legal laboratory Mode S pulse fixtures through attenuation; sweep input level, threshold, temperature and supply.
3. Measure missed/false frames, pulse-width error, comparator delay distribution and recovery after strong blockers.
4. Stress with display refresh, SD writes, Wi-Fi and permitted LoRa transmissions; record blind intervals and RP2040 FIFO/DMA overflow.
5. Do not claim range or sensitivity until a conducted sensitivity curve and repeatable radiated comparison exist.
