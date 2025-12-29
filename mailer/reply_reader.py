from googleapiclient.discovery import build
from utils.google_auth import get_credentials
import base64

def read_recent_replies(days=7):
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    query = (
        f"is:inbox newer_than:{days}d "
        f"subject:(Weekly Freight Market Update)"
    )

    response = service.users().messages().list(
        userId="me",
        q=query
    ).execute()

    messages = response.get("messages", [])
    replies = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        headers = msg_data["payload"]["headers"]
        body = ""

        for part in msg_data["payload"].get("parts", []):
            if part["mimeType"] == "text/plain":
                body = base64.urlsafe_b64decode(
                    part["body"]["data"]
                ).decode("utf-8", errors="ignore")

        sender = next(
            (h["value"] for h in headers if h["name"] == "From"),
            ""
        )

        replies.append({
            "from": sender,
            "body": body
        })

    return replies
