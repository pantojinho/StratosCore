# Footprint reviews: RP2040 support and storage parts

Status: reviewed through 2026-09-15. Project-owned footprints for the RP2040 support and storage candidates. Provenance and residual release gates are recorded per part; anything not yet verified against the exact manufacturer drawing is explicitly marked PENDING. Fabrication of unverified dimensions is prohibited by `AGENTS.md`, so this document records source lineage instead of pretending a completed independent transcription.

## Winbond `W25Q128JVSIQ` — boot flash

- **Footprint:** `hardware/footprints/Winbond_W25Q128JVSIQ_SOIC-8_5.3x5.3mm_P1.27mm.kicad_mod`
- **Source lineage:** vendored from the upstream KiCad footprint library `Package_SO.pretty/SOIC-8_5.3x5.3mm_P1.27mm.kicad_mod` (footprint-generator output, JEITA ED-7311-19 variation 08-001-BBA, 208-mil body width). This is the 5.3 x 5.3 mm, 1.27 mm pitch SOIC-8 body family that the Winbond W25Q128JV DTR Rev B datasheet specifies.
- **Key geometry (from the vendored library file):** 8 x SMD rect pads 1.625 x 0.65 mm, X = +/-3.5875 mm, Y pitch 1.905 mm; courtyard 4.65 mm half-span; pin-1 silk triangle.
- **Verdict:** standard library matches the package family; the project owns a vendored copy so PCB data does not depend on external library versions.
- **Remaining:** pad-to-datasheet cross-check against the Winbond package drawing page, and status-register/boot bring-up per [digital support review](DIGITAL_SUPPORT_REVIEW.md) remain PENDING (bring-up is a prototype gate regardless).
- **Supply snapshot:** DigiKey showed 57,555 units at USD 4.21 (quantity 1) on 2026-09-14 (project snapshot; recheck at purchase).

## Abracon `ABM8-272-T3` — 12 MHz RP2040 reference clock

- **Footprint:** `hardware/footprints/Abracon_ABM8-272-T3_Crystal_SMD_3225-4Pin_3.2x2.5mm.kicad_mod`
- **Controlling sources:** exact-MPN Abracon source-control drawing `456603 Rev B`, dated 2024-09-16, for part identity/package/electrical data, plus the official ABM8 series sheet revised 2020-07-29 for the recommended land pattern. The previous TXC-derived generic KiCad land is no longer the project geometry.
- **Manufacturer land:** four rectangular 1.30 x 0.70 mm lands. Column centers are X = +/-1.15 mm, row centers are Y = +/-0.875 mm, giving a 1.00 mm horizontal inner gap and 1.05 mm vertical inner gap. In the rendered PCB top view pin 1 is lower-left, pin 2 lower-right, pin 3 upper-right and pin 4 upper-left; the CAD pin-1 mark is explicit because package chamfers must not be used as an electrical-numbering inference.
- **Paste/mask boundary:** 1:1 paste and mask are a project process starting point, not a manufacturer stencil recommendation. The PCBA assembler must approve mask expansion, apertures and stencil thickness before release.
- **Independent second pass:** review on 2026-09-15 rejected the old 1.4 x 1.2 mm generic pads, confirmed the exact manufacturer geometry above and found no remaining dimensional conflict in the corrected candidate. KiCad parsing/export and the geometry audit are required below.
- **Application context:** Raspberry Pi's *Hardware design with RP2040* recommends this exact crystal with two 15 pF load capacitors and a 1 kohm series damping resistor; oscillator startup, drive and timebase remain prototype tests.
- **Supply snapshot:** DigiKey showed 29,393 units at USD 0.71 (quantity 1) on 2026-09-14 (project snapshot; recheck at purchase).

## Hirose `DM3AT-SF-PEJM5` — microSD socket

- **Footprint:** `hardware/footprints/Hirose_DM3AT-SF-PEJM5_microSD_HC.kicad_mod`
- **Controlling source:** exact Hirose drawing `0000947170 / EDC-325165-00-00`, revision 4, dated 2026-08-01, for `DM3AT-SF-PEJM5`; the earlier download identifier 44099 is obsolete.
- **Key geometry:** the independent 2026-09-15 comparison confirmed pads 1-8, card-detect pads 9-10, four shell lands, top-board orientation and electrical pin mapping against the exact drawing.
- **Mechanical/process result:** the drawing's C0.15 +/-0.05 callout is a connector-terminal feature inside the rectangular 1.3 x 1.9 mm recommended PCB land, so the PCB pad remains rectangular. The footprint now records the 11.0 mm card width at X = -5.925..+5.075, the 0.8 mm inward overstroke edge at Y = 8.925, locked front edge at Y = 9.725 and ejected front edge at Y = 13.725 on `Cmts.User`. Paste remains a 1:1 project starting point; the drawing calls out a 0.12 mm stencil but does not authorize a different aperture.
- **Verdict:** electrical lands/pin map and the operational card envelope are dimensionally reviewed. Assembler paste approval, final enclosure clearance/access and board-level ESD/power-fail testing keep this footprint gated.
- **Supply snapshot:** DigiKey regional pages showed about 29,700 units at about USD 5.20 (quantity 1) on 2026-09-14 (project snapshot; recheck at purchase).

## Process note

Manufacturer drawings control every project-owned footprint. The ABM8 geometry has replaced the earlier generic library land, and the DM3 comparison has identified its remaining shell/mechanical work. The W25Q128 and residual DM3 items remain explicit rather than treating a KiCad library name as manufacturer proof. The sensors/GNSS/RF footprints are covered by [FOOTPRINT_REVIEWS_SENSORS_GNSS.md](FOOTPRINT_REVIEWS_SENSORS_GNSS.md).
