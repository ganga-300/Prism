import os
from utils.scraper import scrape_url
from utils.search import search
from utils.embeddings import calculate_similarities, is_short_jd
from utils.diff import detect_changes
from dotenv import load_dotenv

load_dotenv()

PLATFORMS = ["naukri.com", "internshala.com", "unstop.com"]

def is_clone(score: float, original_url: str, other_url: str, company: str, snippet: str) -> bool:
    same_platform = any(
        p in original_url and p in other_url
        for p in ["internshala", "naukri", "unstop"]
    )
    company_confirmed = any(
        word.lower() in snippet.lower()
        for word in company.split() if len(word) > 3
    )
    if same_platform and company_confirmed:
        return score > 0.65
    elif company_confirmed:
        return score > 0.75
    else:
        return score > 0.85

def extract_jd_text(content: str) -> str:
    # Return first 2000 chars as JD text
    return content[:2000] if content else ""

def run(job_url: str, job_data: dict, platform_urls: list) -> dict:
    company = job_data.get("company_name")
    role = job_data.get("role_title")

    if not company or not role:
        return {
            "status": "failed",
            "reason": "Missing company or role",
            "confidence": 0.0
        }

    # Step 1 — get original JD
    scraped = scrape_url(job_url)
    if not scraped["success"]:
        return {
            "status": "failed",
            "reason": "Could not scrape original URL",
            "confidence": 0.0
        }
    original_jd = extract_jd_text(scraped["content"])

    # Step 2 — find URLs on other platforms if not provided
    if not platform_urls:
       return {
        "status": "partial",
        "clone_detected": False,
        "reason": "No cross-platform URLs provided from Agent 1",
        "platforms_compared": 0,
        "similarity_scores": [],
        "changes_detected": [],
        "confidence": 0.2
    }

    # Step 3 — compare JDs
    other_jds = []
    platform_names = []

    for item in platform_urls:
        url = item.get("url")
        platform = item.get("platform", "unknown")

        if not url or url == job_url:
            continue

        other_scraped = scrape_url(url)
        if other_scraped["success"] and other_scraped["content"]:
            jd_text = extract_jd_text(other_scraped["content"])
        else:
            # fallback to snippet
            jd_text = item.get("snippet", "")

        if jd_text:
            other_jds.append(jd_text)
            platform_names.append(platform)

    if not other_jds:
        return {
            "status": "partial",
            "clone_detected": False,
            "reason": "Only found on one platform — cannot verify cloning",
            "platforms_compared": 0,
            "similarity_scores": [],
            "changes_detected": [],
            "confidence": 0.2
        }

    # Step 4 — calculate similarity
    scores = calculate_similarities(original_jd, other_jds)

    # Step 5 — detect changes for clones
    clone_detected = False
    changes_detected = []
    similarity_results = []

    for i, score in enumerate(scores):
        platform = platform_names[i]
        similarity_results.append({
            "platform": platform,
            "similarity": score
        })

        if is_clone(score, job_url, item.get("url", ""), company, item.get("snippet", "")):
            clone_detected = True
            changes = detect_changes(original_jd, other_jds[i], "original", platform)
            changes_detected.extend(changes)

    # Step 6 — confidence
    confidence = 0.5
    if len(scores) >= 2:
        confidence += 0.2
    if len(scores) >= 3:
        confidence += 0.2
    confidence = min(confidence, 1.0)

    return {
        "status": "success",
        "clone_detected": clone_detected,
        "platforms_compared": len(scores),
        "similarity_scores": similarity_results,
        "changes_detected": changes_detected,
        "confidence": round(confidence, 2)
    }