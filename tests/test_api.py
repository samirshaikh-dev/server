import unittest
import io
from fastapi.testclient import TestClient
from main import app


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "online")
        self.assertIn("ffmpeg_bin", data)

    def test_upload_and_get_project(self):
        # Create a mock video file payload
        fake_video_content = b"fake video bytes for testing"
        file_obj = io.BytesIO(fake_video_content)

        response = self.client.post(
            "/api/projects/upload",
            files={"file": ("test_clip.mp4", file_obj, "video/mp4")}
        )
        self.assertEqual(response.status_code, 200)
        proj = response.json()
        self.assertIn("project_id", proj)
        self.assertEqual(proj["filename"], "test_clip.mp4")

        # Test project status retrieval
        proj_id = proj["project_id"]
        status_res = self.client.get(f"/api/projects/{proj_id}")
        self.assertEqual(status_res.status_code, 200)
        self.assertEqual(status_res.json()["project_id"], proj_id)


if __name__ == "__main__":
    unittest.main()

