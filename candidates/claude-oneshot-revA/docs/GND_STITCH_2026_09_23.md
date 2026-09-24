# GND stitch session — 2026-09-23 (Hermes, late session)

Closes the three floating GND pads listed in `docs/ISSUES.md` (Digital section)
and integrates the parallel review commit `d88b8a1` correctly.

## What was done

1. **U24.2 (TXU0202 GND)** — 13-segment 0.2 mm track staircase from the pad to
   (5.00, 48.80), 0.45/0.2 via landing on GND fill of In1+In2+B.Cu. DRC-clean
   since first commit (geometry 0.2 mm / clearance 0.127 suffices here).
2. **U2.3 (TPD4E05U06 GND)** — the U2 pad row pocket is closed at 0.15 mm
   clearance (USB90 class neighbors): escape is a single 0.127 mm track to
   (7.17, 71.45) with a 0.35/0.2 via. Minimum foreign-copper distance at the
   via center is 0.330 mm >= 0.175+0.127 needed. DRC-clean.
3. **U3.8 (TPS259474L GND)** — 0.127 mm track staircase west then east to
   (24.30, 75.05) with a 0.35/0.2 via on the In1 plane. This route clears all
   foreign copper; the residual 10 clearance items are chord dips of the
   diagonal BFS staircase near the EFUSE_ILM via (8) and the TP1 VBUS fill
   island (2). Cause analyzed; fix queued (see "Next iteration").
4. **U7 footprint** — the parallel review commit `d88b8a1` carried the correct
   RGT0016C land (SLVSAG7F p.41, EP 1.68 mm) but its board file also carried a
   broken re-route (499 clearance items, sub-minimum track/via/drill classes).
   The footprint block was transplanted alone into the clean board via
   s-expression surgery (`/tmp/merge_u7.py` approach: balanced-paren block
   extraction of `U7` only). RGT0016A residue: none.

## DRC state after this session (kicad-cli 10.0.6, `kicad/reports/drc.json`)

| Check | Before session | After session |
| --- | --- | --- |
| unconnected_items | 5 (3 floating GND + 2 LoRa) | **2 (LoRa RFO/RFI_P TBD only)** |
| shorting_items | 0 | 0 |
| clearance | 0 | 10 (chord dips at U3 east rail + TP1 island) |
| schematic_parity | 0 | 0 |

Remaining non-clearance violations pre-exist: 199 solder_mask_bridge
(assembler gate, ICM/BMP), 117 silk items (cosmetic), 1 track_dangling
(LoRa stub).

## API pitfalls hit (KiCad 10.0.6 swig; confirmed against skill kicad-pcb)

- `GetEffectiveShape(layer)` on a foreign-layer item returns empty geometry —
  silently. Never pass a layer you have not proven the item is on.
- `GetFilledPolysList(layer)` throws `std::out_of_range` (C++, uncatchable)
  when the zone does not span the layer — guard with `GetLayerSet().Contains()`.
- **Zone fill islands inherit the net of the pad that islands them.** The
  "VBUS island" at TP1 is GND fill renamed to VBUS by KiCad; conversely the
  U3 pocket fill is GND but appears foreign to pad U3.9 routing. Classify
  fills by anchor presence (GND via OR GND pad inside), not by net name.
- Diagonal BFS chords dip between cell centers: a path whose endpoints are
  clearance-clean can still violate by up to ~0.07 mm at segment midpoints.
  Use orthogonal-only walk when clearance margin < one step (0.05 mm).
- Hole-to-hole applies to same-net vias too (GND×GND): keep 0.25 mm hole-edge
  distance to ALL holes, not just foreign ones.

## Next iteration (queued, not done)

1. Re-route U3.8 with orthogonal-only BFS, TP1 keepout 0.55 mm, goal via
   0.4/0.2 (larger annular kills the EFUSE_ILM near-misses), same-net via
   distance >= 0.5 mm. Scripts preserved: `/tmp/gnd_v12.py` (router),
   `/tmp/extract_zones4.py` (zone classification), `/tmp/pcb_merged_u7.kicad_pcb`
   (clean base).
2. After clean DRC: regenerate renders/PDF/STEP (STEP + positions currently
   predate this session), then move the TP1 island root cause upstream
   (island is a fill anomaly; may disappear on next full refill).
