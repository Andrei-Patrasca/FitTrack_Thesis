from ai.keypoints import KEYPOINTS, calculate_angle


class AngleCalculator:
    def get_exercise_angles(self, landmarks, exercise):
        def lm(name):
            return landmarks[KEYPOINTS[name]]

        if exercise in ("bicep_curl", "pushup"):
            left  = calculate_angle(lm("LEFT_SHOULDER"),  lm("LEFT_ELBOW"),  lm("LEFT_WRIST"))
            right = calculate_angle(lm("RIGHT_SHOULDER"), lm("RIGHT_ELBOW"), lm("RIGHT_WRIST"))
        elif exercise == "squat":
            left  = calculate_angle(lm("LEFT_HIP"),  lm("LEFT_KNEE"),  lm("LEFT_ANKLE"))
            right = calculate_angle(lm("RIGHT_HIP"), lm("RIGHT_KNEE"), lm("RIGHT_ANKLE"))
        else:
            return None
        return (left + right) / 2
