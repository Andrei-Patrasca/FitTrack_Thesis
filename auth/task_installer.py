"""Installs or removes the FitTrack reminder service as a Windows Task Scheduler task."""
import subprocess
import sys
import os

TASK_NAME = "FitTrackReminderService"


def _service_path():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "auth", "reminder_service.py")


def _run(cmd):
    """Run a schtasks command; return (success, message)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.returncode == 0, result.stderr.strip()
    except Exception as e:
        return False, str(e)


def install_task():
    ok, err = _run([
        "schtasks", "/create",
        "/tn", TASK_NAME,
        "/tr", f'"{sys.executable}" "{_service_path()}"',
        "/sc", "ONLOGON",
        "/rl", "HIGHEST",
        "/f"
    ])
    if ok:
        return True, "Reminder service installed. It will start automatically at next login."
    return False, f"Failed to install: {err}"


def remove_task():
    ok, err = _run(["schtasks", "/delete", "/tn", TASK_NAME, "/f"])
    return (True, "Reminder service removed.") if ok else (False, f"Failed to remove: {err}")


def task_exists():
    ok, _ = _run(["schtasks", "/query", "/tn", TASK_NAME])
    return ok
