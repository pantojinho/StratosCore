#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Clean-room UART transport framing for the RP2040 ADS-B capture link.

Host-side model of the record format exchanged over the dedicated 921600-baud
8N1 UART with RTS/CTS between the RP2040 capture processor and the ESP32 host.
This module and its tests prove the framing, sequencing, timestamping,
overflow-visibility and resynchronization contract on the host before the
RP2040 PIO/DMA implementation exists. It intentionally does not model PIO
state machines, DMA rings or silicon timing.

Wire record layout (little-endian fields, all sizes in bytes):

    offset  size  field
    0       2     SYNC        0xA5 0x5A
    2       1     VERSION     protocol version, currently 0x01
    3       1     TYPE        0x01 CONTACT, 0x02 OVERFLOW, 0x03 WRAP, 0x04 HEARTBEAT
    4       1     SEQ         rolling 8-bit sequence number, increments per record
    5       4     TS          sample-clock timestamp, 8 MHz, wraps at 2**32
    9       1     LEN         payload length in bytes (0..255)
    10      LEN   PAYLOAD     record specific
    10+LEN  2     CRC16       CCITT-FALSE over VERSION..PAYLOAD inclusive

CONTACT payload: 1 class byte (0x01 = 56-bit DF11, 0x02 = 112-bit DF17),
1 confidence byte, then the 7- or 14-byte Mode S frame.
OVERFLOW payload: 2-byte count of records/samples dropped since the previous
OVERFLOW record (or since reset for the first one).
WRAP payload: 4-byte sample-clock wrap counter; sent when TS wraps and at
least once at startup. Host reconstructs a 64-bit timestamp as
(wraps << 32) | ts.
HEARTBEAT payload: 4-byte uptime in sample ticks of the most recent wrap-free
window; used to detect silent stalls when no contacts arrive.

Decoder behavior contract:
- resynchronization: any byte that is not a valid record start is skipped;
  after garbage, decoding resumes at the next SYNC pair.
- a CRC failure discards the record and counts it, never aborts the stream.
- a SEQ discontinuity flags exactly one overflow event per gap, but the
  OVERFLOW record is the authoritative dropped-sample count.
- timestamps must be strictly monotonic on the reconstructed 64-bit clock;
  equal or lower timestamps are protocol violations reported by the decoder.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Iterator, Sequence

SYNC_A, SYNC_B = 0xA5, 0x5A
VERSION = 0x01
HEADER_LEN = 10  # SYNC(2) VERSION(1) TYPE(1) SEQ(1) TS(4) LEN(1)
CRC_LEN = 2
CRC_INIT = 0xFFFF
CRC_POLY = 0x1021  # CCITT-FALSE


class RecordType(enum.IntEnum):
    CONTACT = 0x01
    OVERFLOW = 0x02
    WRAP = 0x03
    HEARTBEAT = 0x04


class FrameClass:
    DF11 = 0x01
    DF17 = 0x02


def crc16_ccitt(data: Sequence[int]) -> int:
    crc = CRC_INIT
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ CRC_POLY) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def _u32(value: int) -> bytes:
    return bytes((value >> shift) & 0xFF for shift in (0, 8, 16, 24))


def build_record(record_type: RecordType, seq: int, ts: int, payload: bytes = b"") -> bytes:
    if not 0 <= len(payload) <= 255:
        raise ValueError("payload must fit LEN (0..255)")
    if not 0 <= ts < 1 << 32:
        raise ValueError("ts is a 32-bit sample-clock value")
    body = bytes((VERSION, int(record_type), seq & 0xFF)) + _u32(ts) + bytes((len(payload),)) + payload
    crc = crc16_ccitt(body)
    return bytes((SYNC_A, SYNC_B)) + body + bytes((crc & 0xFF, (crc >> 8) & 0xFF))


def encode_contact(frame: bytes, ts: int, seq: int, confidence: int = 0xFF) -> bytes:
    if len(frame) == 7:
        fclass = FrameClass.DF11
    elif len(frame) == 14:
        fclass = FrameClass.DF17
    else:
        raise ValueError("contact payload is a 56- or 112-bit Mode S frame")
    return build_record(RecordType.CONTACT, seq, ts, bytes((fclass, confidence)) + frame)


def encode_overflow(ts: int, seq: int, dropped: int) -> bytes:
    if not 0 <= dropped < 1 << 16:
        raise ValueError("dropped must fit 16 bits")
    return build_record(RecordType.OVERFLOW, seq, ts, bytes((dropped & 0xFF, (dropped >> 8) & 0xFF)))


def encode_wrap(ts: int, seq: int, wraps: int) -> bytes:
    return build_record(RecordType.WRAP, seq, ts, _u32(wraps))


def encode_heartbeat(ts: int, seq: int, uptime_ticks: int) -> bytes:
    return build_record(RecordType.HEARTBEAT, seq, ts, _u32(uptime_ticks))


@dataclass
class StreamStats:
    records: int = 0
    crc_errors: int = 0
    seq_gaps: int = 0
    resync_skips: int = 0
    monotonic_violations: int = 0

    def as_dict(self) -> dict[str, int]:
        return dict(self.__dict__)


@dataclass
class Record:
    record_type: RecordType
    seq: int
    ts64: int  # reconstructed (wraps << 32) | ts
    payload: bytes


class Decoder:
    """Streaming decoder implementing the contract in the module docstring."""

    def __init__(self) -> None:
        self.stats = StreamStats()
        self._buf = bytearray()
        self._last_seq: int | None = None
        self._wraps = 0
        self._max_ts: int = -1
        self._saw_wrap_record = False

    def feed(self, data: bytes) -> Iterator[Record]:
        self._buf.extend(data)
        while True:
            record = self._pop_record()
            if record is None:
                return
            yield record

    # --- internal ---------------------------------------------------------

    def _pop_record(self) -> Record | None:
        while True:
            buf = self._buf
            # Skip garbage until a SYNC pair appears; bounded scan keeps this O(n).
            sync = buf.find(bytes((SYNC_A, SYNC_B)))
            if sync == -1:
                keep = 1  # keep last byte: it may pair with the next feed's first byte
                self.stats.resync_skips += max(0, len(buf) - keep)
                del buf[: len(buf) - keep]
                return None
            if sync:
                self.stats.resync_skips += sync
                del buf[:sync]
                continue

            if len(buf) < HEADER_LEN:
                return None
            ts = int.from_bytes(buf[5:9], "little")
            length = buf[9]
            if length == 0 and buf[3] in (RecordType.CONTACT, RecordType.OVERFLOW, RecordType.WRAP):
                # These record types always carry a payload; a zero LEN here means
                # the SYNC bytes are inside a payload, not a record start.
                del buf[:1]
                self.stats.resync_skips += 1
                continue
            total = HEADER_LEN + length + CRC_LEN
            if len(buf) < total:
                return None

            body = bytes(buf[2 : HEADER_LEN + length])
            version, rtype, seq = body[0], body[1], body[2]
            expected = crc16_ccitt(body)
            got = buf[HEADER_LEN + length] | (buf[HEADER_LEN + length + 1] << 8)
            del buf[:total]

            if version != VERSION or expected != got:
                self.stats.crc_errors += 1
                continue  # stream continues after the discarded record
            try:
                record_type = RecordType(rtype)
            except ValueError:
                self.stats.crc_errors += 1
                continue

            if self._last_seq is not None and ((seq - self._last_seq) & 0xFF) > 1:
                self.stats.seq_gaps += 1
            self._last_seq = seq

            payload = bytes(body[8:])
            if record_type is RecordType.WRAP:
                self._wraps = int.from_bytes(payload[:4], "little")
                self._saw_wrap_record = True
            if record_type is RecordType.CONTACT and not self._saw_wrap_record:
                # A contact before any WRAP record is a producer contract violation.
                self.stats.monotonic_violations += 1

            ts64 = (self._wraps << 32) | ts
            if ts64 <= self._max_ts:
                self.stats.monotonic_violations += 1
            else:
                self._max_ts = ts64

            self.stats.records += 1
            return Record(record_type, seq, ts64, payload)


def reconstruct_streams(records: Sequence[Record]) -> list[tuple[int, bytes]]:
    """Return (ts64, frame) pairs from CONTACT records only."""
    return [(r.ts64, r.payload[2:]) for r in records if r.record_type is RecordType.CONTACT]
