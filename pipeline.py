import os
import time
import re

from utils.logger import setup_logger
from docx_processing.docx_region_extractor import split_docx_to_regions

from sheets.customers import load_active_customers, update_customer_after_reply
from sheets.regions import sync_regions
from sheets.logs import log_email

from mapping.customer_region_mapper import map_customer_to_regions

from mailer.sender import send_email
from mailer.reply_reader import read_recent_replies
from mailer.reply_categorizer import categorize_reply

from config.settings import EMAIL_BATCH_SIZE


def get_week_from_filename(path):
    m = re.search(r"Week\s*(\d+)", path)
    return m.group(1) if m else "UNKNOWN"


def get_last_name(name):

    if not name:
        return "Customer"

    parts = name.strip().split()

    return parts[-1]


def personalize_greeting(html, contact_name):

    last_name = get_last_name(contact_name)

    greeting = f"Dear {last_name},"

    html = re.sub(
        r"Dear\s+(Valued\s+Customer|Customer|Valued\s+Client)[,]?",
        greeting,
        html,
        flags=re.IGNORECASE
    )

    return html


def run_pipeline(docx_path):

    logger = setup_logger()

    week = get_week_from_filename(docx_path)

    regions_html = split_docx_to_regions(docx_path)

    subject_regions = list(regions_html.keys())

    sync_regions(subject_regions, week)

    customers = load_active_customers()

    mailing_plan = []

    for customer in customers:

        customer_regions = map_customer_to_regions(
            customer,
            subject_regions
        )

        if "UNKNOWN" in customer_regions:
            continue

        mailing_plan.append({
            "Company": customer.get("Company"),
            "Contact Name": customer.get("Contact Name"),
            "Email": customer.get("Email"),
            "Regions": customer_regions
        })

    logs = []

    sent_count = 0
    processed_pairs = set()

    for item in mailing_plan:

        email = item["Email"]
        company = item["Company"]
        contact_name = item.get("Contact Name", "")
        regions = item["Regions"]

        for region in regions:

            pair = (email, region)

            if pair in processed_pairs:
                continue

            processed_pairs.add(pair)

            html_body = regions_html.get(region)

            html_body = personalize_greeting(
                html_body,
                contact_name
            )

            subject = f"Week {week} – {region} Freight Market Update | {company}"

            success, error = send_email(email, subject, html_body)

            log_email(
                week=week,
                region=region,
                company=company,
                email=email,
                status="Sent" if success else "Failed",
                error=error
            )

            if success:
                logs.append(f"✓ Email sent to {email} | {region}")
            else:
                logs.append(f"✗ Email failed to {email}")

            sent_count += 1

            if EMAIL_BATCH_SIZE and sent_count % EMAIL_BATCH_SIZE == 0:
                time.sleep(10)

    return logs


def process_replies():

    logs = []

    replies = read_recent_replies(days=7)

    for reply in replies:

        category = categorize_reply(reply["body"])

        update_customer_after_reply(
            reply["from"],
            category
        )

        logs.append(f"{reply['from']} -> {category}")

    return logs