from sheets.base import get_sheets_service
from config.settings import MASTER_SHEET_ID
from config.constants import LOGS_TAB
from datetime import datetime

def log_email(week, region, company, email, status, error=""):
    service = get_sheets_service()
    sheet = service.spreadsheets()

    row = [
        week,
        region,
        company,
        email,
        status,
        datetime.now().isoformat(),
        error
    ]

    sheet.values().append(
        spreadsheetId=MASTER_SHEET_ID,
        range=LOGS_TAB,
        valueInputOption="RAW",
        body={"values": [row]}
    ).execute()

def log_unknown_mapping(week, company, email, country):
    log_email(
        week,
        "UNKNOWN",
        company,
        email,
        "Skipped",
        f"No region mapping for country: {country}"
    )
