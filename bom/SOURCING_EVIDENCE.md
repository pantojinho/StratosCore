# Sourcing evidence register (BOM-02, 2026-09-22)

Purpose: consolidate the **dated** sourcing evidence already recorded in this repository per exact MPN, with the authorized-channel pointer for the purchase-time recheck. **No stock or price figure may be entered without a dated, named-channel snapshot; nothing here authorizes an order.** Automated live stock checks were attempted 2026-09-22 and are not reliable for this workflow: LCSC's public search is JavaScript-rendered (no data without a browser session), and the DigiKey/Mouser APIs require project API keys. The owner's purchase-time check therefore remains the authoritative step, per the standing repo rule that supplier IDs, prices and stock are never fabricated.

Evidence classes used below:

- **SNAPSHOT** — a dated stock/price observation already recorded in a repository document (channel and date named).
- **CHANNEL-ONLY** — authorized channel identified; no dated snapshot exists yet; check at purchase.
- **LOCAL** — owner purchases locally by project decision (cells, D26).

## Locked / preferred MPNs with recorded snapshots

| MPN | Role | Class | Last recorded snapshot (channel, date, source doc) | Purchase recheck |
| --- | --- | --- | --- | --- |
| `MAX-M10S-00B` | GNSS | SNAPSHOT | DigiKey/Mouser comparison reviewed 2026-09-11 in `COMPONENT_EVIDENCE.md`; about USD 9.60 above the rejected ATGM at prototype quantity but broader authorized stock | DigiKey/Mouser/u-blox distributor |
| `SX1262IMLTRT` | LoRa radio | CHANNEL-ONLY (ordering code confirmed 2026-09-14, D05) | none recorded | Mouser/DigiKey/LCSC |
| `BQ25887RGER` | 2S charger | SNAPSHOT | Mouser 7,531 @ USD 5.01; DigiKey 235 @ USD 6.62 (2026-09-13, `DECISIONS.md` P14 record); LCSC no stock same date | Mouser/DigiKey; LCSC was empty |
| `TPS62130ARGTR` | Main buck | CHANNEL-ONLY | none recorded | DigiKey/Mouser/LCSC |
| `TPS7A2030PDBVR` / `TPS7A2018PDBVR` | Quiet 3.0 V / 1.8 V LDOs | CHANNEL-ONLY | none recorded | DigiKey/Mouser/LCSC |
| `TPS22918DBVR` (x3) | Load switches | CHANNEL-ONLY | none recorded | DigiKey/Mouser/LCSC |
| `TPS61169DCKR` | Backlight boost | CHANNEL-ONLY | none recorded | DigiKey/Mouser/LCSC |
| `TPS259474LRPWR` | VBUS eFuse | CHANNEL-ONLY | none recorded (PWR-02 closed its application 2026-09-22) | DigiKey/Mouser/LCSC |
| `TUSB320LAIRWBR` | USB-C CC controller | CHANNEL-ONLY | none recorded (D22 GPIO-mode wiring closed 2026-09-22) | DigiKey/Mouser/LCSC |
| `TPD4E05U06DQARG4` | USB signal ESD | CHANNEL-ONLY | none recorded | DigiKey/Mouser/LCSC |
| `W25Q128JVSIQ` | RP2040 flash | SNAPSHOT | DigiKey 57,555 @ USD 4.21 qty 1 (2026-09-14, `DIGITAL_SUPPORT_REVIEW.md`) | DigiKey/Mouser |
| `ABM8-272-T3` | 12 MHz crystal | SNAPSHOT | DigiKey 29,393 @ USD 0.71 qty 1 (2026-09-14, `DIGITAL_SUPPORT_REVIEW.md`) | DigiKey/Mouser |
| `DM3AT-SF-PEJM5` | microSD socket | SNAPSHOT | DigiKey regional ~29,700 @ ~USD 5.20 qty 1 (2026-09-14, `DIGITAL_SUPPORT_REVIEW.md`) | DigiKey/Mouser |
| `MCP6566T-E/OT` | ADS-B comparator | CHANNEL-ONLY | none recorded (pin map frozen 2026-09-22, PR #142; /LT and R/U alternates share stock pools) | DigiKey/Mouser/LCSC |
| `BLB01` (x2) / `TA2003A` (x2) / `ADL5513ACPZ-R7` | ADS-B RF chain | CHANNEL-ONLY | none recorded (BeRex/TAI-SAW are narrower channels; ADI via DigiKey/Mouser) | BeRex/TAI-SAW distribution; ADI franchised distributors |
| `MMICT5838-00-012` | PDM microphone | SNAPSHOT | DigiKey 73,381 in stock (2026-09-14, `AUDIO_ARCHITECTURE.md`) | DigiKey |
| `TXU0202DCUR` | Level translator | CHANNEL-ONLY | none recorded | DigiKey/Mouser/LCSC |
| `USB4105-GF-A` | USB-C receptacle | CHANNEL-ONLY | none recorded (GCT direct + distis) | GCT/DigiKey/Mouser |
| `BM12B-GHS-TBT` / `GHR-12V-S` / `SSHL-002T-P0.2` | Expansion connector set | CHANNEL-ONLY | none recorded (JST direct + distis) | JST/DigiKey/Mouser |
| `SKSCLCE010` (x2) | Buttons | CHANNEL-ONLY | none recorded (Alps direct + distis; guide-boss `SKSCLDE010` alternate needs its own check) | Alps/DigiKey/Mouser |
| `TCA9535PWR` | I2C expander | CHANNEL-ONLY | none recorded | DigiKey/Mouser/LCSC |
| `TPD1E0B04DPYR` (GNSS feed; + SD/USB ESD arrays) | ESD | CHANNEL-ONLY | none recorded | DigiKey/Mouser/LCSC |
| `FXP611.07.0092C` + `U.FL-R-SMT-1(60)` | GNSS antenna + receptacle | CHANNEL-ONLY | none recorded (Taoglas/Hirose direct + distis) | Taoglas/Hirose/DigiKey |
| `CAB.721` | ADS-B/LoRa SMA pigtail | CHANNEL-ONLY | none recorded | Taoglas |
| `INR-21700-M50A` (matched pair) | Cells | **LOCAL** | Owner purchases locally (D26); Brazilian sourcing evidence remains an engineering input to PWR-01/O05 | local purchase + holder fit check |
| Display `AFY240320A1-2.8INTH-C1` + samples | Display | CHANNEL-ONLY | DigiKey exact-part listing checked 2026-09-14 for price/availability context (`DISPLAY_REQUIREMENTS.md`); two traceable samples are EXT-01 | DigiKey/Orient direct |

## Known TBD-MPN rows (BOM-01 territory, listed for completeness)

The seven `MPN=TBD` planning-BOM rows and the passives baseline remain BOM-01/BOM-03 work after subsystem closure; no sourcing claim is made for them here.

## Rules reaffirmed

1. Every purchase uses the exact ordering code above — suffixes are engineering choices (see MCP6566 pin-map record).
2. Stock/price figures older than 30 days are context, not availability promises; recheck at purchase.
3. New snapshots must carry channel, date and quantity/price exactly as displayed; screenshots or copied numbers without a channel/date do not enter the register.
4. LCSC (assembly house) sourcing is desirable for PCBA pricing but requires a browser-session check or the assembler's own BOM tool at order time.
