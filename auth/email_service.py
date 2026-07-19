import smtplib
import random
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_SMTP, EMAIL_PORT


def is_valid_email_format(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email))


def generate_code():
    return str(random.randint(100000, 999999))


def _send(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        return True, "sent"
    except smtplib.SMTPAuthenticationError:
        return False, "Email authentication failed. Check your App Password in config.py."
    except smtplib.SMTPException as e:
        return False, f"Email error: {e}"
    except Exception as e:
        return False, f"Could not send email: {e}"


def send_verification_email(to_email, code):
    return _send(
        to_email,
        "FitTrack — Verify your email",
        f"Welcome to FitTrack.\n\nYour verification code is:\n\n    {code}\n\n"
        f"Enter it in the app to complete registration. Expires in 10 minutes.\n\n"
        f"— The FitTrack Team"
    )


def send_reminder_email(to_email, username, reminder_time):
    return _send(
        to_email,
        "FitTrack — Time to work out!",
        f"Hey {username}!\n\nThis is your daily reminder to work out at {reminder_time}.\n\n"
        f"Open FitTrack and start your session. Let's go!\n\n— The FitTrack Team"
    )
