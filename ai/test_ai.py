import cv2
from ai.pose_estimator import PoseEstimator
from ai.angle_calculator import AngleCalculator
from ai.rep_counter import RepCounter
from ai.exercise_classifier import ExerciseClassifier

estimator  = PoseEstimator()
calculator = AngleCalculator()
counter    = RepCounter()
classifier = ExerciseClassifier()

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
print("Press Q to quit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame, landmarks = estimator.process_frame(frame)
    exercise = classifier.classify(landmarks)

    if landmarks and exercise != "unknown":
        angle    = calculator.get_exercise_angles(landmarks, exercise)
        rep_done = counter.process(exercise, angle)
        if rep_done:
            print(f"Rep! {exercise}: {counter.get_count(exercise)}")

    cv2.putText(frame, f"Exercise: {classifier.get_display_name(exercise)}",
                (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                (57, 255, 20), 2)

    cv2.imshow("AI Test", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()