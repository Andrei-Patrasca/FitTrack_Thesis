"""
P = pushup mode
S = squat mode
C = bicep_curl mode
SPACE = start/stop recording
 Q = quit and save
"""
import cv2
import csv
import os
from datetime import datetime
from ai.pose_estimator import PoseEstimator

LABELS   = {"p": "pushup", "s": "squat", "c": "bicep_curl"}
DATA_DIR = os.path.join(os.path.dirname(__file__), "training_data")
os.makedirs(DATA_DIR, exist_ok=True)

estimator   = PoseEstimator()
cap         = cv2.VideoCapture(0, cv2.CAP_DSHOW)
recording   = False
current_lbl = "pushup"
rows        = []

print("Controls: P=pushup  S=squat  C=curl  SPACE=record  Q=quit+save")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame, landmarks = estimator.process_frame(frame)

    if landmarks and recording:
        row = [current_lbl]
        for lm in landmarks:
            row += [lm.x, lm.y, lm.z]
        rows.append(row)

    # Overlay
    color = (0, 255, 0) if recording else (0, 0, 255)
    cv2.putText(frame,
                f"{'● REC' if recording else '○ PAUSED'}  |  {current_lbl.upper()}  |  {len(rows)} frames",
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    cv2.imshow("Data Collection", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break
    elif key == ord(" "):
        recording = not recording
        print(f"Recording: {recording}")
    elif key == ord("p"):
        current_lbl = "pushup"
        print("Mode: pushup")
    elif key == ord("s"):
        current_lbl = "squat"
        print("Mode: squat")
    elif key == ord("c"):
        current_lbl = "bicep_curl"
        print("Mode: bicep_curl")

cap.release()
cv2.destroyAllWindows()
estimator.close()

# Save to CSV
if rows:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(DATA_DIR, f"data_{timestamp}.csv")
    header = ["label"] + [f"{j}_{a}"
              for j in range(17)
              for a in ["x", "y", "z"]]
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Saved {len(rows)} frames to {path}")
else:
    print("No data recorded.")