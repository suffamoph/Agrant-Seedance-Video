import os

try:
    import cv2
except ImportError as exc:
    raise ImportError("mp4_to_frame_rate requires opencv-python. Please install it first.") from exc


class mp4_to_frame_rate:
    CATEGORY = "Agrant/Video"
    RETURN_TYPES = ("INT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("frame_count", "fps", "duration_seconds")
    FUNCTION = "get_frame_info"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {"default": ""}),
            }
        }

    def get_frame_info(self, video_path):
        path = (video_path or "").strip()
        if not path:
            raise ValueError("video_path is empty")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Video file not found: {path}")

        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video file: {path}")

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
        cap.release()

        duration_seconds = float(frame_count / fps) if fps > 0 else 0.0
        return (frame_count, fps, duration_seconds)
