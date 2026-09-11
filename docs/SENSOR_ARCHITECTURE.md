# Sensor architecture

Locked set: **ICM-42688-P**, **MMC5983MA**, **BMP581**, **SHT40**. BME688 gas/VOC sensing is excluded from baseline. Sensor package temperatures are not substitutes for ambient SHT40 measurement.

| Sensor | Function | Interface plan | Primary source |
| --- | --- | --- | --- |
| ICM-42688-P | Accelerometer + gyro | I2C at 0x68 plus INT1; pin/application entry released, custom physical footprint pending | [TDK DS-000347 v1.9](https://www.invensense.tdk.com/en-us/download-resource/ds-000347-icm-42688-p-datasheet) |
| MMC5983MA | Three-axis magnetic field and calibrated heading input | I2C at 0x30; polled in Rev A; logical pin carrier entered, no footprint | [MEMSIC datasheet Rev A](https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5983MADatasheetRevA.pdf) |
| BMP581 | Pressure, barometric altitude and variometer input | I2C at 0x46; polled in Rev A; logical pin carrier entered, no footprint | [Bosch BST-BMP581-DS004](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf) |
| SHT40-AD1B-R2 | Ambient temperature/humidity | I2C at 0x44; exact symbol/footprint entered; heater normally disabled during ambient measurements | [Sensirion SHT4x datasheet v7.3](https://sensirion.com/media/documents/33FD6951/6A7C10A0/HT_DS_Datasheet_SHT4x_V7.3.pdf) |

Do not assign final I2C addresses until strap states and exact ordering codes are verified; touch, PMIC, fuel gauge and expansion devices must be included in the address/capacitance audit. Choose bus speed for the slowest participating device and actual loading. Add timeout/recovery for a peripheral holding the bus low. Review IRQ/wake requirements before exhausting GPIOs.

The reviewed schematic subset implements MMC5983MA with its 10 µF CAP capacitor and 1 µF VDD decoupling, BMP581 with 100 nF on each rail, and SHT40-AD1B-R2 with 100 nF decoupling. BMP581 VDD is 1.71–3.6 V and VDDIO is 1.08–3.6 V. Bosch DS004-13 Figure 28 requires 10 Ω in VDD and 100 Ω in VDDIO if either rail rises in less than 10 µs; the schematic keeps selectable positions until the rail ramps are measured. Shared I2C pull-ups remain assigned to the interfaces sheet.

ICM-42688-P DS-000347 v1.9 confirms AD0 low for 0x68, AP_CS tied to VDDIO for I2C, pin 7 tied to ground, and INT2/FSYNC/CLKIN grounded when unused. Its application circuit requires 0.1 µF plus 2.2 µF at VDD and 10 nF at VDDIO. AN-000393 v2.4 says the LGA PCB lands follow the package terminals, mask openings add 0.1 mm to land length and width, and stencil opening area is 90% of land area. The similar generic KiCad LGA footprint has larger pads and is not accepted for this device.

## Mechanical and thermal integration

Place SHT40 near an air exchange path and away from charger, regulators, ESP32, display backlight and warm cells. Evaluate slots or a narrow thermal neck around its PCB island while preserving mechanical strength and appropriate electrical return paths. Venting and environmental protection affect response; avoid coating or contaminating sensing openings. Follow manufacturer handling/reflow rules.

Give BMP581 a static-pressure vent protected from direct airflow, moisture and enclosure pressure transients. Do not use a fully sealed box as an assumed atmospheric pressure source. Microphone acoustic vent and pressure vent may have incompatible membrane/response needs.

Place ICM-42688-P on mechanically stable PCB area, not the flexible thermal island. Document body axes and transform to display coordinates in firmware. Keep MMC5983MA away from ferromagnetic fasteners, cell cans, inductors and current loops; test heading bias with one/two cells, charging and radio activity.

## Processing and acceptance

Record raw calibrated vectors, sample rates, timestamps, temperature and calibration version. Characterize gyro bias, acceleration scale/alignment, hard/soft-iron magnetic errors and tilt compensation. Distinguish magnetic heading from true heading; magnetic declination requires a defined source and valid position/time. An IMU does not provide reliable absolute yaw alone.

Vario processing needs pressure-noise/filter/group-delay characterization and a documented reference-pressure model. Specify altitude datum and out-of-range policy. BMP581's specified pressure envelope must be checked against the intended balloon ascent; no extrapolated altitude accuracy is promised. Evaluate SHT40's heating bias in enclosed FLIGHT and USB-charging states against an external reference.

Before board integration: read device IDs/status, verify axes with controlled rotations, check steady pressure and temperature, interrupt timing, sensor-failure recovery and power-cycle behavior. No calibration or performance figures are claimed by this foundation.
