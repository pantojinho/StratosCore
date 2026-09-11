# Preliminary BOM conventions

[preliminary_bom.csv](preliminary_bom.csv) is a functional planning list with the owner's exact 13 columns. Each locked component or mandatory generic block is represented; open selections are explicit. This is not an orderable or quantity-complete assembly BOM.

`Reference` values are logical block labels, **not assigned schematic reference designators**. `LOCKED` identifies the selected device; `REQUIRED - MPN TBD` identifies mandatory hardware without a chosen device; `OPEN` identifies a remaining architecture/support choice. The microphone remains required as a provision with optional operation; a later DNP needs a documented decision.

Manufacturer names for selected parts follow the primary source index. Supply ranges and packages remain TBD where a full electrical/package audit has not been completed. Dated distributor evidence populates selected supplier fields, but it is not an approved vendor list or a purchasing commitment. Assembly entries are targets, not a confirmation that a particular factory accepts the part.

Sources: [locked decisions](../docs/DECISIONS.md), [component evidence](../docs/COMPONENT_EVIDENCE.md), [manufacturer index](../hardware/datasheets/README.md), and [power candidates](../docs/POWER_ARCHITECTURE_OPTIONS.md). Future complete BOMs need quantities, actual reference designators and sourced ordering suffixes, without modifying this requested preliminary CSV schema casually.
