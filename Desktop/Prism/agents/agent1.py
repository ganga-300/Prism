import os
import dateparser
import pytz
import requests
from datetime import datetime
from utils.scraper import scrape_url, extract_job_data, normalize_date
from utils.search import search

import re

def is_job_posting_url(url: str) -> bool:
    # Job posting URLs almost always contain a numeric ID
    return bool(re.search(r'\d{6,}', url))

IST = pytz.timezone("Asia/Kolkata")
PLATFORMS = ["naukri.com", "internshala.com", "unstop.com"]

def validate_url(url: str) -> dict:
    if not url or not url.startswith("http"):
        return {
            "valid": False,
            "reason": "Please paste a valid URL."
        }
    return {"valid": True, "reason": None}

def is_relevant_url(url: str, snippet: str, company: str) -> bool:
    company_lower = company.lower()
    # Check if company name appears in URL or snippet
    url_lower = url.lower()
    snippet_lower = snippet.lower()
    
    # Get first word of company name as minimum match
    company_words = [w.lower() for w in company.split() if len(w) > 3]
    
    matches = sum(1 for w in company_words if w in snippet_lower or w in url_lower)
    return matches >= 1



def find_cross_platform_urls(company: str, role: str) -> list:
    urls_found = []
    for platform in PLATFORMS:
        query = f'"{company}" "{role}" site:{platform}'
        results = search(query)
        for result in results[:2]:
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            if link and is_relevant_url(link, snippet, company) and is_job_posting_url(link):
                urls_found.append({
                    "platform": platform,
                    "url": link,
                    "snippet": snippet
                })
    return urls_found

def extract_date_from_url(url: str, platform: str) -> dict:
    scraped = scrape_url(url)
    if not scraped["success"] or not scraped["content"]:
        return None
    job_data = extract_job_data(scraped["content"])
    date = job_data.get("posted_date")
    if not date:
        return None
    return {
        "platform": platform,
        "date": date,
        "url": url,
        "source": "direct_scrape"
    }

def check_wayback(url: str) -> str:
    try:
        response = requests.get(
            f"http://archive.org/wayback/available?url={url}",
            timeout=5
        )
        data = response.json()
        snapshots = data.get("archived_snapshots", {})
        closest = snapshots.get("closest", {})
        if closest.get("available"):
            raw_date = closest.get("timestamp", "")
            if raw_date:
                parsed = datetime.strptime(raw_date[:8], "%Y%m%d")
                ist_date = IST.localize(parsed)
                return ist_date.strftime("%Y-%m-%d")
        return None
    except:
        return None

def run(job_url: str, job_data: dict) -> dict:
    company = job_data.get("company_name")
    role = job_data.get("role_title")
    original_date = job_data.get("posted_date")

    if not company or not role:
        return {
            "status": "failed",
            "reason": "Could not extract company or role from posting",
            "confidence": 0.0
        }

    # Step 1 — find URLs across platforms
    cross_platform_urls = find_cross_platform_urls(company, role)

    # Step 2 — scrape each URL for real dates
    cross_platform_dates = []
    for item in cross_platform_urls:
        result = extract_date_from_url(item["url"], item["platform"])
        if result:
            cross_platform_dates.append(result)

    # Step 3 — check Wayback for original URL
    wayback_date = check_wayback(job_url)

    # Step 4 — collect all dates
    all_dates = []

    if original_date:
        all_dates.append({
            "platform": "original",
            "date": original_date,
            "source": "direct_scrape"
        })

    if wayback_date:
        all_dates.append({
            "platform": "wayback",
            "date": wayback_date,
            "source": "wayback_machine"
        })

    all_dates.extend(cross_platform_dates)

    # Step 5 — find earliest date
    valid_dates = [d for d in all_dates if d.get("date")]

    if not valid_dates:
        return {
            "status": "partial",
            "reason": "No dates found across platforms",
            "confidence": 0.2,
            "original_date": original_date
        }

    earliest = min(valid_dates, key=lambda x: x["date"])

    # Step 6 — calculate real age
    today = datetime.now(IST).strftime("%Y-%m-%d")
    earliest_date = datetime.strptime(earliest["date"], "%Y-%m-%d")
    today_date = datetime.strptime(today, "%Y-%m-%d")
    real_age_days = (today_date - earliest_date).days

    # Step 7 — calculate displayed age
    displayed_age_days = 0
    if original_date:
        original = datetime.strptime(original_date, "%Y-%m-%d")
        displayed_age_days = (today_date - original).days

    # Step 8 — calculate confidence
    confidence = 0.4
    if wayback_date:
        confidence += 0.3
    if len(valid_dates) >= 3:
        confidence += 0.2
    elif len(valid_dates) >= 2:
        confidence += 0.1
    confidence = min(confidence, 1.0)

    # Step 9 — detect manipulation
    manipulation_detected = real_age_days > (displayed_age_days + 7)

    # Step 10 — also return cross platform URLs for Agent 2
    platforms_found = list(set([d["platform"] for d in valid_dates]))
    repost_count = len([d for d in valid_dates if d["platform"] != "original"])

    return {
        "status": "success",
        "earliest_date": earliest["date"],
        "earliest_platform": earliest["platform"],
        "real_age_days": real_age_days,
        "displayed_age_days": displayed_age_days,
        "platforms_found": platforms_found,
        "repost_count": repost_count,
        "wayback_confirmed": bool(wayback_date),
        "manipulation_detected": manipulation_detected,
        "confidence": round(confidence, 2),
        "cross_platform_urls": cross_platform_urls
    }