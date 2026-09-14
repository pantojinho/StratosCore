# SPDX-License-Identifier: MIT
"""Tests for the RP2040 ADS-B UART framing contract (host model)."""
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import framing  # noqa: E402
from framing import (  # noqa: E402
    Decoder,
    RecordType,
    build_record,
    crc16_ccitt,
    encode_contact,
    encode_heartbeat,
    encode_overflow,
    encode_wrap,
)

KNOWN_DF17 = bytes.fromhex("8D40621D58C382D690C8AC2863A7")
SHORT_FRAME = bytes.fromhex("5D40621D58C382")


def collect(decoder: Decoder, chunks) -> list:
    out = []
    for chunk in chunks:
        out.extend(decoder.feed(chunk))
    return out


class CrcTests(unittest.TestCase):
    def test_known_ccitt_vector(self) -> None:
        # ITU-T V.41 check value for "123456789"
        self.assertEqual(crc16_ccitt(b"123456789"), 0x29B1)

    def test_crc_field_little_endian_round_trip(self) -> None:
        record = build_record(RecordType.HEARTBEAT, 7, 123456, b"\x01\x02\x03")
        self.assertEqual(record[0], 0xA5)
        self.assertEqual(record[1], 0x5A)
        body = record[2:-2]  # VERSION..PAYLOAD inclusive
        crc = record[-2] | (record[-1] << 8)
        self.assertEqual(crc, crc16_ccitt(body))


class ContactFramingTests(unittest.TestCase):
    def test_df17_round_trip(self) -> None:
        decoder = Decoder()
        records = collect(decoder, [encode_contact(KNOWN_DF17, ts=1000, seq=0)])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].record_type, RecordType.CONTACT)
        self.assertEqual(records[0].payload[2:], KNOWN_DF17)
        self.assertEqual(records[0].ts64, 1000)

    def test_contact_requires_wrap_record_first(self) -> None:
        decoder = Decoder()
        collect(decoder, [encode_contact(KNOWN_DF17, ts=5, seq=0)])
        self.assertEqual(decoder.stats.monotonic_violations, 1)

    def test_56_and_112_bit_classes(self) -> None:
        decoder = Decoder()
        stream = [encode_wrap(0, 0, 0), encode_contact(SHORT_FRAME, 10, 1), encode_contact(KNOWN_DF17, 20, 2)]
        records = collect(decoder, stream)
        contacts = [r for r in records if r.record_type is RecordType.CONTACT]
        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0].payload[0], 0x01)
        self.assertEqual(contacts[1].payload[0], 0x02)


class TimestampTests(unittest.TestCase):
    def test_strict_monotonic_ok(self) -> None:
        decoder = Decoder()
        stream = [encode_wrap(0, 0, 0)] + [encode_heartbeat(ts, i + 1, ts) for i, ts in enumerate((1, 2, 10, 11, 5000))]
        records = collect(decoder, stream)
        self.assertEqual(decoder.stats.monotonic_violations, 0)
        self.assertEqual([r.ts64 for r in records][1:], [1, 2, 10, 11, 5000])

    def test_reconstructs_64bit_time_across_wrap(self) -> None:
        decoder = Decoder()
        stream = [
            encode_wrap(0xFFFFF000, 0, 0),
            encode_heartbeat(0xFFFFFF00, 1, 0xFFFFFF00),
            encode_wrap(0x00000010, 2, 1),
            encode_heartbeat(0x00000020, 3, 0x20),
        ]
        records = collect(decoder, stream)
        beats = [r for r in records if r.record_type is RecordType.HEARTBEAT]
        self.assertEqual(beats[0].ts64, 0xFFFFFF00)
        self.assertEqual(beats[1].ts64, (1 << 32) + 0x20)

    def test_non_monotonic_flagged_not_crash(self) -> None:
        decoder = Decoder()
        stream = [encode_wrap(0, 0, 0), encode_heartbeat(100, 1, 100), encode_heartbeat(50, 2, 50)]
        collect(decoder, stream)
        self.assertEqual(decoder.stats.monotonic_violations, 1)


class OverflowTests(unittest.TestCase):
    def test_overflow_record_decodes_count(self) -> None:
        decoder = Decoder()
        stream = [encode_wrap(0, 0, 0), encode_overflow(100, 1, 512), encode_contact(KNOWN_DF17, 200, 2)]
        records = collect(decoder, stream)
        self.assertEqual(records[1].record_type, RecordType.OVERFLOW)
        self.assertEqual(records[1].payload, (512).to_bytes(2, "little"))

    def test_seq_gap_flagged_exactly_once(self) -> None:
        decoder = Decoder()
        stream = [encode_wrap(0, 0, 0)]
        seq = 0
        for i in range(4):
            seq = (seq + 1) & 0xFF
            stream.append(encode_heartbeat(100 + i, seq, 100 + i))
        stream.append(encode_heartbeat(200, (seq + 5) & 0xFF, 200))  # gap of 5
        collect(decoder, stream)
        self.assertEqual(decoder.stats.seq_gaps, 1)

    def test_seq_wraps_cleanly_at_255(self) -> None:
        decoder = Decoder()
        stream = [encode_wrap(0, 254, 0), encode_heartbeat(1, 255, 1), encode_heartbeat(2, 0, 2)]
        collect(decoder, stream)
        self.assertEqual(decoder.stats.seq_gaps, 0)


class ResyncTests(unittest.TestCase):
    def test_garbage_before_stream(self) -> None:
        decoder = Decoder()
        stream = [b"\x00\x11\x22\x33\xff" + encode_wrap(0, 0, 0)]
        records = collect(decoder, stream)
        self.assertEqual(len(records), 1)
        self.assertEqual(decoder.stats.resync_skips, 5)

    def test_corrupted_byte_in_record_discards_and_resyncs(self) -> None:
        good = encode_wrap(0, 0, 0) + encode_heartbeat(10, 1, 10) + encode_heartbeat(20, 2, 20)
        corrupted = bytearray(good)
        corrupted[5] ^= 0x40  # inside first record TS
        decoder = Decoder()
        records = collect(decoder, [bytes(corrupted)])
        self.assertEqual(len(records), 2)  # first record dropped, stream continues
        self.assertEqual(decoder.stats.crc_errors, 1)

    def test_byte_by_byte_feed(self) -> None:
        decoder = Decoder()
        stream = encode_wrap(0, 0, 0) + encode_contact(KNOWN_DF17, 42, 1)
        records = collect(decoder, [bytes([b]) for b in stream])
        self.assertEqual(len(records), 2)
        self.assertEqual(decoder.stats.crc_errors, 0)

    def test_truncated_tail_does_not_emit(self) -> None:
        decoder = Decoder()
        full = encode_heartbeat(10, 1, 10)
        records = collect(decoder, [encode_wrap(0, 0, 0), full[:-3]])
        self.assertEqual(len(records), 1)  # only the WRAP; partial record held
        records.extend(decoder.feed(full[-3:]))
        self.assertEqual(len(records), 2)

    def test_corrupted_length_does_not_swallow_next_record(self) -> None:
        bad = bytearray(encode_heartbeat(10, 1, 10))
        bad[9] = 250
        good = encode_wrap(20, 2, 0)
        decoder = Decoder()
        records = collect(decoder, [bytes(bad) + good])
        self.assertEqual([r.record_type for r in records], [RecordType.WRAP])
        self.assertGreaterEqual(decoder.stats.format_errors, 1)

    def test_contact_class_must_match_payload_length(self) -> None:
        malformed = build_record(RecordType.CONTACT, 1, 10, bytes((0x01, 0xFF)) + KNOWN_DF17)
        good = encode_wrap(20, 2, 0)
        decoder = Decoder()
        records = collect(decoder, [malformed + good])
        self.assertEqual([r.record_type for r in records], [RecordType.WRAP])
        self.assertEqual(decoder.stats.format_errors, 1)

    def test_fixed_record_type_rejects_wrong_length(self) -> None:
        malformed = build_record(RecordType.OVERFLOW, 1, 10, b"\x01\x00\x00")
        good = encode_wrap(20, 2, 0)
        decoder = Decoder()
        records = collect(decoder, [malformed + good])
        self.assertEqual([r.record_type for r in records], [RecordType.WRAP])
        self.assertGreaterEqual(decoder.stats.format_errors, 1)


class ConcurrencyTests(unittest.TestCase):
    """Interleave independent producers the way DMA ring + ISR would."""

    def test_interleaved_contacts_overflow_heartbeat(self) -> None:
        decoder = Decoder()
        stream = encode_wrap(0, 0, 0)
        seq = 1
        for i in range(20):
            stream += encode_contact(KNOWN_DF17, ts=1000 * i + 1, seq=seq)
            seq = (seq + 1) & 0xFF
            if i % 5 == 4:
                stream += encode_overflow(ts=1000 * i + 2, seq=seq, dropped=(i + 1) * 3)
                seq = (seq + 1) & 0xFF
            stream += encode_heartbeat(ts=1000 * i + 3, seq=seq, uptime_ticks=1000 * i + 3)
            seq = (seq + 1) & 0xFF
        records = collect(decoder, [stream[: len(stream) // 2], stream[len(stream) // 2 :]])
        self.assertEqual(decoder.stats.records, 1 + 20 + 4 + 20)
        self.assertEqual(decoder.stats.crc_errors, 0)
        self.assertEqual(decoder.stats.monotonic_violations, 0)
        contacts = [r for r in records if r.record_type is RecordType.CONTACT]
        self.assertEqual(len(contacts), 20)
        frames = [r.payload[2:] for r in contacts]
        self.assertTrue(all(f == KNOWN_DF17 for f in frames))

    def test_capture_stress_burst_loss_visibility(self) -> None:
        """A long fragmented stream keeps contacts and declared drops consistent."""
        decoder = Decoder()
        stream = encode_wrap(0, 0, 0)
        seq = 0
        declared_drops = 0
        ts = 1
        for i in range(200):
            if i % 7 == 3:  # simulated DMA ring overrun every 7 contacts
                declared_drops += 13
                seq = (seq + 1) & 0xFF
                stream += encode_overflow(ts, seq, 13)
                ts += 2
            seq = (seq + 1) & 0xFF
            stream += encode_contact(KNOWN_DF17, ts, seq)
            ts += 960  # 120 us spacing at the 8 MHz sample clock
        records = collect(decoder, [stream[i * 997 : (i + 1) * 997] for i in range(len(stream) // 997 + 1)])
        contacts = [r for r in records if r.record_type is RecordType.CONTACT]
        self.assertEqual(len(contacts), 200)
        drops = sum(int.from_bytes(r.payload, "little") for r in records if r.record_type is RecordType.OVERFLOW)
        self.assertEqual(drops, declared_drops)
        self.assertEqual(decoder.stats.monotonic_violations, 0)


if __name__ == "__main__":
    unittest.main()
