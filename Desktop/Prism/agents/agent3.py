import os
from datetime import datetime

import dateparser
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


    # Step 2 — check registration
    registration = check_registration(company_name)

    # Step 3 — check hiring history
    hiring_history = check_hiring_history(company_name)

    # Step 4 — founder credibility check if new company
    founder_credibility = None
    incorporation_date = registration.get("incorporation_date")
    is_new_company = False

    if incorporation_date:
        parsed_date = dateparser.parse(incorporation_date)
        if parsed_date:
            months_old = (datetime.now() - parsed_date.replace(tzinfo=None)).days / 30
            is_new_company = months_old < 12

    if is_new_company:
        directors = registration.get("directors", [])
        founder_credibility = check_founder_credibility(company_name, directors)


        # Step 5 — assemble final output
    overall_confidence = round(
        (registration.get("confidence", 0) + 
         hiring_history.get("confidence", 0) + 
         (founder_credibility.get("confidence", 0) if founder_credibility else 0.5)) / 3,
        2
    )

    return {
        "status": "success",
        "company_name": company_name,
        "is_new_company": is_new_company,
        "registration": registration,
        "hiring_history": hiring_history,
        "founder_credibility": founder_credibility,
        "confidence": overall_confidence
    }