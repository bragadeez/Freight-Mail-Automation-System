import json
import os
import time

from utils.logger import setup_logger
from utils.file_utils import get_latest_pdf
from utils.text_utils import extract_week_number

from pdf_processing.layout_extractor import (
    extract_layout_blocks,
    split_blocks_by_region
)

from sheets.customers import load_active_customers, update_customer_after_reply
from sheets.regions import sync_regions
from sheets.logs import log_email

from mapping.customer_region_mapper import map_customer_to_regions

from mailer.template_builder import build_email_body_html
from mailer.sender import send_email
from mailer.reply_reader import read_recent_replies
from mailer.reply_categorizer import categorize_reply

from config.settings import EMAIL_BATCH_SIZE
from config.constants import REGION_ALIASES


def main():
    logger = setup_logger()
    logger.info("=== Freight Market Automation Started ===")

    # --------------------------------------------------
    # STEP 1: Load latest weekly PDF
    # --------------------------------------------------
    try:
        pdf_path = get_latest_pdf("data/input_pdfs")
        logger.info(f"Using PDF: {pdf_path}")
    except Exception as e:
        logger.error(f"Failed to locate weekly PDF: {e}")
        return

    # --------------------------------------------------
    # STEP 2: Extract week number (text-only, safe)
    # --------------------------------------------------
    try:
        from pdf_processing.extractor import extract_text_exact

        raw = extract_text_exact(
            pdf_path,
            "data/extracted_text/raw_text.json"
        )
        combined_text = " ".join(raw["pages"].values())
        week = extract_week_number(combined_text)
    except Exception:
        week = "UNKNOWN"

    logger.info(f"Detected Week: {week}")

    # --------------------------------------------------
    # STEP 3: Layout-aware extraction (SINGLE source of truth)
    # --------------------------------------------------
    logger.info("Extracting layout-aware blocks")
    all_blocks = extract_layout_blocks(pdf_path)

    region_blocks_map = split_blocks_by_region(all_blocks)

    if not region_blocks_map:
        logger.error("No regions detected from layout titles — aborting")
        return

    # --------------------------------------------------
    # STEP 4: Normalize region names (aliases)
    # --------------------------------------------------
    normalized_regions = {}

    for region, blocks in region_blocks_map.items():
        normalized = REGION_ALIASES.get(region, region)
        normalized_regions[normalized] = blocks

    subject_regions = list(normalized_regions.keys())
    logger.info(f"Region source of truth (layout): {subject_regions}")

    # --------------------------------------------------
    # STEP 5: Persist structured report (audit/debug)
    # --------------------------------------------------
    structured_report = {
        "week": week,
        "regions": {}
    }

    for region, blocks in normalized_regions.items():
        structured_report["regions"][region] = {
            "blocks": blocks
        }

    os.makedirs("data/structured_reports", exist_ok=True)
    structured_path = f"data/structured_reports/Week{week}_structured.json"

    with open(structured_path, "w", encoding="utf-8") as f:
        json.dump(structured_report, f, indent=2, ensure_ascii=False)

    logger.info(f"Structured report saved: {structured_path}")

    # --------------------------------------------------
    # STEP 6: Google Sheets – Region Master sync
    # --------------------------------------------------
    try:
        sync_regions(subject_regions, week)
        logger.info("Region_Master sheet synced successfully")
    except Exception as e:
        logger.error(f"Failed to sync Region_Master: {e}")
        return

    # --------------------------------------------------
    # STEP 7: Load active customers
    # --------------------------------------------------
    customers = load_active_customers()

    if not customers:
        logger.warning("No active customers found — nothing to process")
        return

    logger.info(f"Loaded {len(customers)} active customers")

    # --------------------------------------------------
    # STEP 8: Customer → Region Mapping
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
    # STEP 9: Email Generation & Sending
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

            region_data = structured_report["regions"].get(region)
            if not region_data:
                logger.warning(
                    f"No layout blocks found for region {region}"
                )
                continue

            body = build_email_body_html(
                contact_name,
                region,
                region_data["blocks"],
                week
            )

            subject = (
                f"Week {week} – {region} Freight Market Update"
                if week != "UNKNOWN"
                else f"{region} Freight Market Update"
            )

            success, error = send_email(email, subject, body)

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
    # STEP 10: Reply Processing
    # --------------------------------------------------
    replies = read_recent_replies(days=7)

    for reply in replies:
        category = categorize_reply(reply["body"])
        update_customer_after_reply(reply["from"], category)
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
