import unittest
from app.services.silence_detector import invert_silences_to_speech


class TestSilenceDetector(unittest.TestCase):
    def test_invert_silences_to_speech(self):
        # 10 second audio with silences at [2.0, 3.5] and [6.0, 8.0]
        silences = [(2.0, 3.5), (6.0, 8.0)]
        total_dur = 10.0
        speech = invert_silences_to_speech(silences, total_dur, padding=0.08)

        self.assertTrue(len(speech) >= 2)
        # First speech chunk should start near 0.0
        self.assertAlmostEqual(speech[0][0], 0.0, places=1)
        # Last speech chunk should end near 10.0
        self.assertAlmostEqual(speech[-1][1], 10.0, places=1)

    def test_no_silences(self):
        speech = invert_silences_to_speech([], 15.0)
        self.assertEqual(len(speech), 1)
        self.assertEqual(speech[0], (0.0, 15.0))


if __name__ == "__main__":
    unittest.main()

