import numpy as np

# Shared keypoint index map
KEYPOINTS = {
    "NOSE":           0,
    "LEFT_SHOULDER":  5,  "RIGHT_SHOULDER": 6,
    "LEFT_ELBOW":     7,  "RIGHT_ELBOW":    8,
    "LEFT_WRIST":     9,  "RIGHT_WRIST":   10,
    "LEFT_HIP":      11,  "RIGHT_HIP":     12,
    "LEFT_KNEE":     13,  "RIGHT_KNEE":    14,
    "LEFT_ANKLE":    15,  "RIGHT_ANKLE":   16,
}


def calculate_angle(a, b, c):
    a = np.array([a.x, a.y])
    b = np.array([b.x, b.y])
    c = np.array([c.x, c.y])
    ba, bc = a - b, c - b
    cos = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))
