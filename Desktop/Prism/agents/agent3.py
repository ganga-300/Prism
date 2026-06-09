import os
from datetime import datetime
from utils.company import normalize_company_name, check_registration, check_hiring_history
from utils.founder import check_founder_credibility
from dotenv import load_dotenv

load_dotenv()

def run(job_data: dict) -> dict:
    # Step 1 — extract and normalize company name
    raw_company = job_data.get("company_name")
    location = job_data.get("location")

    if not raw_company:
        return {
            "status": "failed",
            "reason": "No company name found",
            "confidence": 0.0
        }

    company_name = normalize_company_name(raw_company)