from sheets.base import get_sheets_service
from config.settings import MASTER_SHEET_ID
from config.constants import REGIONS_TAB

def sync_regions(detected_regions, week):
    service = get_sheets_service()
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=MASTER_SHEET_ID,
        range=REGIONS_TAB
    ).execute()

    values = result.get("values", [])
    existing = {row[0] for row in values[1:]} if len(values) > 1 else set()

    new_rows = []
    for region in detected_regions:
        if region not in existing:
            new_rows.append([region, week])

    if new_rows:
        sheet.values().append(
            spreadsheetId=MASTER_SHEET_ID,
            range=REGIONS_TAB,
            valueInputOption="RAW",
            body={"values": new_rows}
        ).execute()
