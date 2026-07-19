from collections import deque
from ai.keypoints import KEYPOINTS, calculate_angle


class ExerciseClassifier:
    _HISTORY_SIZE = 15

    def __init__(self):
        self.history          = deque(maxlen=self._HISTORY_SIZE)
        self.current_exercise = None

    def _lm(self, landmarks, name):
        return landmarks[KEYPOINTS[name]]

    def classify(self, landmarks):
        if landmarks is None or len(landmarks) < 17:
            return "unknown"
        try:
            g = lambda n: self._lm(landmarks, n)
            shoulder_y = (g("LEFT_SHOULDER").y + g("RIGHT_SHOULDER").y) / 2
            hip_y      = (g("LEFT_HIP").y      + g("RIGHT_HIP").y)      / 2
            torso_diff = abs(hip_y - shoulder_y)
            knee_angle = (calculate_angle(g("LEFT_HIP"),      g("LEFT_KNEE"),  g("LEFT_ANKLE")) +
                          calculate_angle(g("RIGHT_HIP"),     g("RIGHT_KNEE"), g("RIGHT_ANKLE"))) / 2
            hip_angle  = (calculate_angle(g("LEFT_SHOULDER"), g("LEFT_HIP"),   g("LEFT_KNEE")) +
                          calculate_angle(g("RIGHT_SHOULDER"),g("RIGHT_HIP"),  g("RIGHT_KNEE"))) / 2

            if torso_diff < 0.15:
                prediction = "pushup"
            elif knee_angle < 145 and torso_diff > 0.15:
                prediction = "squat"
            elif knee_angle > 150 and hip_angle > 150 and torso_diff > 0.15:
                prediction = "bicep_curl"
            else:
                prediction = "unknown"
        except Exception:
            prediction = "unknown"

        self.history.append(prediction)
        self.current_exercise = max(set(self.history), key=self.history.count)
        return self.current_exercise

    def get_display_name(self, exercise):
        return {
            "pushup":     "Push-up",
            "squat":      "Squat",
            "bicep_curl": "Bicep Curl",
            "unknown":    "No exercise detected"
        }.get(exercise, "Unknown")

    def reset(self):
        self.history.clear()
        self.current_exercise = None
