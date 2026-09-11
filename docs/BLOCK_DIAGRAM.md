# Conceptual block diagram

Boxes are functions, not selected footprints, final rails or a wiring diagram. Dashed links are proposed interfaces. Exact routing, antenna positions and connectors are open.

```mermaid
flowchart LR
  USB[USB-C] --> PWR[Input protection and charger / power path TBD]
  CELLS[Removable 21700 bays] --> SAFE[Independent protection / topology TBD]
  SAFE <--> PWR
  PWR --> RAILS[Regulation and switched domains TBD]
  USB -. native USB data .-> ESP[ESP32-S3-WROOM-1-N16R8]
  RAILS --> ESP
  ESP <--> WIFI[Module PCB antenna: Wi-Fi / BLE]
  ESP -. display bus .-> LCD[2.8-inch IPS 320 x 240]
  TOUCH[Capacitive touch + two buttons] --> ESP
  GNSSA[GNSS antenna TBD] --> GNSS[ATGM332D-5NR32]
  GNSS <-->|UART| ESP
  SENS[ICM-42688-P / MMC5983MA / BMP581 / SHT40] <-->|I2C or SPI allocation TBD| ESP
  ESP <-->|SPI| LORA[SX1262 + Semtech RF matching]
  LORA <--> UFL[U.FL: 915 MHz antenna]
  ADSA[Separate 1090 MHz antenna] --> FILTER[RF preselection / SAW]
  FILTER --> LNA[LNA and further filtering TBD]
  LNA --> DET[Detector / comparator TBD]
  DET --> RP[RP2040: timing and Mode-S decoding]
  RP -. UART or SPI .-> ESP
  ESP <-->|Storage bus TBD| SD[microSD]
  MIC[Digital MEMS microphone] -. I2S / PDM .-> ESP
  ESP <--> EXP[3V3 / GND / I2C / SPI / UART / GPIO expansion]
  GAUGE[Fuel gauge TBD] -. I2C .-> ESP
  RAILS --> RFPOWER[GNSS / ADS-B / LoRa / sensors / display / SD domains]
```

The bidirectional cell/power-path link denotes the need for separately controlled charging and discharge paths, **not permission to parallel removable cells**. RF filter order and gain stages must follow blocker/noise analysis. See [power options](POWER_ARCHITECTURE_OPTIONS.md) and [ADS-B architecture](ADSB_ARCHITECTURE.md).
