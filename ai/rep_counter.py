class RepCounter:
    THRESHOLDS = {
        "bicep_curl": {"down": 160, "up":  50},
        "squat":      {"down": 100, "up": 160},
        "pushup":     {"down":  90, "up": 160},
    }

    def __init__(self):
        self.counts = {k: 0    for k in self.THRESHOLDS}
        self.stages = {k: None for k in self.THRESHOLDS}

    def process(self, exercise, angle):
        if exercise not in self.THRESHOLDS or angle is None:
            return False

        t     = self.THRESHOLDS[exercise]
        stage = self.stages[exercise]
        rep   = False

        if exercise == "bicep_curl":
            if angle > t["down"]:                          self.stages[exercise] = "down"
            if angle < t["up"] and stage == "down":
                self.stages[exercise] = "up"
                self.counts[exercise] += 1
                rep = True
        else:
            if angle < t["down"]:                          self.stages[exercise] = "down"
            if angle > t["up"] and stage == "down":
                self.stages[exercise] = "up"
                self.counts[exercise] += 1
                rep = True

        return rep

    def get_count(self, exercise):
        return self.counts.get(exercise, 0)

    def get_progress(self, exercise, angle):
        if exercise not in self.THRESHOLDS or angle is None:
            return 0.0
        t = self.THRESHOLDS[exercise]
        if exercise == "bicep_curl":
            progress = 1.0 - (angle - t["up"]) / (t["down"] - t["up"])
        else:
            progress = 1.0 - (angle - t["down"]) / (t["up"] - t["down"])
        return max(0.0, min(1.0, progress))

    def reset(self):
        for k in self.counts:
            self.counts[k] = 0
            self.stages[k] = None
