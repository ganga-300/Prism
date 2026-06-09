import os
import dateparser
import pytz
from datetime import datetime
from utils.scraper import scrape_url, extract_job_data, normalize_date
from utils.search import search

IST = pytz.timezone("Asia/Kolkata")

PLATFORMS = ["naukri.com", "internshala.com", "unstop.com", "linkedin.com/jobs"]

def find_cross_platform_dates(company: str, role: str) -> list:
    dates_found = []
    
    for platform in PLATFORMS:
        query = f'"{company}" "{role}" site:{platform}'
        results = search(query)
        
        for result in results:
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            
            # Try to extract date from snippet
            date = normalize_date(snippet)
            if date:
                dates_found.append({
                    "platform": platform,
                    "date": date,
                    "url": link,
                    "source": "search_snippet"
                })
    
    return dates_found

def check_wayback(url: str) -> str:
    import requests
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
            # Wayback timestamp format: 20240214123456
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
    
    # Step 1 — find job across platforms
    cross_platform_dates = find_cross_platform_dates(company, role)
    
    # Step 2 — check Wayback for original URL
    wayback_date = check_wayback(job_url)
    
    # Step 3 — collect all dates
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
    
    # Step 4 — find earliest date
    valid_dates = [d for d in all_dates if d.get("date")]
    
    if not valid_dates:
        return {
            "status": "partial",
            "reason": "No dates found across platforms",
            "confidence": 0.2,
            "original_date": original_date
        }
    
    earliest = min(valid_dates, key=lambda x: x["date"])
    
    # Step 5 — calculate real age
    today = datetime.now(IST).strftime("%Y-%m-%d")
    earliest_date = datetime.strptime(earliest["date"], "%Y-%m-%d")
    today_date = datetime.strptime(today, "%Y-%m-%d")
    real_age_days = (today_date - earliest_date).days
    
    # Step 6 — calculate displayed age
    displayed_age_days = 0
    if original_date:
        original = datetime.strptime(original_date, "%Y-%m-%d")
        displayed_age_days = (today_date - original).days
    
    # Step 7 — calculate confidence
    confidence = 0.4  # base
    if wayback_date:
        confidence += 0.3
    if len(valid_dates) >= 3:
        confidence += 0.2
    elif len(valid_dates) >= 2:
        confidence += 0.1
    confidence = min(confidence, 1.0)
    
    # Step 8 — detect manipulation
    manipulation_detected = real_age_days > (displayed_age_days + 7)
    
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
        "confidence": round(confidence, 2)
    }