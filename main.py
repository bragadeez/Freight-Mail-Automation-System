import json
import os
import time

from utils.logger import setup_logger
from utils.file_utils import get_latest_pdf
from config.constants import REGION_ALIASES
from utils.text_utils import extract_week_number

from pdf_processing.layout_extractor import extract_layout_blocks, split_blocks_by_region
from pdf_processing.extractor import extract_text_exact
from pdf_processing.layout_extractor import extract_layout_blocks
from pdf_processing.region_detector import detect_regions
from pdf_processing.section_splitter import split_sections
from pdf_processing.region_splitter import split_by_subject

from sheets.customers import load_active_customers, update_customer_after_reply
from sheets.regions import sync_regions
from sheets.logs import log_email

from mapping.customer_region_mapper import map_customer_to_regions

from mailer.template_builder import build_email_body_html
from mailer.sender import send_email
from mailer.reply_reader import read_recent_replies
from mailer.reply_categorizer import categorize_reply

from config.settings import EMAIL_BATCH_SIZE


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
    # STEP 2: Extract raw text (EXACT content)
    # --------------------------------------------------
    raw_text_path = "data/extracted_text/raw_text.json"
    extracted = extract_text_exact(pdf_path, raw_text_path)
    logger.info("Raw text extracted successfully")

    # --------------------------------------------------
    # STEP 3: Detect week number and regions
    # --------------------------------------------------
    combined_text = " ".join(extracted["pages"].values())

    week = extract_week_number(combined_text)
    if week == "UNKNOWN":
        logger.warning("Week number could not be detected")

    # regions = detect_regions(extracted["pages"])

    logger.info(f"Detected Week: {week}")
    # --------------------------------------------------
    # STEP 4: Split content by region and sections
    # --------------------------------------------------
    full_text = "\n".join(extracted["pages"].values())
    region_blocks = split_by_subject(full_text)
    normalized_blocks = {}
    for region, block in region_blocks.items():
        normalized = REGION_ALIASES.get(region, region)
        normalized_blocks[normalized] = block

    region_blocks = normalized_blocks
    subject_regions = list(region_blocks.keys())

    logger.info(f"Subject Regions (normalized): {subject_regions}")
    subject_regions = list(region_blocks.keys())
    logger.info(f"Subject Regions (source of truth): {subject_regions}")

    structured_report = {
        "week": week,
        "regions": {}
    }

    for region, block in region_blocks.items():
        all_blocks = extract_layout_blocks(pdf_path)
        region_blocks_map = split_blocks_by_region(all_blocks)

        structured_report = {
            "week": week,
            "regions": {}
        }

        for region, blocks in region_blocks_map.items():
            structured_report["regions"][region] = {
                "subject": region_blocks.get(region, {}).get("subject", ""),
                "blocks": blocks
            }



    os.makedirs("data/structured_reports", exist_ok=True)
    structured_path = f"data/structured_reports/Week{week}_structured.json"

    with open(structured_path, "w", encoding="utf-8") as f:
        json.dump(structured_report, f, indent=2, ensure_ascii=False)

    logger.info(
        f"Structured report saved for Week {week}: {structured_path}"
    )

    # --------------------------------------------------
    # STEP 5: Google Sheets – Region Master sync
    # --------------------------------------------------
    try:
        sync_regions(subject_regions, week)
        logger.info("Region_Master sheet synced successfully")
    except Exception as e:
        logger.error(f"Failed to sync Region_Master: {e}")
        return

    # --------------------------------------------------
    # STEP 6: Load active customers
    # --------------------------------------------------
    customers = load_active_customers()

    if not customers:
        logger.warning("No active customers found — nothing to process")
        return

    logger.info(f"Loaded {len(customers)} active customers")

    # --------------------------------------------------
    # STEP 7: Customer → Region Mapping
    # --------------------------------------------------
    mailing_plan = []

    for customer in customers:
        customer_regions = map_customer_to_regions(customer, subject_regions)

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
    # STEP 8: Email Generation & Sending
    # (PHASE 7 – Dispatch)
    # --------------------------------------------------
    sent_count = 0
    processed_pairs = set()  # (email, region)

    for item in mailing_plan:
        email = item["Email"]
        company = item["Company"]
        contact_name = item.get("Contact Name", "")
        customer_regions = item["Regions"]

        for region in customer_regions:
            pair = (email, region)
            if pair in processed_pairs:
                continue

            processed_pairs.add(pair)

            region_content = structured_report["regions"].get(region)
            if not region_content:
                logger.warning(
                    f"No structured content found for region {region}"
                )
                continue

            subject = region_blocks[region]["subject"]

            body = build_email_body_html(
                contact_name,
                region,
                region_content["blocks"],
                week
            )


            success, error = send_email(email, subject, body)

            status = "Sent" if success else "Failed"

            log_email(
                week=week,
                region=region,
                company=company,
                email=email,
                status=status,
                error=error
            )

            if success:
                logger.info(f"Email sent to {email} | {region}")
            else:
                logger.error(f"Email failed to {email} | {error}")

            sent_count += 1

            # Gmail safety batching
            if EMAIL_BATCH_SIZE and sent_count % EMAIL_BATCH_SIZE == 0:
                logger.info("Batch limit reached — cooling down")
                time.sleep(10)

    # --------------------------------------------------
    # STEP 9: Reply Processing
    # (PHASE 8 – Engagement Handling)
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
    logger.info("Phase 7 & 8 completed successfully")
    logger.info("=== Freight Market Automation Finished ===")


if __name__ == "__main__":
    main()
