# 💪 FitTrack — AI-Powered Exercise Tracker

A real-time desktop fitness tracking application using computer vision and deep learning.
Automatically detects, classifies, and counts repetitions for **push-ups**, **squats**, and **bicep curls** using only a standard webcam.

---

## Requirements

- **OS:** Windows 10 / 11
- **Python:** 3.10.x (exactly — not 3.11 or 3.12)
- **Webcam:** Any standard USB or built-in webcam
- **GPU (optional):** NVIDIA GPU for faster YOLOv8 inference (works on CPU too)
- **Gmail account:** Required for email verification and workout reminders (App Password needed)

---

## Installation

### 1. Clone or download the project

Place the project folder anywhere on your machine, e.g.:
```
C:\Users\YourName\PythonProjects\FitTrack
```

### 2. Create a virtual environment

Open a terminal inside the project folder and run:
```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

Run these commands **in order** — order matters due to numpy compatibility:

```
pip install numpy==1.25.2
pip install customtkinter==5.2.2
pip install opencv-python==4.9.0.80
pip install ultralytics
pip install pillow
pip install bcrypt==4.1.2
pip install schedule==1.2.1
```

For CNN training only (optional — needed only to retrain the classifier):
```
pip install tensorflow-cpu==2.13.0
pip install scikit-learn
pip install pandas
```

> ⚠️ **Important:** If numpy ever upgrades automatically (e.g. after installing ultralytics or tensorflow),
> run `pip install numpy==1.24.3` again to pin it back. A wrong numpy version causes an
> `ImportError: numpy.core.multiarray failed to import` crash.

---

## Gmail App Password Setup

The app sends emails via Gmail SMTP. You need a Gmail **App Password** (not your real password).

1. Go to https://myaccount.google.com/security
2. Enable **2-Step Verification** if not already on
3. Go to https://myaccount.google.com/apppasswords
4. Select **Mail** + **Windows Computer** → Generate
5. Copy the 16-character password

Then open `config.py` in the project root and fill in:
```python
EMAIL_SENDER   = "your_gmail@gmail.com"
EMAIL_PASSWORD = "xxxx xxxx xxxx xxxx"   # your App Password
EMAIL_SMTP     = "smtp.gmail.com"
EMAIL_PORT     = 587
```

---

## Running the App

Make sure your virtual environment is active, then:
```
python main.py
```

The app will:
- Create `fittrack.db` automatically on first run
- Download `yolov8n-pose.pt` automatically on first workout session (~6MB)

---

## Project Structure

```
FitTrack/
├── main.py                        # App entry point
├── config.py                      # Email credentials (never share this)
├── fittrack.db                    # SQLite database (auto-created)
│
├── database/
│   ├── db.py                      # Database connection and table setup
│   ├── models.py                  # Data models
│   └── workout_manager.py         # Workout CRUD operations
│
├── auth/
│   ├── auth_manager.py            # Login, register, update user
│   ├── email_service.py           # Send verification and reminder emails
│   ├── reminder_service.py        # Background service — checks time and sends reminders
│   └── task_installer.py          # Installs/removes Windows Task Scheduler entry
│
├── ai/
│   ├── pose_estimator.py          # YOLOv8 pose estimation, keypoint extraction
│   ├── angle_calculator.py        # Joint angle math
│   ├── rep_counter.py             # State machine rep counting
│   ├── exercise_classifier.py     # Exercise classification (rule-based or CNN)
│   ├── collect_training_data.py   # Record training data for CNN
│   ├── train_classifier.py        # Train the CNN classifier
│   ├── training_data/             # CSV files from recording sessions
│   ├── exercise_model.keras       # Trained CNN model (created after training)
│   └── label_classes.npy          # Label mapping (created after training)
│
└── ui/
    ├── styles.py                  # Colors and fonts
    ├── login_screen.py
    ├── register_screen.py
    ├── verify_email_screen.py
    ├── dashboard_screen.py
    ├── workout_screen.py
    ├── history_screen.py
    └── account_screen.py
```

---

## CNN Classifier Training (Optional)

The app ships with a rule-based classifier that works out of the box.
To train a more accurate CNN classifier on your own data:

### Step 1 — Collect training data
```
python ai/collect_training_data.py
```
Controls:
- `P` — switch to push-up mode
- `S` — switch to squat mode
- `C` — switch to bicep curl mode
- `SPACE` — start / stop recording
- `Q` — quit and save CSV

Record at least **200–300 frames per exercise**. Run multiple sessions for better accuracy.
Each session saves a new CSV to `ai/training_data/` — all are combined during training.

### Step 2 — Train the model
```
python ai/train_classifier.py
```
This reads all CSVs from `ai/training_data/`, trains the CNN, and saves:
- `ai/exercise_model.keras`
- `ai/label_classes.npy`

### Step 3 — Restart the app
The classifier automatically detects the trained model and switches from rules to CNN.
No other changes needed.

---

## Email Reminder Service (Windows)

The reminder service runs as a Windows background task and sends a daily workout email at your chosen time.

### Install the service
1. Run PyCharm (or terminal) **as Administrator**
2. Open the app → Account Settings → click **Install Background Service**
3. The service will auto-start on every Windows login

### Remove the service
Account Settings → click **Remove Service**

### Manual run (for testing)
```
python auth/reminder_service.py
```

---

## Known Issues & Notes

| Issue | Fix |
|---|---|
| `numpy.core.multiarray failed to import` | Run `pip install numpy==1.24.3` |
| Camera not found | Make sure no other app is using the webcam |
| Email not sending | Check `config.py` credentials and App Password |
| Install Service fails | Run terminal or PyCharm as Administrator |
| YOLOv8 slow on first run | Model downloads once (~6MB), subsequent runs are fast |

---

## Dependencies Summary

| Package | Version | Purpose |
|---|---|---|
| customtkinter | 5.2.2 | Modern desktop UI |
| opencv-python | 4.9.0.80 | Webcam capture and image processing |
| ultralytics | latest | YOLOv8 pose estimation |
| numpy | 1.24.3 | Numerical operations (must stay at this version) |
| pillow | latest | Image conversion for UI display |
| bcrypt | 4.1.2 | Password hashing |
| schedule | 1.2.1 | Task scheduling |
| tensorflow-cpu | 2.13.0 | CNN classifier training (optional) |
| scikit-learn | latest | Label encoding for training (optional) |
| pandas | latest | CSV loading for training (optional) |