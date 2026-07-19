import numpy as np
import os
from collections import deque
from ai.keypoints import KEYPOINTS, calculate_angle

MODEL_PATH        = os.path.join(os.path.dirname(__file__), "exercise_model.keras")
LABELS_PATH       = os.path.join(os.path.dirname(__file__), "label_classes.npy")
CONFIDENCE_THRESH = 0.7
HISTORY_SIZE      = 15


class ExerciseClassifierCNN:
    def __init__(self):
        self.history          = deque(maxlen=HISTORY_SIZE)
        self.current_exercise = None
        self.model            = None
        self.classes          = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(LABELS_PATH):
            import tensorflow as tf
            self.model   = tf.keras.models.load_model(MODEL_PATH)
            self.classes = np.load(LABELS_PATH, allow_pickle=True)
            print(f"CNN classifier loaded. Classes: {self.classes}")
        else:
            print("No trained model found — using rule-based classifier.")

    def classify(self, landmarks):
        if landmarks is None or len(landmarks) < 17:
            return "unknown"

        if self.model is not None:
            features = np.array(
                [[lm.x, lm.y, lm.z] for lm in landmarks], dtype=np.float32
            ).flatten().reshape(1, -1)
            probs      = self.model.predict(features, verbose=0)[0]
            confidence = np.max(probs)
            prediction = (self.classes[np.argmax(probs)]
                          if confidence >= CONFIDENCE_THRESH else "unknown")
        else:
            prediction = self._rule_based(landmarks)

        self.history.append(prediction)
        self.current_exercise = max(set(self.history), key=self.history.count)
        return self.current_exercise

    def _rule_based(self, landmarks):
        try:
            g = lambda n: landmarks[KEYPOINTS[n]]
            shoulder_y = (g("LEFT_SHOULDER").y + g("RIGHT_SHOULDER").y) / 2
            hip_y      = (g("LEFT_HIP").y      + g("RIGHT_HIP").y)      / 2
            torso_diff = abs(hip_y - shoulder_y)
            knee_angle = (calculate_angle(g("LEFT_HIP"),      g("LEFT_KNEE"),  g("LEFT_ANKLE")) +
                          calculate_angle(g("RIGHT_HIP"),     g("RIGHT_KNEE"), g("RIGHT_ANKLE"))) / 2
            hip_angle  = (calculate_angle(g("LEFT_SHOULDER"), g("LEFT_HIP"),   g("LEFT_KNEE")) +
                          calculate_angle(g("RIGHT_SHOULDER"),g("RIGHT_HIP"),  g("RIGHT_KNEE"))) / 2

            if torso_diff < 0.15:                           return "pushup"
            elif knee_angle < 145:                          return "squat"
            elif knee_angle > 150 and hip_angle > 150:      return "bicep_curl"
            else:                                           return "unknown"
        except Exception:
            return "unknown"

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
