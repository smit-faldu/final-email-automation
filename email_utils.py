# email_utils.py
from flask import session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from apscheduler.schedulers.background import BackgroundScheduler
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime, math
import re
from email.mime.multipart import MIMEMultipart

scheduler = BackgroundScheduler()
scheduler.start()
import json, os

def log_sent_email(data, filepath="sent_log.json"):
    logs = []
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            logs = json.load(f)
    logs.append(data)
    with open(filepath, "w") as f:
        json.dump(logs, f, indent=2)

def get_gmail_service():
    creds_dict = session.get('credentials')
    if not creds_dict:
        raise RuntimeError("User not authenticated. No credentials in session.")

    creds = Credentials(**creds_dict)
    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(sender, to_emails, subject, body, use_bcc=True):
    message = MIMEMultipart()
    message["from"] = sender
    message["subject"] = subject

    if use_bcc:
        message["to"] = sender  # dummy 'To' field
        message["bcc"] = ", ".join(to_emails)
    else:
        message["to"] = ", ".join(to_emails)

    message.attach(MIMEText(body, "plain"))
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return raw


def send_email(subject, body, to_emails, creds_dict=None, investor_name=None):
    if creds_dict is None:
        creds_dict = session.get("credentials")
        if not creds_dict:
            raise RuntimeError("User not authenticated. No credentials in session.")

    creds = Credentials(**creds_dict)
    service = build("gmail", "v1", credentials=creds)

    profile = service.users().getProfile(userId="me").execute()
    sender_email = profile["emailAddress"]

    # Use BCC if multiple recipients, else use TO
    use_bcc = len(to_emails) > 1
    message = {
        "raw": create_message(sender_email, to_emails, subject, body, use_bcc=use_bcc)
    }

    service.users().messages().send(userId="me", body=message).execute()

    # Log the sent email
    log_sent_email({
        "to": to_emails,
        "subject": subject,
        "body": body,
        "investor_name": investor_name,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })


def save_draft(subject, body, to_emails):
    creds_dict = session.get("credentials")
    if not creds_dict:
        raise RuntimeError("User not authenticated. No credentials in session.")

    creds = Credentials(**creds_dict)
    service = build("gmail", "v1", credentials=creds)

    raw_message = create_message("me", to_emails, subject, body, use_bcc=(len(to_emails) > 1))
    message = {'raw': raw_message}
    draft = {'message': message}
    service.users().drafts().create(userId="me", body=draft).execute()


def scheduled_send(subject, body, to_emails, creds_dict):
    send_email(subject, body, to_emails, creds_dict)


def schedule_batch_emails(subject, body, to_emails, batch_count):
    creds_dict = session.get("credentials")
    total = len(to_emails)
    batches = [to_emails[i:i + batch_count] for i in range(0, total, batch_count)]

    for day_offset, batch in enumerate(batches):
        run_time = datetime.datetime.now() + datetime.timedelta(days=day_offset)
        job_id = f"{run_time.timestamp()}-{day_offset+1}"
        scheduler.add_job(
            func=scheduled_send,
            trigger='date',
            run_date=run_time,
            id=job_id,
            kwargs={
                "subject": subject,
                "body": body,
                "to_emails": batch,
                "creds_dict": creds_dict
            }
        )


def schedule_all_at_once(subject, body, to_emails, run_time):
    creds_dict = session.get("credentials")
    job_id = f"{run_time.timestamp()}-all"
    scheduler.add_job(
        func=scheduled_send,
        trigger='date',
        run_date=run_time,
        id=job_id,
        kwargs={
            "subject": subject,
            "body": body,
            "to_emails": to_emails,
            "creds_dict": creds_dict
        }
    )


def get_scheduled_emails():
    return [
        {
            "id": job.id,
            "next_run_time": str(job.next_run_time),
            "subject": job.kwargs.get("subject", ""),
            "body": job.kwargs.get("body", "")[:100],
            "to_emails": job.kwargs.get("to_emails", [])
        }
        for job in scheduler.get_jobs()
    ]


def get_all_sent_to_emails(filepath="sent_log.json"):
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        logs = json.load(f)
    emails = set()
    for entry in logs:
        if isinstance(entry["to"], list):
            emails.update(entry["to"])
        else:
            emails.add(entry["to"])
    return emails


def fetch_replies(creds_dict):
    creds = Credentials(**creds_dict)
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(userId="me", q="is:inbox").execute()
    messages = results.get("messages", [])

    sent_to_emails = get_all_sent_to_emails()

    replies = []
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg['id']).execute()
        headers = msg_data.get("payload", {}).get("headers", [])

        from_email = next((h["value"] for h in headers if h["name"] == "From"), "")
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), None)

        if not subject or "Re:" not in subject:
            continue

        match = re.search(r'<(.+?)>', from_email)
        email_only = match.group(1) if match else from_email

        if email_only in sent_to_emails:
            replies.append({
                "from": from_email,
                "subject": subject,
                "snippet": msg_data.get("snippet", ""),
                "timestamp": int(msg_data.get("internalDate"))
            })

    return replies

def schedule_individual_email(subject, body, to_email, run_time):
    creds_dict = session.get("credentials")
    job_id = f"{run_time.timestamp()}-{to_email}"

    scheduler.add_job(
        func=scheduled_send,
        trigger='date',
        run_date=run_time,
        id=job_id,
        kwargs={
            "subject": subject,
            "body": body,
            "to_emails": [to_email],
            "creds_dict": creds_dict
        }
    )