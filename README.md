# Freight Mail Automation System

A fully automated, deterministic freight market intelligence system that:

- Extracts exact content from weekly freight market PDFs
- Segments content by region
- Maps customers to relevant regions
- Sends personalized emails with **exact report content**
- Tracks replies and adjusts follow-up cadence automatically

## 🚀 Key Features

- Zero AI / Zero hallucination
- Exact-content preservation (PDF → Email)
- Region-wise and customer-wise segmentation
- Gmail API based sending
- Google Sheets as system-of-record
- Automated reply tracking & follow-up logic
- Windows Task Scheduler compatible
- Zero cloud cost

## 🧱 Architecture Overview

1. Weekly PDF ingestion
2. Text extraction & region detection
3. Section-wise content structuring
4. Customer-region mapping
5. Email generation & sending
6. Reply categorization
7. Follow-up state management
8. Logging & audit trail

## 📁 Project Structure

Freight Mail Automation/
├── main.py
├── config/
├── mailer/
├── mapping/
├── pdf_processing/
├── sheets/
├── utils/
├── data/ (ignored in git)
├── requirements.txt
├── .env.example
└── README.md

## ⚠️ Notes

- Sensitive files (`.env`, credentials, PDFs, logs) are excluded via `.gitignore`
- Designed for deterministic, auditable enterprise use-cases

## 🛠️ Tech Stack

- Python
- Gmail API
- Google Sheets API
- pdfplumber
- Regex-based rule engines

---

## 📌 Status

Production-ready, modular, and extensible.
