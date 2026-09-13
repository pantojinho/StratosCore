# Conceptual block diagram

Boxes are functions, not selected footprints, final rails or a wiring diagram. Dashed links are proposed interfaces. Exact routing, antenna positions and connectors are open.

```mermaid
flowchart LR
  USB[USB-C] --> PWR[Input protection + balanced 2S charger candidate]
  CELLS[Two removable matched 21700 cells in series] --> SAFE[Common 2S protection / current cutoff / NTC]
  CELLS <--> PWR
  SAFE --> RAILS[2S buck regulation and switched domains TBD]
  USB -. native USB data .-> ESP[ESP32-S3-WROOM-1-N16R8]
  RAILS --> ESP
  ESP <--> WIFI[Module PCB antenna: Wi-Fi / BLE]
  ESP -. display bus .-> LCD[2.8-inch IPS 320 x 240]
  TOUCH[Capacitive touch + two buttons] --> ESP
  GNSSA[GNSS antenna TBD] --> GNSS[MAX-M10S-00B]
  GNSS <-->|UART| ESP
  SENS[ICM-42688-P / MMC5983MA / BMP581 / SHT40] <-->|I2C or SPI allocation TBD| ESP
  ESP <-->|SPI| LORA[SX1262 + Semtech RF matching]
  LORA <--> UFL[U.FL: 915 MHz antenna]
  ADSA[Separate 1090 MHz antenna] --> LNA1[BLB01 candidate]
  LNA1 --> FILTER[TA2003A / BLB01 / TA2003A candidate]
  FILTER --> DET[ADL5513 / MCP6566 candidate]
  DET --> RP[RP2040: timing and Mode-S decoding]
  RP -. UART 921600 + RTS/CTS .-> ESP
  ESP <-->|Storage bus TBD| SD[microSD]
  MIC[Digital MEMS microphone] -. I2S / PDM .-> ESP
  ESP <--> EXP[3V3 / GND / I2C / SPI / UART / GPIO expansion]
  CHGMON[BQ25887 per-cell ADC / 2S state estimation TBD] -. I2C .-> ESP
  RAILS --> RFPOWER[GNSS / ADS-B / LoRa / sensors / display / SD domains]
```

The cell/charger link denotes balanced series charging with midpoint sensing, not permission to parallel removable cells. The common 2S discharge-protection and system-power path still require independent review. RF filter order and gain stages must follow blocker/noise analysis. See [power options](POWER_ARCHITECTURE_OPTIONS.md) and [ADS-B architecture](ADSB_ARCHITECTURE.md).
