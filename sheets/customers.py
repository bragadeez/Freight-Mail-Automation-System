from sheets.base import get_sheets_service
from config.settings import MASTER_SHEET_ID
from config.constants import CUSTOMERS_TAB
from datetime import datetime

REQUIRED_COLUMNS = [
    "Company",
    "Country",
    "Email",
    "Status"
]

def load_active_customers():
    service = get_sheets_service()
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=MASTER_SHEET_ID,
        range=CUSTOMERS_TAB
    ).execute()

    values = result.get("values", [])
    headers = values[0]
    rows = values[1:]

    # Safety validation
    for col in REQUIRED_COLUMNS:
        if col not in headers:
            raise Exception(f"Missing required column: {col}")

    customers = []
    for row in rows:
        record = dict(zip(headers, row))
        if record.get("Status", "").strip().lower() == "active":
            customers.append(record)

    return customers


def update_customer_after_reply(email, category):
    service = get_sheets_service()
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=MASTER_SHEET_ID,
        range=CUSTOMERS_TAB
    ).execute()

    values = result.get("values", [])
    headers = values[0]

    email_idx = headers.index("Email")
    status_idx = headers.index("Status")
    follow_idx = headers.index("Follow-Up Stage")
    response_idx = headers.index("Last Response Date")

    for i, row in enumerate(values[1:], start=2):
        if len(row) > email_idx and row[email_idx].lower() in email.lower():
            row[response_idx] = datetime.now().isoformat()

            if category == "UNSUBSCRIBE" or category == "COMPLAINT":
                row[status_idx] = "Inactive"
            elif category == "ENGAGED":
                row[follow_idx] = "Weekly"
            elif category == "NOT_RELEVANT_NOW":
                row[follow_idx] = "Monthly"

            sheet.values().update(
                spreadsheetId=MASTER_SHEET_ID,
                range=f"{CUSTOMERS_TAB}!A{i}",
                valueInputOption="RAW",
                body={"values": [row]}
            ).execute()
            break