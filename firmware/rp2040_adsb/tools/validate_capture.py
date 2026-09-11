#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Clean-room Mode S pulse-position capture model used before RP2040 PIO work.

This host-only tool intentionally models the digital boundary. It does not model RF
gain, detector voltage, comparator hysteresis, metastability, or RP2040 DMA.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


SAMPLES_PER_US = 8
HALF_SYMBOL_SAMPLES = SAMPLES_PER_US // 2
PREAMBLE_US = 8
PREAMBLE_SAMPLES = PREAMBLE_US * SAMPLES_PER_US
MODE_S_POLY = 0xFFF409


@dataclass(frozen=True)
class DecodedFrame:
    start_sample: int
    payload: bytes
    crc_remainder: int

    @property
    def valid_crc(self) -> bool:
        return self.crc_remainder == 0


def mode_s_crc(frame: bytes) -> int:
    """Return the 24-bit Mode S polynomial remainder for a complete frame."""
    if len(frame) not in (7, 14):
        raise ValueError("Mode S frames are 56 or 112 bits")
    bit_count = len(frame) * 8
    remainder = int.from_bytes(frame, "big")
    for bit_index in range(bit_count - 24):
        test_bit = 1 << (bit_count - 1 - bit_index)
        if remainder & test_bit:
            remainder ^= MODE_S_POLY << (bit_count - 25 - bit_index)
    return remainder & 0xFFFFFF


def _bits(data: bytes) -> Iterable[int]:
    for value in data:
        for shift in range(7, -1, -1):
            yield (value >> shift) & 1


def synthesize_samples(frame: bytes, jitter: Sequence[int] | None = None) -> list[int]:
    """Create an 8 MHz comparator stream for one Mode S frame."""
    if len(frame) not in (7, 14):
        raise ValueError("Mode S frames are 56 or 112 bits")
    jitter = jitter or (0, 0, 0, 0)
    if len(jitter) != 4 or any(abs(value) > 1 for value in jitter):
        raise ValueError("preamble jitter must contain four values in [-1, 1]")

    guard = SAMPLES_PER_US
    data_samples = len(frame) * 8 * SAMPLES_PER_US
    samples = [0] * (guard + PREAMBLE_SAMPLES + data_samples + SAMPLES_PER_US)
    for start, shift in zip((0, 8, 28, 36), jitter):
        shifted = guard + start + shift
        samples[shifted : shifted + HALF_SYMBOL_SAMPLES] = [1] * HALF_SYMBOL_SAMPLES

    cursor = guard + PREAMBLE_SAMPLES
    for bit in _bits(frame):
        pulse_start = cursor if bit else cursor + HALF_SYMBOL_SAMPLES
        samples[pulse_start : pulse_start + HALF_SYMBOL_SAMPLES] = [1] * HALF_SYMBOL_SAMPLES
        cursor += SAMPLES_PER_US
    return samples


def find_preamble(samples: Sequence[int]) -> int:
    """Locate the best 8 us preamble using pulse and quiet-window correlation."""
    template = [0] * PREAMBLE_SAMPLES
    for pulse_start in (0, 8, 28, 36):
        template[pulse_start : pulse_start + HALF_SYMBOL_SAMPLES] = [1] * HALF_SYMBOL_SAMPLES
    best_start = -1
    best_score = -10_000
    for start in range(0, len(samples) - PREAMBLE_SAMPLES + 1):
        window = samples[start : start + PREAMBLE_SAMPLES]
        score = sum(1 if actual == expected else -1 for actual, expected in zip(window, template))
        if score > best_score:
            best_start, best_score = start, score
    if best_score < 48:
        raise ValueError("no valid Mode S preamble found")
    return best_start


def decode_samples(samples: Sequence[int], frame_bytes: int = 14) -> DecodedFrame:
    if frame_bytes not in (7, 14):
        raise ValueError("frame_bytes must be 7 or 14")
    start = find_preamble(samples)
    cursor = start + PREAMBLE_SAMPLES
    required = cursor + frame_bytes * 8 * SAMPLES_PER_US
    if required > len(samples):
        raise ValueError("capture ends before complete frame")

    value = 0
    for _ in range(frame_bytes * 8):
        first = sum(samples[cursor : cursor + HALF_SYMBOL_SAMPLES])
        second = sum(samples[cursor + HALF_SYMBOL_SAMPLES : cursor + SAMPLES_PER_US])
        if first == second:
            raise ValueError("ambiguous pulse-position symbol")
        value = (value << 1) | int(first > second)
        cursor += SAMPLES_PER_US
    payload = value.to_bytes(frame_bytes, "big")
    return DecodedFrame(start, payload, mode_s_crc(payload))


def main() -> None:
    known_df17 = bytes.fromhex("8D40621D58C382D690C8AC2863A7")
    decoded = decode_samples(synthesize_samples(known_df17, (-1, 0, 1, 0)))
    print(f"frame={decoded.payload.hex().upper()} crc=0x{decoded.crc_remainder:06X}")


if __name__ == "__main__":
    main()
