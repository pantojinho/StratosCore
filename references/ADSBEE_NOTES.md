# ADSBee research notes

Source: [PantsForBirds/adsbee](https://github.com/PantsForBirds/adsbee/tree/2942116b726f3b014605fc78af5373c6452c721d), reviewed 2026-09-11 UTC. Older CoolNamesAllTaken links in the repository redirect/name the same project lineage; use the pinned source for this review.

Reviewed [README](https://github.com/PantsForBirds/adsbee/blob/2942116b726f3b014605fc78af5373c6452c721d/README.md), [LICENSE](https://github.com/PantsForBirds/adsbee/blob/2942116b726f3b014605fc78af5373c6452c721d/LICENSE), repository inventory and [1090 capture PIO source](https://github.com/PantsForBirds/adsbee/blob/2942116b726f3b014605fc78af5373c6452c721d/firmware/adsbee_1090/pico/application/pio/capture.pio).

## Architectural findings

The 1090 design separates SAW/LNA/log detector/comparator conditioning, RP2040 timing and ESP32 networking. Comparator threshold control is part of receiver behavior. The current project additionally describes CC1312 UAT reception and a separate LR2021/CC1314 product family. Neither UAT nor that alternative processor/radio becomes a StratosCore requirement.

The inspected PIO source allocates multiple detector/demodulator state machines and documents sampling at 48 MHz. Comments discuss asymmetric AD8313 pulse edges and timing adjustments. This is stronger evidence than assuming an arbitrary GPIO interrupt can decode the waveform. StratosCore must measure its own detector pulse response, resource use and worst-case overruns; reference clocks/constants are not validated settings for a new frontend.

## License boundary

The project declares GNU GPL v3 for its firmware, software and design files. This is not permission to relabel copied material MIT or CERN-OHL-P. GPL-compliant reuse may be possible with retained obligations; obtaining a separate license or an independently authored implementation are alternatives to review. An RP2040/ESP32 separation is not, by itself, a legal compatibility conclusion.

No source code, PIO program, schematic, layout or library was imported or modified. The prototype and final frontend still require component datasheets and manufacturer application verification. Record actual future reuse in [REUSE_REGISTER.md](REUSE_REGISTER.md).
