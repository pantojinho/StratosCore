# Rev A concurrency and resource contract (SYS-03)

Status: pre-Astra engineering contract. This document converts the accepted resource map and current subsystem parameters into calculable bounds and a post-PCBA stress procedure. It is not a firmware implementation, timing qualification, or change to a locked decision. **Derived** values below are arithmetic from documented inputs. **Candidate** limits are proposed acceptance criteria for review. **TBD** means the exact implementation, manufacturer limit, or measured result is still needed. No board-level result is claimed.

## Baseline and ownership

The ESP32-S3 owns UI/display/touch, GNSS, sensors, LoRa, storage, PDM audio, profiles and networking. The RP2040 independently captures and frames ADS-B timing data, then reports validated records and health over a dedicated UART. Acquisition and peripheral drivers must not depend on UI/network progress. A single ESP32 storage owner serializes microSD access. Each queue is bounded and exposes high-water, overflow/drop and age counters; full queues must cause a declared drop/degradation policy, not an unbounded wait or reset of unrelated services.

| Resource / signal | Current allocation | Contract |
| --- | --- | --- |
| Shared SPI host | GPIO11 MOSI, GPIO12 SCLK, GPIO13 MISO; LCD_CS GPIO10, SD_CS GPIO14, SX1262_NSS GPIO9 | One owner/arbitrator; one selected CS at a time. Transactions are bounded. Restore device mode/clock/format at each acquisition. Never wait on radio BUSY while holding the host. |
| SX1262 service | BUSY GPIO6, DIO1 GPIO5 | ISR records timestamp/status and wakes radio task. Radio commands and status reads wait for bus ownership only in bounded chunks. Never defer DIO1 service behind a full-frame LCD or unbounded SD operation. Semtech-specific maximum service latency: **TBD** from selected datasheet/application and firmware behavior. |
| LCD | Three-line serial candidate, GPIO8 reserved; 320 x 240; display serial clock <=15.15 MHz; ninth bit carries command/data | Partial rectangles only during concurrent radio service. Full refresh is a bulk operation and must yield between bounded chunks. Three-wire branch needs its specified 3.3-to-1.8 V translation; do not translate the shared bus wholesale. |
| microSD | Shared SPI, SD_CS GPIO14; card detect through expander; switched `3V3_SD` | One task owns initialization and writes. Card busy/program time is not bus ownership: release SPI after each bounded command/data transaction, poll readiness later, and honor card protocol state. Graceful stop/quiesce before power removal where possible; after power loss/remount perform fresh initialization. |
| RP2040 ADS-B UART | GPIO43/44 TX/RX and GPIO41/42 RTS/CTS; 921600 baud, 8N1 candidate | Dedicated UART; framing, sequence, CRC, overflow and timestamp counters are mandatory. ESP32 UI, SD and Wi-Fi may not block UART draining beyond the receive-buffer budget. RP2040 PIO/DMA and silicon timing are not yet implemented or proven. |
| GNSS UART | GPIO17 host TX -> module RXD; GPIO18 host RX <- module TXD; MAX-M10S-00B | 9600 baud 8N1 at boot, proposed change to 115200 after identity/acknowledged configuration; no hardware flow control. Bound enabled messages to available bandwidth and drain continuously. |
| GNSS PPS | GPIO21 input | Default 1 pulse/s; qualify using GNSS time-valid state before UTC discipline. Preserve monotonic host time on reacquisition. Probe and GPIO must remain high impedance during GNSS startup. |
| PDM microphone | GPIO15 clock, GPIO16 data; T5838 candidate through TXU0202 | High-quality clock must remain within 2.0–3.7 MHz; documented proposed selectable rates include 2.048/3.072/3.2544 MHz class. Capture in hardware/DMA or equivalent bounded mechanism; no per-bit CPU service. Audio is optional and may be disabled by profile. |
| Native USB | GPIO19/20 D-/D+ | Reserved for native USB and local program/recovery/data use. Do not remap. USB traffic class, endpoint allocation and concurrent throughput requirement: **TBD**. USB console is the console path; do not consume UART0 for a permanent console. |
| Other direct interrupts | Touch GPIO4; expansion GPIO38; ICM-42688 INT1 GPIO47; buttons GPIO0/48 | ISR work is timestamp/acknowledge/queue only; defer protocol or rendering work. Touch/IMU service rates and maximum interrupt masking time: **TBD** from selected configuration and measured scheduler/driver behavior. Slow reset/enable/card-detect/status stays on TCA9535 and is not a timing-critical safety path. |
| Shared I2C (context) | GPIO1/2, 100 kHz accepted | Keep out of hard real-time paths. Existing bus contract uses 2.2 kOhm preferred pulls and <=150 pF expansion cable reserve. Stuck-bus recovery may pulse SCL up to nine times; do not invoke synchronously from a radio/audio ISR. |

Pin names and assignments are from [INTERFACE_GPIO_MAP.md](INTERFACE_GPIO_MAP.md). System ownership is from [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md). Acceptance still depends on the off-state/boot and independent system review gates; this document does not release schematic circuits.

## Pre-Astra quantitative bounds

### Shared SPI

The exact common SPI frequency is not frozen. LCD evidence gives an upper serial clock of 15.15 MHz, not a guaranteed bus setting for all three devices. Final shared frequency must be no greater than the lowest validated limit of the LCD translator/display, SX1262, SD card and MCU configuration, including signal-integrity margin. SD and SX1262 exact operating clock choices and mode are **TBD** in their circuit/application reviews.

For the planning calculation only, assume RGB565 (2 bytes/pixel) and that each data byte uses the display's ninth command/data bit. This is a labeled wire-time model; final pixel format and transfer behavior must be confirmed against the controlled display interface and driver.

* Full active image payload = 320 x 240 x 2 = **153,600 pixel bytes**.
* At nine serial bits per byte, payload clocks = 153,600 x 9 = **1,382,400 clocks**.
* At the display's documented maximum 15.15 MHz, ideal wire time = 1,382,400 / 15,150,000 = **91.25 ms**, excluding commands, gaps, DMA setup and scheduling. This is an optimistic floor, not a frame-rate promise.
* A 320 x 1 RGB565 row is 5,760 clocks, or **0.380 ms** at 15.15 MHz. An `H`-row chunk takes `0.380 x H ms` at this clock before overhead. At another bus clock `fSPI`, use `t = pixels x 18 / fSPI` seconds.

Therefore full-frame LCD writes cannot be treated as atomic under concurrent radio service. Drivers must send partial rectangles in chunks, yield after each chunk, and allow the radio task between chunks. Choose and record the maximum display chunk only after obtaining the SX1262 deadline and the actual shared clock. The enforceable relation is:

`T_SPI_BLOCK = (chunk wire bits / measured SPI bit rate) + measured acquisition/setup overhead`

`T_SPI_BLOCK + worst scheduler/ISR delay < SX1262 maximum service latency`

The numerical right-hand side, target margin, and resulting maximum bytes/chunk are **TBD**. Similarly, SD wire-time is `8 x bytes / fSPI` plus framing; SD internal busy time is device/card dependent and must never be spent holding the bus. Until the measured bounds are populated, a valid concurrency claim cannot be made.

### RP2040 UART and ADS-B load

8N1 spends ten wire bits per payload byte. At 921,600 baud the ideal byte ceiling is 921,600 / 10 = **92,160 B/s** (92.16 kB/s decimal), before framing gaps and software overhead. The architecture's documented sizing scenario is 1,000 records/s x 40 bytes = **40,000 B/s**, which occupies 400,000 / 921,600 = **43.4%** of the line and leaves 52,160 B/s ideal residual capacity. This is a sizing scenario, not a traffic forecast or measured throughput.

The repository's host record format adds 12 bytes of framing around a payload (2 sync + 8 fixed header bytes after sync + 2 CRC); a 14-byte raw contact plus 2 metadata bytes is a **28-byte** record, and a 7-byte contact plus metadata is **21 bytes**. The existing 40-byte/sizing case is more conservative than these contact records, while health/control bursts and future payload changes still require measurement. At 1,000 maximum-length contact records/s, the current framing layout is 28,000 B/s, or 30.4% ideal UART line occupancy. Do not replace the 40 kB/s stress case with that lower calculated figure.

For an input rate `R` bytes/s and a host UART service blackout `T` seconds, minimum buffering before headroom is `B >= R x T`; at the documented scenario, every 1 ms of blackout accumulates **40 bytes**, every 10 ms **400 bytes**, and every 100 ms **4,000 bytes**. Actual ESP32 UART FIFO/DMA/ring capacities and RTS/CTS reaction bytes are **TBD** and must be measured/configured. Require zero unexplained sequence gaps and zero RP2040 overflow counts during nominal stress; injected overload must produce explicit overflow counters while acquisition continues.

The RP2040 sample clock is 8 MHz. A 32-bit timestamp wraps after 2^32 / 8,000,000 = **536.87 s (8 min 56.9 s)**; the protocol already calls for a wrap record at startup and each wrap. ESP32 timestamp reconstruction must remain strictly monotonic across wrap records and UART resynchronization.

### GNSS UART and PPS

At 8N1, the module's boot rate of 9600 baud has an ideal ceiling of **960 B/s**; the proposed 115200 baud rate has **11,520 B/s**. Both are full-duplex capacities in each direction. MAX-M10S supports 9600–921600 baud and has no UART flow control. Therefore the configured output-message set, worst burst and receive ring must be matched explicitly; receiver output bytes/s and burst size are **TBD**. The startup baud switch requires identity/acknowledgement, host rate change and the documented approximately 100 ms transition delay. PPS default is 1 Hz (configurable 0.25 Hz–10 MHz); product time discipline uses the default unless a reviewed requirement changes it.

### PDM, USB, and interrupt load

The T5838 high-quality PDM clock contributes **2.0–3.7 million clock cycles/s** and one data bit per PDM clock at its device interface. This is not equivalent to CPU interrupts per bit: capture must be handled by the selected ESP32 peripheral/DMA path. Audio sample representation, decimation, buffer period/size, memory placement, CPU budget and timestamp mapping are **TBD**. For a buffer holding `N` captured bits at clock `fPDM`, the fill interval is `N/fPDM`; require the worst-case consumer blackout to stay below that interval with documented queue headroom. Audio off mode must stop the clock before disabling its switched domain as specified by the audio contract.

USB data is native and the pins are reserved, but no documented workload or board-level endpoint-throughput target is available in the current baseline. Quantify local programming/recovery and any runtime USB traffic before claiming concurrent USB plus CPU/RF/logging throughput. Do not infer an end-to-end data rate from the connector or MCU capability alone.

Direct ISR arrival frequency and hard deadlines for SX1262 DIO1, ICM-42688, touch, PPS and expansion are configuration-dependent. ISR maximum execution time, maximum global interrupt masking time, priority/nesting policy and worst scheduler latency are all **TBD** until implementation and hardware measurements. Minimum implementation contract: ISR does no SPI transaction, SD operation, allocation, logging-format conversion, display work, or blocking lock acquisition; it captures a monotonic timestamp/status, posts to a bounded queue/notification, and exits. PPS timestamps and radio event timestamps must be captured before deferred task scheduling.

## Firmware scheduling and queue contract

1. Use separate acquisition/service tasks or equivalent bounded work loops for the SX1262, RP2040 UART, GNSS UART/PPS, ICM interrupt, PDM capture/consumer, display and storage. Final priorities and cores are implementation choices; record them in firmware documentation before claiming a timing result.
2. Interrupt handlers are short and nonblocking. Every queue has a declared capacity in entries/bytes, producer/consumer ownership, overflow counter and full policy. No producer may wait indefinitely for UI, network, SD-card-ready, or another queue.
3. The display refresh task submits partial rectangles only and yields after the maximum reviewed SPI chunk. Storage batches records but bounds each bus transaction; it must release SPI while waiting for card ready/program completion.
4. Radio state changes, IRQ status and any required receive FIFO reads take precedence at the next SPI arbitration point. Never wait for SX1262 BUSY under SPI ownership. The radio's measured and manufacturer-derived latency requirement must be added to this document before selecting the SPI chunk limit.
5. RP UART draining, PDM DMA servicing, PPS capture and IMU timestamping remain independent of display and storage task progress. USB/network work must not mask interrupts or hold shared peripheral locks for unbounded periods.
6. Every stream carries monotonic capture time or a documented clock mapping, validity, and loss counters. GNSS UTC only disciplines a separate mapping; it does not step monotonic time. ADS-B sequence/CRC/overflow and 8 MHz wrap records remain authoritative for transport integrity.
7. Runtime profiles may disable audio and ADS-B as already specified. Mandatory microSD logging must report card absent/full/failure explicitly; no promise of zero data loss through arbitrary power failure is made.

## Post-PCBA stress and acceptance procedure

Run only after schematic/layout/assembly reviews and electrical safety gates permit energizing the prototype. Use a logic analyzer on SPI SCLK/MOSI/MISO/CS lines, SX1262 DIO1/BUSY, RP UART+RTS/CTS, GNSS UART/PPS, PDM clock/data, ICM interrupt, USB activity where instrumentable, and a common timing marker. Record firmware build/configuration, card make/model/capacity, radio mode, display refresh pattern, audio state, USB host workload, supply/charging state, timestamps, queue high-water marks and all error counters. Test at room conditions first; broader temperature/supply corners belong to their subsystem qualification plans.

| Test | Stimulus | Measurable acceptance |
| --- | --- | --- |
| SPI exclusivity / mode restoration | Alternate display rectangles, SD reads/writes/remounts and SX1262 commands/RX events. Capture all CS and clock edges. | Never more than one CS asserted; mode/frequency match the current device on every acquisition; no malformed transaction after a device switch. Observed maximum SPI hold time <= recorded chunk bound. |
| Radio priority under SPI contention | Generate the maximum supported display rectangle pattern and sustained SD write/read traffic while repeatedly producing SX1262 IRQ activity into a conducted load/shielded setup; do not radiate unauthorized TX. | DIO1-to-required-status/FIFO-service latency stays below the manufacturer-derived deadline with the predeclared margin; zero unexplained IRQ loss, RX FIFO overrun or radio reset. Numeric deadline/margin must be entered before this test. |
| LCD/SD blocking envelope | Sweep candidate display chunk sizes and SPI clock; include card busy periods and card removal/full conditions. | Determine and log min/median/p99/max blocking time, throughput and radio latency. Select the largest chunk that retains the accepted radio margin. Card busy wait must show bus released. |
| RP2040 link sustained and burst stress | Drive the documented 1,000 x 40-byte/s 40 kB/s scenario for at least 30 min, then use the highest supported burst pattern and intentional host stalls. Run with concurrent LCD, SD, GNSS, Wi-Fi if enabled, audio and USB workload. | At nominal 40 kB/s: zero unexplained sequence gaps, CRC errors, host overruns or RP2040 overflow counts; monotonic reconstructed timestamp including a forced/long-duration wrap test. During intentional overload/stall: explicit counts, bounded memory, acquisition continues and parser resynchronizes. Record line utilization, RTS/CTS reaction and ring high-water. |
| GNSS bandwidth / PPS | Enable the final message set at the proposed 115200 baud; include cold-start 9600-to-115200 reconfiguration, maximum output burst and concurrent UART/SPI load. Observe PPS against a reference timebase. | No UART overrun or missing acknowledged configuration; measured peak bytes/s fits the ring and line budget. PPS capture remains monotonic and time-valid gating works. Accuracy/uncertainty acceptance is **TBD** in GNSS review; do not claim timing accuracy from this test alone. |
| PDM capture coexistence | Capture at selected high-quality clock with audio logging enabled while SPI contention, UART streams, GNSS/PPS and optional USB/Wi-Fi are active; then disable/re-enable audio repeatedly. | No unreported DMA/ring overflow; dropped audio blocks carry counters/timestamps; clock remains in 2.0–3.7 MHz; audio off sequence stops clock before domain-off and recovers without disturbing shared SPI or RF. Required audio loss/latency tolerance is **TBD**. |
| Direct interrupt latency and load | Toggle/generate each interrupt source at its configured operating rate, simultaneous where possible. Measure pin edge to ISR marker and deferred-service completion. | Report min/median/p99/max per source, ISR execution time, max interrupt masking and scheduler delay. SX1262 meets its separate deadline; other limits remain **TBD** until each subsystem sets them. No ISR blocks on a lock or performs bus/storage work. |
| USB and system-profile concurrency | Local flash/recovery session and declared runtime USB transfer workload; run DESKTOP and FLIGHT profile combinations including charging per D21. | USB enumeration/recovery remains available; no unexplained reset, UART/SPI loss, queue overflow or peripheral fault. USB throughput target and allowable interference are **TBD** before qualification. |
| Long mixed soak | At least 8 hours using documented primary portable profile, SD logging active, GNSS/sensors active, ADS-B active for FLIGHT, display at declared brightness, and audio at its declared optional state. Also run DESKTOP charging profile separately. | No deadlock or unexplained reboot; every queue/counter bounded and reviewed; timestamps remain monotonic; all card/radio/audio/transport errors visible. Runtime, ADS-B performance and power acceptance are judged by their own requirements; this test does not manufacture those results. |

For each test save raw analyzer captures or machine-readable timing logs, test configuration and a concise report under the project's test-results location selected by the integrator. Do not write measured results into this pre-Astra contract until actually observed and reviewed. Failed limits require a documented root cause and a new measured run after correction.

## Open values required before a numerical concurrency pass

* Final shared SPI clock/mode and per-device timing after exact component/application and translator review.
* SX1262 DIO1 event/service deadline, BUSY handling and receive FIFO constraints from the exact Semtech datasheet/reference configuration.
* Maximum SPI transaction/chunk size from the radio deadline and measured arbitration/setup/scheduler overhead.
* SD card protocol clock, selected card qualification set, busy-time envelope and measured write burst/insertion behavior.
* ESP32 UART hardware/DMA/ring capacities, RTS/CTS threshold/reaction behavior, and maximum supported RP2040 burst.
* Configured GNSS message set/rates and measured peak output volume; PPS uncertainty acceptance.
* PDM capture peripheral/format, DMA buffer sizes, audio loss tolerance, CPU/memory budget and timestamp mapping.
* USB runtime data use and interference/throughput target.
* Sensor sampling/interrupt rates, global interrupt masking limit, task priorities, core placement and worst-case scheduling latency.

These are review/implementation gates, not reasons to infer new locked requirements. The numerical measurements belong after PCBA; pre-Astra work can close exact datasheet constraints and specify the executable fixture.

## Source record

Reviewed 2026-09-22 from project-controlled material:

* [INTERFACE_GPIO_MAP.md](INTERFACE_GPIO_MAP.md): ESP32 GPIO map, shared-SPI rules, 921600 UART/8N1, 40 kB/s reference scenario, direct interrupt allocation.
* [ADSB_ARCHITECTURE.md](ADSB_ARCHITECTURE.md): 1,000 records/s x 40 B/s sizing arithmetic, 8 MHz sample clock and 56/112-bit frame model.
* [firmware/rp2040_adsb/tools/framing.py](../firmware/rp2040_adsb/tools/framing.py): current host record fields, CRC and wrap semantics; explicitly not PIO/DMA/silicon evidence.
* [GNSS_ARCHITECTURE.md](GNSS_ARCHITECTURE.md) and [COMPONENT_EVIDENCE.md](COMPONENT_EVIDENCE.md): MAX-M10S UART range/default, no flow control, proposed 115200, PPS output and startup sequence.
* [AUDIO_ARCHITECTURE.md](AUDIO_ARCHITECTURE.md): T5838 high-quality PDM range/current and proposed clock rates.
* [hardware/datasheets/README.md](../hardware/datasheets/README.md): exact display serial ceiling of 15.15 MHz and candidate status.
* [PRODUCT_REQUIREMENTS.md](PRODUCT_REQUIREMENTS.md): use profiles, optional audio, mandatory logging, 8-hour portable-runtime target, and USB-charging operation.

No external values or benchmark results were introduced by this contract. Revisit source revisions and exact MPN parameters during the final application review.
