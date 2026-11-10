import unittest
from app.models.edit_plan import EditPlan, TimelineCut, TargetPlatform, AspectRatio
from app.models.project import ProjectMetadata, JobStatus


class TestModels(unittest.TestCase):
    def test_edit_plan_serialization(self):
        plan = EditPlan(
            project_id="abc123",
            target_platform=TargetPlatform.LINKEDIN_POST,
            aspect_ratio=AspectRatio.RATIO_1_1,
            timeline_cuts=[
                TimelineCut(cut_id=1, source_start=1.0, source_end=5.5, zoom_scale=1.15)
            ]
        )

        json_str = plan.model_dump_json()
        self.assertIn('"project_id":"abc123"', json_str)
        self.assertIn('"aspect_ratio":"1:1"', json_str)

        # Deserialize back
        reconstructed = EditPlan.model_validate_json(json_str)
        self.assertEqual(reconstructed.project_id, "abc123")
        self.assertEqual(reconstructed.timeline_cuts[0].zoom_scale, 1.15)

    def test_project_metadata(self):
        meta = ProjectMetadata(
            project_id="proj99",
            filename="talking_head.mp4",
            status=JobStatus.UPLOADING
        )
        self.assertEqual(meta.status, JobStatus.UPLOADING)
        self.assertEqual(meta.filename, "talking_head.mp4")


if __name__ == "__main__":
    unittest.main()

