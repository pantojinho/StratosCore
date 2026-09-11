# Mechanical requirements

Target footprint approximately **80 x 60 mm**, desired thickness **25-32 mm**, with a **3D-printed enclosure**. These are product targets, not CAD dimensions. PCB outline must leave enclosure walls, mounting features and manufacturing clearance; an 80 x 60 mm PCB will not fit inside an enclosure with exactly the same outside dimensions.

Support a compact one-21700 variant and larger two-21700 variant. Nominal cell class is about 21 mm diameter x 70 mm length; actual selected cell, protection/button top, wrapper, contact travel and holder can exceed those values. A nominal 70 mm cell leaves only 10 mm along the 80 mm target for both contacts and walls. Two nominal diameters already consume 42 mm before separators/holders. Verify tolerance stacks before claiming fit.

A 21 mm cylinder beneath a display, PCB, components and walls makes 25 mm thickness especially aggressive. Do not freeze cell position, board outline, connector cutouts or stacked-board design from this arithmetic. Keep batteries away from antenna keepouts and evaluate magnetic bias.

## Required fit study

Build later dummy solids from verified drawings: module/antenna keepout, LCD glass/FPC/connector, cell(s)/holder/removal clearance, PCB/component heights, USB-C, microSD insertion/removal, two button actuators, GNSS antenna alternatives, LoRa U.FL pigtail/SMA bulkhead and ADS-B RF path. Check both orientations, fingers/grip, cable bends and access to recovery/test pads.

Provide positive cell retention, insulated contacts, reverse-insertion prevention, no wrapper damage, and a serviceable battery door. Account for vibration and drops. 3D-print material must be selected against measured internal heat and solar exposure; no flammability, ingress or impact rating is claimed.

SHT40 needs airflow and thermal isolation. BMP581 needs a controlled static pressure path; microphone needs an acoustic path. Rain/dust membranes and slots must be designed with sensor response and manufacturability, not generic decorative openings. Provide antenna strain relief; do not let pigtails cross the ESP module antenna region casually.

Deliverables before placement: dimensioned envelope and tolerance table, one/two-cell section views, sensor/antenna keepout map, connector access review and printed fit dummy. Files in `mechanical/` are placeholders now; no fabricated STEP/STL is included.
