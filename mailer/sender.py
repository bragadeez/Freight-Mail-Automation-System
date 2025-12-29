import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from utils.google_auth import get_credentials
from config.settings import SYSTEM_EMAIL, EMAIL_RETRY_LIMIT
import time

def send_email(to_email, subject, body):
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body)
    message["to"] = to_email
    message["from"] = SYSTEM_EMAIL
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    for attempt in range(EMAIL_RETRY_LIMIT):
        try:
            service.users().messages().send(
                userId="me",
                body={"raw": raw}
            ).execute()
            return True, ""
        except Exception as e:
            if attempt == EMAIL_RETRY_LIMIT - 1:
                return False, str(e)
            time.sleep(2)

    return False, "Unknown error"
