# RF connector selection for Rev A

Status: **PROPOSED, not released for KiCad**. Review date: 2026-09-15. This document selects exact connector candidates and mechanical interfaces only. It does not freeze an RF circuit, transmission-line geometry, antenna match, ESD network or PCB footprint.

## Proposed connector set

| Path | PCB connector | External interface | Proposed use |
| --- | --- | --- | --- |
| LoRa 915 MHz class | Hirose `U.FL-R-SMT-1(60)`, HRS `CL0331-0472-2-60` | Taoglas `CAB.721` only when the enclosure needs a user-accessible antenna | Keep the locked U.FL board interface; terminate the optional pigtail in a normal-polarity 50-ohm SMA female bulkhead |
| GNSS L1 | Hirose `U.FL-R-SMT-1(60)`, HRS `CL0331-0472-2-60` | Taoglas `FXP611.07.0092C` plugs directly into the internal U.FL receptacle | First prototype uses the accepted passive antenna proposal with no exposed RF connector and no DC antenna bias |
| ADS-B 1090 MHz | Hirose `U.FL-R-SMT-1(60)`, HRS `CL0331-0472-2-60` | Taoglas `CAB.721` | Put the normal-polarity 50-ohm SMA female bulkhead in the enclosure and keep cable strain off the PCB RF input |

These are preferred candidates pending RF/CAD review. The shared U.FL part reduces the number of PCB footprints and assembly line items. The external LoRa and ADS-B connectors must be clearly labeled and their internal cables identified because they use the same mechanical families but connect to a transmitter and a sensitive receiver, respectively.

## Board receptacle: `U.FL-R-SMT-1(60)`

The exact manufacturer ordering code is Hirose `U.FL-R-SMT-1(60)`, HRS `CL0331-0472-2-60`. Hirose lists it as a sales product, 50 ohms, 8 GHz maximum, VSWR 1.3 maximum, 30 mating/unmating cycles, and 1.9 mm nominal mated height. The receptacle body is about 3.0 x 3.1 x 1.25 mm. The `(60)` suffix is the 4,000-piece reel version at 8 mm tape pitch; it is not a different RF interface.

The exact drawing `0001257918 / EDC-302540-60-80` and catalog were independently compared on 2026-09-15. The project footprint now carries the exact signal/two-ground copper rectangles and separate manufacturer metal-mask apertures. The central callout prohibits a board cut-out; it does not prescribe a copper keepout or a solder-mask opening, so both provisional library features were removed. RF return copper remains a final-layout decision. Final solder-mask/process treatment, stencil compatibility and tool/cable clearance remain assembler/RF/mechanical gates.

The 30-cycle rating makes U.FL an internal assembly/service connection. It is not a user-accessible antenna jack. Production assembly needs the Hirose insertion/extraction tool or a controlled equivalent process, cable slack and strain relief; repeated bench swaps should occur at the external SMA connector.

Primary evidence:

- [Hirose exact product page](https://www.hirose.com/en/product/p/CL0331-0472-2-60), detailed specifications updated 2026-02-07.
- [Hirose U.FL series catalog](https://www.hirose.com/en/product/document?clcode=CL0331-0472-2-60&documentid=ed_U.FL_CAT&documenttype=Catalog&lang=en&productname=U.FL-R-SMT-1%2860%29&series=U.FL), August 2026 edition; receptacle table, recommended PCB/metal-mask pattern, cable ordering and handling/tool sections.

Authorized availability snapshot checked 2026-09-14: Mouser listed 35,073 pieces available, cut-tape quantity one at USD 1.55 and 15-week factory lead time. Stock and price are sourcing evidence only and must be refreshed before purchase. [Mouser exact listing](https://www.mouser.com/en/ProductDetail/Hirose-Connector/U.FL-R-SMT-160?qs=PABxe4V6HDqIFtIEeJcXCQ%3D%3D).

## External SMA pigtail: `CAB.721`

Taoglas `CAB.721` is the preferred enclosure pigtail for ADS-B and the optional LoRa bulkhead. The exact assembly has a right-angle Hirose U.FL plug, 100 mm of 1.32 mm coax and a normal-polarity SMA female bulkhead jack. Taoglas revision E, dated 2024-02-06, specifies nominal 50 +/- 3 ohms, VSWR 1.3 maximum from 0 to 6 GHz and a 105 degrees C cable rating. Both 915 MHz-class LoRa and 1090 MHz ADS-B fall inside the specified range.

The 100 mm cable is a procurement starting point, not a final length. The printed dummy must confirm routing without sharp bends, contact with the 21700 holder, crossing the ESP antenna keepout or pulling on the U.FL plug. The exact panel hole, nut stack, wall-thickness range, cable bend radius and SMA torque must be independently transcribed from the controlled drawing and proven in the enclosure. Taoglas does not state mating-cycle durability in the reviewed exact datasheet; record it as **TBD** instead of assuming a generic SMA value.

Primary evidence:

- [Taoglas exact product page](https://www.taoglas.com/product/cab-721-hirose-u-fl-to-100mm-1-32-to-smafbkst/).
- [Taoglas CAB.721 specification SPE-12-8-103-E](https://www.taoglas.com/datasheets/CAB.721.pdf), revision E, 2024-02-06; cable specification, insertion-loss plot, mechanical drawing and packaging.

Authorized availability snapshot checked 2026-09-14: DigiKey listed the part active with 4,430 assemblies available at USD 5.14 in quantity one and a 16-week manufacturer lead time. Mouser also listed 2,199 available at USD 5.14. Refresh both before the PCBA/mechanical order. [DigiKey exact listing](https://www.digikey.com/en/products/detail/taoglas-limited/CAB-721/3664641), [Mouser exact listing](https://www.mouser.com/en/ProductDetail/Taoglas/CAB.721?qs=%2Fv8iy7V9uix41yCF2gxgAA%3D%3D).

## GNSS prototype interface

The proposed first GNSS prototype does not need a bulkhead adapter. Taoglas `FXP611.07.0092C` already terminates its 92 mm, 1.37 mm cable in an I-PEX MHF I/U.FL-compatible plug and mates to the selected Hirose receptacle. The antenna remains passive, so this interface carries RF only. It does not authorize active-antenna bias, a DC-block topology or surge components.

The antenna is external to the PCB but should normally sit within or directly against the plastic enclosure, with the previously documented 40 x 40 mm reservation and 10 mm clearance from metal/main ground. Exposing the U.FL connection to the user is prohibited by its 30-cycle service rating. A removable external GNSS antenna with an enclosure SMA would require a separate product decision because it changes the antenna, loss, ESD exposure, bias policy and mechanical stack.

Primary evidence:

- [Taoglas FXP611.07.0092C specification SPE-13-8-010-G](https://www.taoglas.com/datasheets/FXP611.07.0092C.pdf), reviewed previously for the 1559-1610 MHz passive antenna, dimensions, cable and connector.
- [Hirose U.FL catalog](https://www.hirose.com/en/product/document?clcode=CL0331-0472-2-60&documentid=ed_U.FL_CAT&documenttype=Catalog&lang=en&productname=U.FL-R-SMT-1%2860%29&series=U.FL), mating-cycle and handling limits.

Authorized availability snapshot checked 2026-09-14: DigiKey listed 2,809 pieces at USD 8.59 in quantity one; Mouser listed 919 at USD 9.16. Refresh at purchase. [DigiKey exact listing](https://www.digikey.com/es/products/detail/taoglas-limited/FXP611-07-0092C/3945623), [Mouser exact listing](https://www.mouser.com/es/ProductDetail/Taoglas/FXP611.07.0092C?qs=RuW%2Fu%252BNMQmvGqLjAtZaGrQ%3D%3D).

## Electrical, firmware and mechanical impact

- **Electrical:** all selected interfaces are nominal 50-ohm RF paths. Their existence does not set the PCB trace width. Each path still needs the final stackup, controlled-impedance calculation, return-via layout, selected ESD parasitics and VNA verification. GNSS remains passive/no-bias under P20. LoRa and ADS-B remain physically and electrically independent.
- **Firmware:** no pin or protocol changes. Firmware must retain region-specific LoRa settings and may need coexistence test modes, but connector selection creates no new bus or GPIO requirement.
- **PCB:** reserve three separate U.FL footprints, tool approach and cable keepouts. Place the ADS-B receptacle next to the first RF stage, the LoRa receptacle beside its final matching/switch network, and the GNSS receptacle beside its protected input. Exact placements wait for RF partition and mechanical review.
- **Enclosure:** two `CAB.721` assemblies would add two SMA bulkheads and two 100 mm cables. Confirm wall thickness, wrench/nut access, bend radius, strain relief, antenna spacing, drop loads and connector labeling with the printed dummy. The GNSS film antenna adds its existing 38 x 37 mm body and 92 mm cable reservation but no SMA bulkhead.
- **Assembly/service:** U.FL is an internal 30-cycle connection. Add cable labels at both ends, record the mating tool/process and prohibit using the U.FL plug as the normal test disconnect. Provide conducted-test access before the enclosure bulkhead where the RF reviewer requires it.

## Remaining release gates

1. RF reviewer accepts the exact `U.FL-R-SMT-1(60)` use for LoRa, GNSS and ADS-B and `CAB.721` for ADS-B plus optional LoRa SMA.
2. Obtain assembler approval for the corrected Hirose copper/mask/paste implementation and confirm the controlled drawing's stencil assumptions; the exact dimensional comparison is complete.
3. Independently transcribe the `CAB.721` bulkhead drawing; confirm panel hole, wall thickness, nut/washer stack, torque, cable exit and actual minimum bend radius with Taoglas.
4. Fit physical samples in the printed enclosure dummy with display, exact holder and both cells installed; verify tool access, strain relief, drop loads and that cables do not cross antenna or magnetic/thermal keepouts.
5. Freeze the factory four-layer stackup, calculate each 50-ohm path and review return-current/via placement. Do not reuse a trace width from another board.
6. Include exact ESD parts in each RF simulation and VNA-check connector-plus-cable insertion/return loss. For ADS-B, verify sensitivity and blocker limits through the complete bulkhead path; for LoRa, verify conducted output/match; for GNSS, compare C/N0 and cold start in both device orientations.
7. Run coexistence tests with LoRa TX, Wi-Fi/BLE, display, SD and charging active. Label the external LoRa and ADS-B ports and the internal pigtails so assembly cannot swap the transmitter and receiver paths.
8. Refresh authorized stock/pricing and obtain the PCBA assembler's confirmation that the selected reel packaging, U.FL placement/tool clearance and any separately installed bulkhead cable are supported.

Until these gates close, the exact parts are suitable for BOM planning and sample procurement only. They do not release a schematic, footprint, RF layout or manufacturing package.
