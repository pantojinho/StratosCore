# RP2040 ADS-B firmware plan

Dedicated capture, preamble/frame extraction, timestamping, format-aware parity validation and transport/health reporting. PIO plus DMA is the candidate mechanism; no copied PIO, hardcoded pin assignment or build exists.

Specify clock limits, PIO/DMA resources, boot flash, watchdog, recovery, packet protocol and queue-overflow behavior after frontend characterization. Test decoder logic with independent known fixtures, then conducted waveform replay. See [ADS-B architecture](../../docs/ADSB_ARCHITECTURE.md) and [reuse register](../../references/REUSE_REGISTER.md); GPL code is not implicitly part of this MIT firmware.
