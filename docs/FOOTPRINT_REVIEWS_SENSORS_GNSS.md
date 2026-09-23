# Footprint reviews: sensors, GNSS and RF parts

Status: sensor-spacing correction reviewed 2026-09-23; other entries retain their dated review scope. This file separates accepted project candidates from examined geometry that is not safe to release. A filename that names an exact component is not evidence that its land pattern matches that component.

## MEMSIC `MMC5983MA` — manufacturer-derived candidate

- **Candidate footprint:** `hardware/footprints/MEMSIC_MMC5983MA_LGA-16_3x3mm_P0.5mm.kicad_mod`.
- **Controlling source:** MEMSIC `MMC5983MA` datasheet Rev A, formal release 2019-04-03, page 20 package drawing and land pattern; official PDF visually reviewed 2026-09-15.
- **Package and pin order:** nominal 3.0 x 3.0 x 1.0 mm 16-LGA. In the manufacturer top view, pin 1 is the top-right terminal; pins 1-4 run right-to-left along the top, 5-8 top-to-bottom on the left, 9-12 left-to-right along the bottom and 13-16 bottom-to-top on the right.
- **Copper:** the manufacturer land is 0.450 x 0.300 mm with 0.500 mm tangential pitch and 2.550 mm opposing row-center spacing (not outside span). Row centers are +/-1.275 mm radially and -0.750, -0.250, 0.250 and 0.750 mm tangentially.
- **Mask and paste boundary:** the exact datasheet supplies the copper land only. The candidate carries coincident 1:1 pad mask/paste as a clearly labeled process starting point; it is not a manufacturer recommendation. The assembler must set final mask expansion, paste aperture and stencil thickness for its process before release.
- **Placement:** preserve magnetic distance from cell cans, ferromagnetic fasteners, speakers, inductors, charger/buck loops and high-current copper. The final layout needs a heading-bias test across charging, pack current and all radio states.
- **Correction 2026-09-23:** the previous independent-review claim was wrong: it treated the 2.550 mm center dimension as an outside span and missed overlapping corner lands. The radial centers are now +/-1.275 mm; copper spans 3.000 mm. Top-view numbering was checked visually against page 20. See the [correction evidence](FOOTPRINT_CORRECTIONS_2026_09_23.md).
- **Validation boundary:** the KiCad-parsed regression check now covers the 16-pad source map, 3.000 mm copper envelope and every pair of copper lands (minimum nominal gap 0.200 mm). **Assembler process approval, final Gerber aperture review and magnetic placement review still gate schematic/PCB release.**

## Bosch `BMP581` — manufacturer-derived candidate

- **Candidate footprint:** `hardware/footprints/Bosch_BMP581_LGA-10_2x2mm.kicad_mod`.
- **Controlling source:** Bosch `BST-BMP581-DS004-13`, revision 1.13, April 2025, Figures 29, 30 and 32 plus Section 8.2; official PDF visually reviewed 2026-09-15.
- **Package and pin order:** nominal 2.0 x 2.0 x 0.80 mm maximum 10-LGA. The manufacturer bottom-view numbering was mirrored into the normal PCB top view: pins 1/2 run down the left, 3-5 left-to-right along the bottom, 6/7 bottom-to-top on the right and 8-10 right-to-left along the top. Pin 1 is at the top-left package corner in top view.
- **Copper:** Bosch expands the 0.250 x 0.275 mm package terminals by 25 micrometers on every side to 0.300 x 0.325 mm lands. Opposite row-center spacing is 1.525 mm (radial centers +/-0.7625 mm), giving 1.850 mm copper extent. The three-pad-row outer-center spacing is 1.000 mm, adjacent pitch is 0.500 mm and the minimum nominal edge gap is 0.200 mm.
- **Mask, paste and keepout:** Figure 32 specifies the 2.200 x 2.200 mm no-mask region and says vias/traces are not recommended under the sensor. The candidate implements that full mask opening and a four-layer 0.875 x 0.875 mm central track/via/pour keepout between the inner land edges. The 1:1 paste apertures are a project starting point because Bosch gives no exact paste aperture in this drawing and warns against excess paste; assembler approval is mandatory.
- **Mechanical boundary:** preserve the top pressure port, keep the sensor clear of coating/adhesive/flux contamination and provide the reviewed static-pressure vent. Final placement must exclude unnecessary under-body routing outside the small enforced central keepout.
- **Correction 2026-09-23:** the previous independent-review claim was wrong: it treated the 1.525 mm center dimension as an outside span and missed 0.0375 mm corner gaps. Copper and matching provisional paste centers are now +/-0.7625 mm. Figure 30 bottom-view pin numbering was mirrored and checked against Figure 29 top-view pin-1 and pressure-port locations. See the [correction evidence](FOOTPRINT_CORRECTIONS_2026_09_23.md).
- **Validation boundary:** the KiCad-parsed regression check covers the ten-pad source map, 1.850 mm copper envelope and every pair of copper lands (minimum nominal gap 0.200 mm). Full-mask-opening/process and under-body routing review remain separate; the regression check does not certify them. **Assembler paste/stencil approval, final DRC/manual confirmation of no unnecessary routing under the complete body and pressure-port/vent review still gate schematic/PCB release.**

## TDK InvenSense `ICM-42688-P` — manufacturer-derived candidate

- **Candidate footprint:** `hardware/footprints/TDK_ICM-42688-P_LGA-14_3x2.5mm_P0.5mm.kicad_mod`.
- **Controlling sources:** DS-000347 v1.9, dated 2024-11-12, Figure 5 and Section 10.2; AN-000393 v2.4, dated 2026-02-09, Sections 2.1-2.4 and Figure 1. Exact PDFs were retrieved from TDK's versioned CloudFront resources and visually reviewed 2026-09-14.
- **Package and pin order:** nominal 3.0 x 2.5 x 0.91 mm body, 14 terminals and 0.5 mm pitch. In the datasheet top view, pins 1-4 run down the left, 5-7 left-to-right along the bottom, 8-11 up the right and 12-14 right-to-left along the top. Pin 1 is the top-left side terminal.
- **Copper:** AN-000393 says LGA land length and width equal the package-terminal length and width. DS-000347 gives nominal 0.475 x 0.25 mm terminals. Left/right row centers are X = +/-1.1625 mm with Y = -0.75, -0.25, 0.25 and 0.75 mm; top/bottom centers are Y = +/-0.9125 mm with X = -0.5, 0 and 0.5 mm.
- **Solder mask:** AN-000393 recommends no solder mask under the package where the board process permits it. The candidate therefore includes a nominal 3.0 x 2.5 mm body opening. The per-pad rule also adds 0.1 mm to both land dimensions as the documented fallback. The assembler must choose and approve the final opening against registration and process capability.
- **Paste:** AN-000393 specifies a 90% stencil-opening-to-land ratio and at least 100 micrometer stencil thickness subject to aspect ratio >= 1.5 and area ratio >= 0.66. The candidate preserves pad aspect ratio and interprets 90% as copper area (linear scale `sqrt(0.90)`). At 100 micrometers the smallest aperture calculates to aspect ratio 2.372 and area ratio 0.777; at 125 micrometers the area ratio is only 0.622. The calculated thickness ceiling is about 117.7 micrometers. The assembler must confirm whether 90% means area or linear dimension and choose a compatible approximately 100 micrometer/step-down process or revise the aperture.
- **Placement/assembly:** a central 1.8 x 1.3 mm rule area blocks traces, vias and copper pours on all four locked copper layers while leaving perimeter fanout possible. Final layout review must confirm that the complete under-body area outside the necessary symmetrical fanout also remains clear. Keep power, charger/DC-DC and high-speed/high-current signals away; place VDD/VDDIO decoupling close; place the sensor on a mechanically stable region away from anchors, board edges, buttons, connectors, speakers and heat sources. Do not snap panel tabs or use ultrasonic cleaning.
- **Independent second pass:** a separate pad-by-pad review on 2026-09-14 found no critical/high mismatch in identity, package, top-view pin order, centers, pitch, copper or per-pad mask expansion. It identified the paste/stencil ambiguity, full-body mask-registration gate, missing keepout and an out-of-courtyard pin-1 marker. The marker and central keepout were corrected; their final parse/audit is recorded below.
- **Validation boundary:** KiCad 10 parses and exports the footprint, and an automated geometry audit passes for 14 numbered lands, 14 paste apertures, pitch, positions, sizes, pin order, 90% paste area, body mask opening and central keepout. **Assembler mask/paste approval and final PCB placement/routing review still gate schematic/PCB release.**
- The upstream KiCad `LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` file remains rejected for this exact part: its embedded source is an STMicroelectronics package and its 0.625 x 0.35 mm pads are larger than the TDK rule.

## u-blox `MAX-M10S-00B` — manufacturer-derived candidate

- **Candidate footprint:** `hardware/footprints/u-blox_MAX-M10S-00B_LCC-18_10.1x9.7mm.kicad_mod`
- **Controlling sources:** MAX-M10S datasheet UBX-20035208 R08 Figures 2/4 and integration manual UBX-20053088 R05 Figure 30/Table 44 plus Figure 31/Table 45, visually reviewed 2026-09-14 from the official u-blox PDFs.
- **Copper and solder mask:** 18 rectangular lands at 1.1 mm pitch. Pads 1/9/10/18 are 0.7 x 1.8 mm; the other pads are 0.8 x 1.8 mm. Land centers are X = -4.4 through +4.4 mm and Y = +/-4.75 mm in the Figure 30 orientation. Copper and mask are coincident, as u-blox requires.
- **Pin order:** Figure 30 puts pin 1 at bottom-left; pins 1-9 run left-to-right on the bottom row and 10-18 run right-to-left on the top row. This was cross-checked against the datasheet top view, which is rotated 90 degrees relative to Figure 30.
- **Paste:** each terminal uses the u-blox T-shaped recommendation. The outer segment is 1.4 mm long at full 0.7/0.8 mm land width; the inner segment is 0.9 mm long at 0.5/0.6 mm width. Outer-to-outer paste span is 12.5 mm and the inner gap is 7.9 mm. The manual recommends a 150 micrometer stencil and says the assembler must adapt the recommendation to its process.
- **Independent second pass:** a separate dimensional review on 2026-09-15 confirmed all 18 copper/mask lands, 1.1 mm pitch, corner/standard pad sizes, row centers, top-view pin order and the exact T-paste dimensions, including the 7.9 mm inner gap and 12.5 mm outside span. It found no electrical or dimensional mismatch. The review moved the two side silk lines clear of the 10.7 mm maximum-width body and added an F.Fab pin-1 chamfer as a CAD convention; the physical module identifies pin 1 with a dot.
- **Mechanical/review boundary:** the 10.1 x 9.7 mm nominal body, 11.1 x 10.1 mm manufacturer keepout and de-paneling-tab warning are recorded. KiCad 10 parses and exports the corrected footprint, and the automated geometry audit passes. **Assembler approval of the 150 micrometer/T-paste process, RF/PDN review and final placement constraints still gate release.**
- A previous SparkFun-derived candidate was rejected and removed because it lacked a direct manufacturer derivation and the prescribed paste pattern.

## Hirose `U.FL-R-SMT-1(60)` — RF receptacles

- **Candidate footprint:** `hardware/footprints/Hirose_U.FL-R-SMT-1_60_Vertical.kicad_mod`
- **Controlling sources:** exact Hirose drawing `0001257918 / EDC-302540-60-80` for ordering variant `(60)` and the U.FL catalog's receptacle/metal-mask page, independently reviewed 2026-09-15.
- **Copper and drawing restriction:** signal pad 1 is a 1.05 x 1.00 mm rectangle centered at (-1.525, 0); the two pad-2 ground lands are 2.20 x 1.05 mm rectangles centered at (0, -1.475) and (0, +1.475). The exact drawing's central callout prohibits a PCB cut-out; it does not prescribe a copper keepout. The earlier library's central F.Mask opening and the provisional F.Cu keepout were therefore removed. Final RF return copper is a layout decision.
- **Metal mask:** separate F.Paste apertures reproduce the exact drawing: 0.85 x 0.80 mm at (-1.525, 0), and 2.00 x 0.90 mm at (0, +/-1.50). The assembler must confirm stencil/process compatibility.
- **Status:** the exact land and paste dimensions plus the board-cut-out restriction completed an independent comparison and the corrected footprint parses in KiCad. RF layout, mask/process approval, insertion/extraction-tool access, cable strain relief and the final mechanical envelope remain mandatory before layout release.

## TI `TPD1E0B04DPYR` — GNSS RF ESD shunt

- **Candidate footprint:** `hardware/footprints/TI_TPD1E0B04DPYR_X1SON-2_DPY0002A.kicad_mod`
- **Controlling source:** TI TPD1E0B04 data sheet Rev C, June 2025, package drawing `4224561/C` dated 2024-07, pages 23-25.
- **Exact geometry:** terminal centers X = +/-0.35 mm; exposed SMD land and 0.10 mm-stencil apertures `0.30 x 0.50 mm`, R0.05. TI prefers solder-mask-defined lands with copper extending at least 0.07 mm under mask on all sides.
- **Review correction 2026-09-17:** corrected the earlier 90-degree pad-axis error. The candidate now uses `0.44 x 0.64 mm` copper with separate `0.30 x 0.50 mm` rounded mask and paste apertures, expands the courtyard beyond maximum body/copper and adds a fab pin-1 index.
- **Independent second pass:** confirmed centers, pin orientation, SMD opening, derived minimum copper overlap, paste, body and courtyard against drawing 4224561/C with no critical/high/medium mismatch; KiCad 10.0.6 export returned success.
- **Status:** exact dimensions passed independent review and the corrected footprint parses/exports in KiCad. Assembler approval of mask registration/web, copper enlargement, paste and courtyard remains mandatory.

## Release boundary

The MMC5983MA, BMP581, ICM-42688-P, MAX-M10S, U.FL and TPD1E0B04 candidate files remain in `hardware/footprints/` from this review. MAX-M10S, U.FL and the corrected TPD1E0B04 have completed dimensional evidence comparisons. None is released for manufacture until the remaining assembler, RF, mechanical and part-specific checks are recorded. The RP2040 support and storage group is covered by [the digital footprint review](FOOTPRINT_REVIEWS_DIGITAL.md).
