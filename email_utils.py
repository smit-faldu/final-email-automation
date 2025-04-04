# email_utils.py
from flask import session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from apscheduler.schedulers.background import BackgroundScheduler
import base64
from email.mime.text import MIMEText

scheduler = BackgroundScheduler()
scheduler.start()

def get_gmail_service():
    creds_dict = session.get('credentials')
    if not creds_dict:
        raise RuntimeError("User not authenticated. No credentials in session.")

    creds = Credentials(**creds_dict)
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to_emails, subject, body_text):
    to_header = ", ".join(to_emails) if isinstance(to_emails, list) else to_emails
    message = MIMEText(body_text, "plain")
    message["to"] = to_header
    message["from"] = sender
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return raw
def send_email(subject, body, to_emails):
    creds_dict = session.get("credentials")
    if not creds_dict:
        raise RuntimeError("User not authenticated. No credentials in session.")
    
    creds = Credentials(**creds_dict)
    service = build("gmail", "v1", credentials=creds)

    message = {
        "raw": create_message("me", to_emails, subject, body)
    }

    service.users().messages().send(userId="me", body=message).execute()
    
def save_draft(subject, body):
    service = get_gmail_service()
    message = create_message(subject, body)
    draft = {'message': message}
    service.users().drafts().create(userId="me", body=draft).execute()

def schedule_email(subject, body, delay=60):  # delay in seconds
    scheduler.add_job(lambda: send_email(subject, body), 'date')
