import re

def extract_week_number(text):
    """
    Extracts week number like 'Week 46'
    """
    match = re.search(r"Week\s+(\d{1,2})", text, re.IGNORECASE)
    return match.group(1) if match else "UNKNOWN"