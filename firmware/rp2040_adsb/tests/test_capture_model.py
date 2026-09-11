# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from validate_capture import decode_samples, mode_s_crc, synthesize_samples  # noqa: E402


KNOWN_DF17 = bytes.fromhex("8D40621D58C382D690C8AC2863A7")


class CaptureModelTests(unittest.TestCase):
    def test_known_df17_has_zero_remainder(self) -> None:
        self.assertEqual(mode_s_crc(KNOWN_DF17), 0)

    def test_valid_frame_round_trip(self) -> None:
        decoded = decode_samples(synthesize_samples(KNOWN_DF17))
        self.assertEqual(decoded.payload, KNOWN_DF17)
        self.assertTrue(decoded.valid_crc)

    def test_preamble_sample_jitter(self) -> None:
        decoded = decode_samples(synthesize_samples(KNOWN_DF17, (-1, 1, -1, 1)))
        self.assertEqual(decoded.payload, KNOWN_DF17)
        self.assertTrue(decoded.valid_crc)

    def test_corrupted_payload_fails_crc(self) -> None:
        corrupted = bytearray(KNOWN_DF17)
        corrupted[5] ^= 0x04
        decoded = decode_samples(synthesize_samples(bytes(corrupted)))
        self.assertFalse(decoded.valid_crc)


if __name__ == "__main__":
    unittest.main()
