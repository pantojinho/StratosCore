# Expansion interface

Logical interface required in Rev A. This table is **not a physical pin order**. Connector family, pitch, orientation, number of ground contacts, ESD parts and GPIO assignment are TBD.

| Signal | Direction at StratosCore | Required behavior |
| --- | --- | --- |
| 3V3 | Power out | Regulated, current budget/current-limit strategy TBD; no external power injection assumed |
| GND | Reference | Return path; multiple ground contacts may be necessary |
| I2C SDA / SCL | Bidirectional | Shared bus candidate; pullup ownership/address conflicts documented |
| SPI MOSI | Out | Host-driven data |
| SPI MISO | In | Peripheral must release line while deselected |
| SPI SCK | Out | Bus speed depends on connector/cable and internal clients |
| SPI CS | Out | Dedicated expansion select with safe inactive reset state |
| UART TX | Out | Board transmit to peripheral receive |
| UART RX | In | Board receive from peripheral transmit |
| GPIO / IRQ | Configurable | Default high impedance; interrupt polarity and wake capability specified later |
| 5V | Optional power out | Only if available, protected and budgeted; not a locked requirement |

Nominal logic domain is 3.3 V, pending exact interface buffer ratings. Do not claim 5 V tolerance. Key or clearly label the connector, protect accessible contacts and prevent an unpowered peripheral from feeding internal rails. Hot-plug capability is unproven and must not be advertised until tested.

The same physical UART cannot simultaneously serve independent GNSS, RP2040 and expansion streams without an explicit transport design. Validate allocation in [system architecture](SYSTEM_ARCHITECTURE.md). Expansion SPI shares a bus only after latency/MISO-release tests; reserve dedicated CS and GPIO/IRQ even with sharing. Consider an isolatable expansion bus if external faults can compromise onboard acquisition.

Before freeze: choose current/cable limits, data speeds, reset states, connector drawing/footprint, addressing policy and GPIO table. Verify reversed connector prevention, short/load faults, clock integrity, reset recovery, and operation while internal SD/radio/display are busy. No promise of Arduino shield or hobby-module pin compatibility.
