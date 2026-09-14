# USB-C and expansion connector architecture

Status: preferred orderable candidates selected for independent CAD and application review. This document does not release a footprint or a complete USB input circuit.

## USB-C receptacle

Use GCT `USB4105-GF-A` as the preferred Rev A receptacle candidate. It is a top-mount, right-angle USB 2.0 Type-C receptacle with 16 functional contacts, through-hole shell stakes and a published 20,000-cycle durability rating. GCT rates the VBUS contacts collectively at 5 A and the other signal contacts at 0.25 A each. Those connector ratings do not authorize a 5 A input policy: StratosCore remains a fixed USB sink, uses no USB PD and limits charger input to the source-current class validly reported by the reviewed CC circuit.

The manufacturer drawing defines the pad geometry, contact numbering, board edge and shell features. A second person must transcribe and compare the project footprint against drawing revision B4 before KiCad release. The manufacturer's downloadable third-party CAD is reference material only and is not accepted without that comparison.

### Signal ownership

| Connector signals | Destination | Gate before schematic commitment |
| --- | --- | --- |
| A6/B6 D+ and A7/B7 D- | ESP32-S3 native USB, with duplicated receptacle contacts joined as required by USB Type-C | Verify routing topology, series elements if required by the Espressif reference, ESD placement and 90-ohm differential geometry on the selected stackup |
| A5 CC1 and B5 CC2 | `TUSB320LAIRWBR` fixed-UFP candidate | Verify TI fixed-UFP application, orientation/current reporting, unattached behavior and every unpowered/back-power state |
| A4/A9/B4/B9 VBUS | 5 V input protection and `BQ25887RGER` charger path | Close fuse/current limiting, surge/ESD, inrush, discharge, reverse current, connector temperature and charge-while-operating behavior |
| A1/A12/B1/B12 GND | System ground at the connector entry | Review return-current and protection-current paths |
| Shell stakes | Chassis/ground treatment TBD | Select direct, RC or other treatment only after enclosure/ESD review |

## USB signal ESD

Use TI `TPD4E05U06DQARG4` as the preferred four-channel signal-protection candidate for D+, D-, CC1 and CC2. TI lists it active in the 10-pin DQA USON package with 5.5 V working voltage, 0.5 pF typical channel capacitance and IEC 61000-4-2 contact protection of +/-12 kV. Place it at the receptacle with short strike-current paths and straight-through data routing. It protects the four signal conductors only; VBUS protection remains a separate open circuit.

Independent review must verify the DQA pin map and land pattern, confirm CC compatibility with the selected controller, and check that the layout does not add stubs or force USB current through digital ground paths.

## Expansion connector

Use the JST GH family as the preferred expansion connection and `BM12B-GHS-TBT` as the 12-position, right-angle SMT board-header candidate. The matching housing candidate is `GHR-12V-S`, and JST lists `SSHL-002T-P0.2` as the family crimp-contact candidate. The exact wire gauge and finished cable assembly remain open until the current drawings and required cable current are reviewed. JST specifies the family at 1.25 mm pitch, 1 A per contact with AWG 26, 50 V and -40 to +105 degrees C; its listed conductor range is AWG 30-26. Actual rail limits will be lower and must be documented on the enclosure and interface specification.

Candidate pin allocation, subject to footprint orientation and system-level electrical review:

| Pin | Signal | Notes |
| ---: | --- | --- |
| 1 | GND | Ground adjacent to the supply entry |
| 2 | 3V3_EXP | Current-limited or switchable 3.3 V; final limit TBD |
| 3 | I2C_SDA | Shared sensor bus; external capacitance budget required |
| 4 | I2C_SCL | Shared sensor bus; pullups remain on the main board |
| 5 | SPI_SCLK | Shared expansion SPI clock |
| 6 | GND | Return between clock and data group |
| 7 | SPI_MOSI | Shared expansion SPI controller output |
| 8 | SPI_MISO | Shared expansion SPI controller input |
| 9 | EXP_CS | Dedicated active-low chip select |
| 10 | EXP_UART_TX | StratosCore transmit output |
| 11 | EXP_UART_RX | StratosCore receive input |
| 12 | EXP_IRQ | Dedicated interrupt/GPIO input candidate |

No 5 V output is assigned. Adding it would need a recorded decision, current limiting and unpowered-state review. The final cable pin numbering must be checked from both mating faces to prevent a mirrored harness.

## Remaining release gates

- independently compare the USB4105 and BM12B project footprints with their current manufacturer drawings;
- close VBUS fuse/current limiting, surge/ESD, inrush, discharge and reverse-current behavior;
- prove USB attach, orientation, enumeration, source-current limiting and cable-removal behavior;
- verify USB differential impedance using the factory stackup;
- select the JST crimp terminal and wire gauge, then define a keyed cable drawing;
- verify expansion bus capacitance, external load current, hot-plug policy, ESD and back-power behavior;
- check connector access, shell stakes, cable bend radius and enclosure clearances with a printed dummy.

## Primary sources

- GCT, [USB4105 product page](https://gct.co/connector/usb4105), [manufacturer drawing revision B4 dated 2023-12-18](https://gct.co/files/drawings/usb4105.pdf), and [product specification](https://gct.co/files/specs/usb4105-spec.pdf), reviewed 2026-09-14.
- Texas Instruments, [TPD4E05U06 exact orderable part and Rev O data sheet](https://www.ti.com/product/TPD4E05U06/part-details/TPD4E05U06DQARG4), reviewed 2026-09-14.
- J.S.T. Mfg., [GH series product index](https://www.jst-mfg.com/product/index.php?lang=2&series=105), including `BM12B-GHS-TBT` and `GHR-12V-S`, reviewed 2026-09-14.

Supplier stock and unit prices are procurement snapshots rather than technical evidence. Recheck exact suffix, packaging and authorized availability before purchase.
