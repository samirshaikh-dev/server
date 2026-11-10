import unittest
import tempfile
from pathlib import Path
from app.services.captioner import format_ass_time, generate_ass_subtitles
from app.models.edit_plan import CaptionsConfig, CaptionWord


class TestCaptioner(unittest.TestCase):
    def test_format_ass_time(self):
        # 1 hr, 2 mins, 3.45 secs = 1:02:03.45
        t = 3600 + 120 + 3.45
        formatted = format_ass_time(t)
        self.assertEqual(formatted, "1:02:03.45")

        # 0 secs
        self.assertEqual(format_ass_time(0.0), "0:00:00.00")

    def test_generate_ass_subtitles(self):
        cfg = CaptionsConfig(
            words=[
                CaptionWord(word="Build", start=0.5, end=0.9, is_highlight=True),
                CaptionWord(word="fast", start=1.0, end=1.4),
                CaptionWord(word="videos", start=1.5, end=2.0)
            ]
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "test.ass"
            result_path = generate_ass_subtitles(cfg, out_path, words_per_batch=3)
            self.assertTrue(result_path.is_file())

            content = result_path.read_text(encoding="utf-8")
            self.assertIn("[Script Info]", content)
            self.assertIn("PlayResY: 1920", content)
            self.assertIn("BUILD", content)
            self.assertIn("VIDEOS", content)


if __name__ == "__main__":
    unittest.main()

