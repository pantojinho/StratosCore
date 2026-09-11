# avBadge 2024 research notes

Source: [AerospaceVillage/avBadge_2024](https://github.com/AerospaceVillage/avBadge_2024/tree/d03f2a3bee7544e03df314edd8eafa24e040701b), reviewed 2026-09-11 UTC.

Reviewed the [README](https://github.com/AerospaceVillage/avBadge_2024/blob/d03f2a3bee7544e03df314edd8eafa24e040701b/README.md), [published schematic PDF](https://github.com/AerospaceVillage/avBadge_2024/blob/d03f2a3bee7544e03df314edd8eafa24e040701b/hardware/DCAV32_WINGLET_V1P_OSR.pdf) sheet 8/10 (PDF page 8, visually inspected), [kernel ADS-B driver](https://github.com/AerospaceVillage/avBadge_2024/blob/d03f2a3bee7544e03df314edd8eafa24e040701b/software/winglet-kernel/drivers/char/winglet_adsb_rx.c) and [GUI receiver](https://github.com/AerospaceVillage/avBadge_2024/blob/d03f2a3bee7544e03df314edd8eafa24e040701b/software/winglet-gui/winglet-ui/worker/adsbreceiver.cpp).

## Observed architecture

This is a Linux badge with GNSS, display, storage and native aircraft reception. It is not an ESP32/RP2040 design. Schematic sheet 8 shows antenna switching (PE4259-63), PSA4-5043 gain stage, TA0970A SAW, SGL0622Z gain stage, TA0232A SAW, AD8313 detector and COS6143SR output stage, with output to `SOC_TVIN0`. Thus the actual filter/gain order differs from StratosCore's initial filter-first concept. The listed values are evidence of the reference, not selected BOM parts.

The inspected kernel driver exchanges short/long message data with a DSP and queues results for host software, including overflow handling. The inspected GUI code consumes receiver messages and maintains aircraft fields with validity flags. This supports separating acquisition, decoding and UI; it does not establish equivalent performance for a comparator/PIO implementation.

## Transferable questions

Study gain distribution versus blockers, detector/video pulse fidelity, clean analog power, antenna selection and ownship-relative UI. StratosCore needs a logic-compatible comparator path for RP2040 rather than copying the TV-input output stage. Carry over the concept of validity and overrun reporting with independently designed interfaces.

## License and reuse disposition

No clear repository-wide hardware license was established from the inspected root/hardware files. The large recursive API tree was truncated; this is not proof that no license exists anywhere. Kernel and other subtrees contain their own license material; those do not automatically license the hardware or GUI. Do not copy circuits, layout, firmware, graphical assets or pin maps until exact scope and permission are established.

Actual reuse: none. Modifications: none. Future review must record each source file, commit, applicable license, permission and changes in [REUSE_REGISTER.md](REUSE_REGISTER.md). Full schematic electrical verification and hardware reproduction were outside this foundation task.
