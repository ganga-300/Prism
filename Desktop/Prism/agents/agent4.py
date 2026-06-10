import os
from utils.scraper import scrape_url
from utils.search import search
from dotenv import load_dotenv

load_dotenv()

def run(job_data: dict) -> dict:
    company = job_data.get("company_name")
    role = job_data.get("role_title")

    if not company or not role:
        return {
            "status": "failed",
            "reason": "Missing company or role",
            "confidence": 0.0
        }
    

    # Step 1 — find careers page
    results = search(f'"{company}" official careers page jobs opening')
    
    if not results:
        return {
            "status": "partial",
            "careers_page_found": False,
            "role_found_on_careers_page": False,
            "reason": "Could not find company careers page",
            "confidence": 0.2
        }
    
    careers_url = results[0]["link"]


    # Step 2 — scrape careers page
    scraped = scrape_url(careers_url)
    
    if not scraped["success"] or not scraped["content"]:
        return {
            "status": "partial",
            "careers_page_found": True,
            "careers_url": careers_url,
            "role_found_on_careers_page": False,
            "reason": "Could not scrape careers page",
            "confidence": 0.3
        }

    # Step 3 — check if role exists on page
    content_lower = scraped["content"].lower()
    role_lower = role.lower()
    
    # check for full role title or key words from role
    role_words = [w for w in role_lower.split() if len(w) > 3]
    words_found = sum(1 for w in role_words if w in content_lower)
    role_found = words_found >= len(role_words) * 0.6

    return {
        "status": "success",
        "careers_page_found": True,
        "careers_url": careers_url,
        "role_found_on_careers_page": role_found,
        "match_score": round(words_found / max(len(role_words), 1), 2),
        "confidence": 0.8 if role_found else 0.7
    }