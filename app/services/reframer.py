from pathlib import Path
from typing import List, Tuple, Optional
from app.core.logger import logger


class FaceReframer:
    """
    Computes horizontal crop centers to reframe 16:9 talking-head footage into 9:16 or 1:1.
    Uses temporal smoothing (Exponential Moving Average) to eliminate jitter.
    """
    def __init__(self, smoothing_alpha: float = 0.15, deadzone_pixels: int = 30):
        self.alpha = smoothing_alpha
        self.deadzone = deadzone_pixels

    def calculate_crop_centers(
        self,
        video_path: Path,
        sample_fps: float = 5.0,
        source_width: int = 1920,
        source_height: int = 1080,
        target_aspect_ratio: str = "9:16"
    ) -> List[Tuple[float, int]]:
        """
        Samples video frames, detects face centers, and calculates smooth crop X offsets.
        Returns a list of (timestamp_seconds, smoothed_crop_x).
        """
        if target_aspect_ratio == "9:16":
            target_width = int(source_height * (9 / 16))  # e.g., 607px out of 1920
        elif target_aspect_ratio == "1:1":
            target_width = source_height                  # 1080px out of 1920
        else:
            target_width = source_width

        default_center_x = (source_width - target_width) // 2

        try:
            import cv2
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                return [(0.0, default_center_x)]

            # Load Haar cascade face detector bundled with OpenCV
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            face_cascade = cv2.CascadeClassifier(cascade_path)

            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            frame_interval = max(1, int(fps / sample_fps))

            smoothed_x = float(default_center_x)
            results = []
            frame_idx = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % frame_interval == 0:
                    timestamp = frame_idx / fps
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5, minSize=(80, 80))

                    if len(faces) > 0:
                        # Pick largest face (the speaker)
                        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                        fx, fy, fw, fh = faces[0]
                        face_center_x = fx + (fw // 2)

                        # Desired crop X such that face is horizontally centered
                        raw_crop_x = face_center_x - (target_width // 2)
                        clamped_x = max(0, min(source_width - target_width, raw_crop_x))

                        # Apply deadband: ignore movements smaller than deadzone
                        if abs(clamped_x - smoothed_x) > self.deadzone:
                            smoothed_x = (self.alpha * clamped_x) + ((1 - self.alpha) * smoothed_x)

                    results.append((timestamp, int(smoothed_x)))

                frame_idx += 1

            cap.release()
            return results if results else [(0.0, default_center_x)]

        except ImportError:
            logger.warning("OpenCV not installed. Using centered crop fallback.")
            return [(0.0, default_center_x)]

