import os
from utils.company import investigate_company
from dotenv import load_dotenv

load_dotenv()

def run(job_data: dict, job_url: str = "", job_markdown: str = "") -> dict:
    company = job_data.get("company_name")

    if not company:
        return {
            "status": "failed",
            "reason": "No company name found",
            "confidence": "unverifiable"
        }

    return investigate_company(company, job_data, job_url, job_markdown)