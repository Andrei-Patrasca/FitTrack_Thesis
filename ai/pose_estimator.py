import cv2
import numpy as np
from ultralytics import YOLO


class KeypointProxy:
    def __init__(self, x, y, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)


class PoseEstimator:
    # Body skeleton connections (no face/bounding box)
    SKELETON_CONNECTIONS = [
        (5, 6), (5, 11), (6, 12), (11, 12),  # torso
        (5, 7), (7, 9),                        # left arm
        (6, 8), (8, 10),                       # right arm
        (11, 13), (13, 15),                    # left leg
        (12, 14), (14, 16),                    # right leg
    ]

    def __init__(self):
        self.model = YOLO("yolov8n-pose.pt")

    def process_frame(self, frame):
        results   = self.model(frame, verbose=False)
        landmarks = None
        annotated = frame.copy()

        if results and results[0].keypoints is not None and len(results[0].keypoints.xy) > 0:
            result = results[0]
            h, w   = frame.shape[:2]
            kp_xy  = result.keypoints.xy[0].cpu().numpy()
            kp_conf= result.keypoints.conf[0].cpu().numpy()

            landmarks = [
                KeypointProxy(kp_xy[i][0] / w, kp_xy[i][1] / h, float(kp_conf[i]))
                for i in range(len(kp_xy))
            ]
            self._draw_skeleton(annotated, kp_xy, kp_conf)

        return annotated, landmarks

    def _draw_skeleton(self, frame, kp_xy, kp_conf):
        for a, b in self.SKELETON_CONNECTIONS:
            if kp_conf[a] > 0.4 and kp_conf[b] > 0.4:
                cv2.line(frame,
                         (int(kp_xy[a][0]), int(kp_xy[a][1])),
                         (int(kp_xy[b][0]), int(kp_xy[b][1])),
                         (57, 255, 20), 2)
        for i in range(5, len(kp_xy)):  # skip face keypoints 0–4
            if kp_conf[i] > 0.4:
                x, y = int(kp_xy[i][0]), int(kp_xy[i][1])
                cv2.circle(frame, (x, y), 5, (255, 255, 255), -1)
                cv2.circle(frame, (x, y), 7, (57, 255, 20), 2)

    def close(self):
        pass
