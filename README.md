# FitTrack: AI-Powered Exercise Tracking

**Author:** Pătrașca Andrei Ioan
**Coordinator:** Lect. Dr. Ioan Drăgan
**West University of Timișoara — Faculty of Informatics**
Bachelor Thesis, 2026

---

## Overview

FitTrack is a fully offline desktop application that automatically detects,
classifies, and counts repetitions for three exercises — push-ups, squats,
and biceps curls — using only a standard webcam. It combines YOLOv8-Pose for
body keypoint extraction, a Convolutional Neural Network for automatic
exercise classification, and a joint-angle state machine for repetition
counting, wrapped in a desktop interface with user accounts, persistent
workout history, and daily email reminders.

---

## Repository Structure

```
.
├── main branch/          # The thesis paper, presentation and demo video 
├── master branch/
│   └── FitTrack_2/   # The application source code
│       └── README.md # Detailed setup and usage instructions for the app
└── README.md         # This file
```

- **`main/`** contains the written thesis: the LaTeX source files and the
  final compiled PDF describing the motivation, related work, architecture,
  implementation, and evaluation of the project.

- **`master/FitTrack_2/`** contains the full application source code. This
  is a clean copy of the project: it includes three sample training CSV files
  but excludes private configuration data (such as email credentials) and the
  generated evaluation images. A more detailed **README is located inside this
  folder**, covering installation, dependencies, the Gmail setup required for
  email features, CNN training, and how to run the application.

---

## Quick Start

To run the application, see the detailed instructions in master branch
`FitTrack_2/README.md`. In short:

1. Install Python 3.10 and create a virtual environment.
2. Install the dependencies listed in the project README (in order).
3. Provide a Gmail App Password in a local `config.py` file (for email
   verification and reminders).
4. Run `python main.py`.

---

## Technologies

Python 3.10 · CustomTkinter · YOLOv8-Pose (Ultralytics) · TensorFlow / Keras ·
OpenCV · SQLite · bcrypt · Gmail SMTP

---

## Notes

- The application is designed for Windows and runs fully offline; no workout
  video ever leaves the user's machine.
- The included model and sample data are sufficient to run the application;
  the CNN can be retrained on custom data using the tools described in the
  project README.
