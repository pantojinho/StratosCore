# Display interface specification

Locked target: **2.8-inch IPS LCD, 320 x 240, capacitive touch**, portrait and landscape. Exact LCD manufacturer/MPN, controller, touch IC and connector remain TBD. **Do not create a footprint or assign FPC pins until the exact manufacturer's drawings and a sample are verified.**

## Selection evidence

Obtain the complete module outline, active/viewing areas, FPC bend/exit/length, connector mating details and contact orientation, glass/touch stack height, mounting keepouts, supply/logic limits, backlight circuit/current, interface mode and initialization sequence. Confirm controller identity, IPS viewing angles, touch controller interface/address/interrupt/reset, operating temperature, luminance, availability, MOQ, unit cost and replacement policy. Marketplace photos are not evidence of pin compatibility.

SPI is the preferred candidate from the product discussion, subject to actual panel availability and throughput. QSPI or another interface needs a documented bus/pin/driver comparison. 2.4-inch is a later fallback only with substantial dated cost or supply-chain advantage; it is not approved for this baseline.

## Logical host contract (no connector numbering)

| Logical function | Requirement |
| --- | --- |
| Display power and ground | Voltage, sequencing, inrush and sleep leakage from exact panel |
| Pixel transfer / control | Bus type and signals TBD; DMA transfers must coexist with SD/LoRa |
| Reset / optional TE | Reserve only if panel supports and needs them |
| Backlight | Dimming and shutoff; driver topology follows LED string, never assume direct GPIO drive |
| Touch data / clock | I2C candidate; address/voltage and bus loading to verify |
| Touch interrupt / reset | Candidate GPIO budget; polarity and sequencing TBD |

At RGB565, a full 320 x 240 frame is 153,600 bytes. Thirty full frames/s requires 4.608 MB/s, or 36.864 Mbit/s of pixel payload before command overhead and bus gaps. This is a design calculation, not a guaranteed refresh target. Prefer partial updates where useful; assign a refresh/latency requirement after use testing. Two frame buffers occupy 307,200 bytes before UI overhead; PSRAM capacity alone does not establish DMA compatibility.

Firmware abstraction should separate panel driver, touch driver, orientation/coordinate transform, backlight policy and UI. Test all four corners and button access in each supported orientation, sleep/wake and display-off logging. UI capabilities include altitude/vario, weather, GNSS, telemetry/messages, traffic relative to valid ownship, battery and storage health. Do not bind UI layout to legacy 280 x 456 AMOLED assets.

Exit evidence: selected sample, verified drawings, affordable supply path, fit in mechanical stack and acceptable readability/power under FLIGHT conditions. Only then freeze connector and footprint.
