import unittest
from app.services.planner import build_deterministic_plan
from app.models.transcript import TranscriptResult, Segment, WordTimestamp
from app.models.edit_plan import TargetPlatform, AspectRatio


class TestPlanner(unittest.TestCase):
    def test_build_deterministic_plan_instagram(self):
        transcript = TranscriptResult(
            duration=30.0,
            full_text="Welcome to this video tutorial on local development.",
            segments=[
                Segment(
                    id=0,
                    start=0.0,
                    end=4.0,
                    text="Welcome to this video",
                    words=[
                        WordTimestamp(word="Welcome", start=0.0, end=0.8),
                        WordTimestamp(word="to", start=0.8, end=1.2),
                        WordTimestamp(word="this", start=1.2, end=1.8),
                        WordTimestamp(word="video", start=1.8, end=3.0),
                    ]
                ),
                Segment(
                    id=1,
                    start=5.0,
                    end=9.0,
                    text="tutorial on local development.",
                    words=[
                        WordTimestamp(word="tutorial", start=5.0, end=6.0),
                        WordTimestamp(word="on", start=6.0, end=6.5),
                        WordTimestamp(word="local", start=6.5, end=7.2),
                        WordTimestamp(word="development", start=7.2, end=8.8),
                    ]
                )
            ]
        )

        plan = build_deterministic_plan(
            project_id="test1234",
            transcript=transcript,
            platform=TargetPlatform.INSTAGRAM_REEL,
            target_duration=60.0
        )

        self.assertEqual(plan.project_id, "test1234")
        self.assertEqual(plan.aspect_ratio, AspectRatio.RATIO_9_16)
        self.assertEqual(plan.output_resolution.width, 1080)
        self.assertEqual(plan.output_resolution.height, 1920)
        self.assertEqual(len(plan.timeline_cuts), 2)
        self.assertTrue(len(plan.captions.words) > 0)


if __name__ == "__main__":
    unittest.main()

