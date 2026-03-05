import os
import time

from utils.logger import setup_logger
from utils.text_utils import extract_week_number

from docx_processing.docx_region_extractor import split_docx_to_regions

from sheets.customers import load_active_customers, update_customer_after_reply
from sheets.regions import sync_regions
from sheets.logs import log_email

from mapping.customer_region_mapper import map_customer_to_regions

from mailer.sender import send_email
from mailer.reply_reader import read_recent_replies
from mailer.reply_categorizer import categorize_reply

from config.settings import EMAIL_BATCH_SIZE


# --------------------------------------------------
# Helper: Get latest DOCX file
# --------------------------------------------------
def get_latest_docx(directory):

    files = [
        f for f in os.listdir(directory)
        if f.lower().endswith(".docx")
    ]

    if not files:
        raise FileNotFoundError("No DOCX found in input directory")

    files.sort(
        key=lambda f: os.path.getmtime(os.path.join(directory, f)),
        reverse=True
    )

    return os.path.join(directory, files[0])


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------
def main():

    logger = setup_logger()
    logger.info("=== Freight Market Automation Started ===")

    # --------------------------------------------------
    # STEP 1: Load latest DOCX report
    # --------------------------------------------------
    try:
        docx_path = get_latest_docx("data/input_reports")
        logger.info(f"Using DOCX: {docx_path}")
    except Exception as e:
        logger.error(f"Failed to locate DOCX report: {e}")
        return

    # --------------------------------------------------
    # STEP 2: Extract week number
    # --------------------------------------------------
    try:
        week = extract_week_number(docx_path)
    except Exception:
        week = "UNKNOWN"

    logger.info(f"Detected Week: {week}")

    # --------------------------------------------------
    # STEP 3: Extract regions from DOCX
    # --------------------------------------------------
    logger.info("Extracting regions from DOCX")

    try:
        regions_html = split_docx_to_regions(docx_path)
    except Exception as e:
        logger.error(f"Failed to extract regions from DOCX: {e}")
        return

    if not regions_html:
        logger.error("No regions detected — aborting")
        return

    subject_regions = list(regions_html.keys())

    logger.info(f"Regions detected: {subject_regions}")

    # --------------------------------------------------
    # STEP 4: Sync regions to Google Sheets
    # --------------------------------------------------
    try:
        sync_regions(subject_regions, week)
        logger.info("Region_Master sheet synced successfully")
    except Exception as e:
        logger.error(f"Failed to sync Region_Master: {e}")
        return

    # --------------------------------------------------
    # STEP 5: Load active customers
    # --------------------------------------------------
    customers = load_active_customers()

    if not customers:
        logger.warning("No active customers found — nothing to process")
        return

    logger.info(f"Loaded {len(customers)} active customers")

    # --------------------------------------------------
    # STEP 6: Customer → Region Mapping
    # --------------------------------------------------
    mailing_plan = []

    for customer in customers:

        customer_regions = map_customer_to_regions(
            customer,
            subject_regions
        )

        if "UNKNOWN" in customer_regions:
            logger.warning(
                f"Skipping customer due to unknown region mapping: "
                f"{customer.get('Company')} | {customer.get('Email')} "
                f"| Country: {customer.get('Country')}"
            )
            continue

        mailing_plan.append({
            "Company": customer.get("Company"),
            "Contact Name": customer.get("Contact Name"),
            "Email": customer.get("Email"),
            "Regions": customer_regions
        })

    logger.info(f"Mailing plan prepared for {len(mailing_plan)} customers")

    # --------------------------------------------------
    # STEP 7: Email Generation & Sending
    # --------------------------------------------------
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

            if not html_body:
                logger.warning(
                    f"No HTML content found for region {region}"
                )
                continue

            subject = (
                f"Week {week} – {region} Freight Market Update"
                if week != "UNKNOWN"
                else f"{region} Freight Market Update"
            )

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
                logger.info(f"Email sent to {email} | {region}")
            else:
                logger.error(f"Email failed to {email} | {error}")

            sent_count += 1

            if EMAIL_BATCH_SIZE and sent_count % EMAIL_BATCH_SIZE == 0:
                logger.info("Batch limit reached — cooling down")
                time.sleep(10)

    # --------------------------------------------------
    # STEP 8: Reply Processing
    # --------------------------------------------------
    replies = read_recent_replies(days=7)

    for reply in replies:

        category = categorize_reply(reply["body"])

        update_customer_after_reply(
            reply["from"],
            category
        )

        logger.info(
            f"Processed reply from {reply['from']} -> {category}"
        )

    # --------------------------------------------------
    # COMPLETION
    # --------------------------------------------------
    logger.info(f"Emails processed: {sent_count}")
    logger.info("=== Freight Market Automation Finished ===")


if __name__ == "__main__":
    main()