# RP2040 ADS-B firmware plan

The first clean-room validation artifact is a host-only pulse-position capture model. It generates and decodes a known 112-bit DF17 fixture at 8 samples/us and validates the Mode S CRC polynomial without importing ADSBee GPL source.

Run from the repository root:

```powershell
python -m unittest discover firmware/rp2040_adsb/tests -v
python firmware/rp2040_adsb/tools/validate_capture.py
```

This proves only the digital timing/test contract. RP2040 PIO/DMA, comparator behavior, RF sensitivity and the ESP32 transport still require implementation and bench measurements described in [the validation plan](../../docs/ADSB_VALIDATION.md).
