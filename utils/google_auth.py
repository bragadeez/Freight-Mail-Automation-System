import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

def get_credentials():
    creds = None
    token_path = "credentials/token.json"
    cred_path = "credentials/credentials.json"

    # Try loading existing token safely
    if os.path.exists(token_path):
        try:
            with open(token_path, "r") as f:
                json.load(f)  # validate JSON
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except Exception:
            # Token is corrupt → delete it
            os.remove(token_path)
            creds = None

    # Refresh or create new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return creds
