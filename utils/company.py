import os
import re
import json
from groq import Groq
from utils.scraper import scrape_url
from utils.search import search
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_company_profile_url(markdown: str, platform: str) -> str:
    if platform == "internshala":
        match = re.search(r'https://internshala\.com/company/[^\)\s\"]+', markdown)
        if match:
            return match.group(0)
    return None

def detect_platform(job_url: str) -> str:
    if "internshala.com" in job_url:
        return "internshala"
    elif "naukri.com" in job_url:
        return "naukri"
    elif "unstop.com" in job_url:
        return "unstop"
    return "unknown"

def scrape_internshala_profile(profile_url: str) -> dict:
    scraped = scrape_url(profile_url)
    if not scraped["success"] or not scraped["content"]:
        return None

    prompt = f"""
Extract the following from this Internshala company profile and return ONLY a JSON object:

{{
    "hiring_since": "year or null",
    "employee_count": "range or null",
    "opportunities_posted": number or null,
    "candidates_hired": number or null,
    "location": "location or null",
    "industry": "industry or null",
    "about": "company description or null",
    "current_openings": ["role1", "role2"],
    "perks": ["perk1", "perk2"]
}}

Profile content:
{scraped["content"][:3000]}
"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except:
        return None

def google_search_company(company_name: str) -> str:
    queries = [
        f'{company_name} official website India',
        f'{company_name} site:linkedin.com/company',
    ]
    all_snippets = ""
    for query in queries:
        results = search(query)
        for r in results[:3]:
            all_snippets += f"Source: {r.get('link', '')}\n{r.get('title', '')}\n{r.get('snippet', '')}\n\n"
    return all_snippets

def extract_online_presence(snippets: str, company_name: str) -> dict:
    if not snippets.strip():
        return {
            "website_found": False,
            "website_url": None,
            "linkedin_found": False,
            "linkedin_url": None
        }
    
    prompt = f"""
From these search results about "{company_name}", identify their official website and LinkedIn company page.

Search results:
{snippets[:2500]}

Guidance:
- The official website is usually their own domain (e.g., companyname.com), not a news article, 
  not a job portal (internshala/naukri/linkedin job listings), not a directory site.
- For well-known companies, their official homepage will be obvious even if news articles also appear — 
  pick the homepage, not an article about them.
- linkedin_url must be a company page (contains "linkedin.com/company/"), not a personal profile.
- If you genuinely cannot identify either from the results, return null — don't guess.

Return ONLY a JSON object:
{{
    "website_found": true or false,
    "website_url": "url or null",
    "linkedin_found": true or false,
    "linkedin_url": "url or null"
}}
"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        
        linkedin_url = data.get("linkedin_url")
        if linkedin_url and "linkedin.com/company" not in linkedin_url:
            data["linkedin_found"] = False
            data["linkedin_url"] = None
        
        return data
    except:
        return {
            "website_found": False,
            "website_url": None,
            "linkedin_found": False,
            "linkedin_url": None
        }

def build_verdict(profile_data: dict, online_presence: dict, company_name: str, job_data: dict) -> dict:
    
    prompt = f"""
You are investigating a company for a student who is considering applying for an internship.
Use your judgment based on ALL the data below — don't follow rigid rules, reason like an experienced investigator would.

Company name from job posting: {company_name}
Role: {job_data.get("role_title", "unknown")}

Internshala profile data:
{json.dumps(profile_data, indent=2) if profile_data else "Not available"}

Online presence:
{json.dumps(online_presence, indent=2)}

IMPORTANT CALIBRATION GUIDANCE:
- A 15-40% hire rate (candidates_hired / opportunities_posted) is NORMAL and healthy. Only flag hire rate as 
  concerning if it's under 10% AND opportunities_posted is high (50+) over multiple years — that's resume farming.
- If hiring_since is recent (within the last year) and opportunities_posted is low (under 15), 
  zero or low hires is EXPECTED, not suspicious — the company hasn't had time to hire yet. Don't flag this.
- Don't penalize a company just because online presence search found nothing — many small legitimate 
  companies have minimal web presence. Treat missing website/LinkedIn as "could not check", not as a red flag, 
  unless combined with other inconsistencies.
- You MUST be willing to say "yes" when the evidence is genuinely clean — don't default to caution. 
  If hiring history is solid, no name/description mismatches exist, and nothing is inconsistent, say "yes".
- Reserve "no" for cases with multiple serious, specific red flags (e.g., name/description mismatch 
  AND zero hires over years AND fake LinkedIn).
- Reserve "verify_first" for genuine specific inconsistencies — not just "we couldn't find their website."

Things to specifically watch for:
- Company name doesn't match the "about" description (different business entirely)
- Resume farming pattern (see calibration above — must be high volume + multi-year + near-zero rate)
- LinkedIn page name doesn't match the company name
- Company description is generic, copy-pasted, or doesn't make sense for the role

Return ONLY a JSON object:
{{
    "verified": ["specific things you can confirm with the data, with source"],
    "suspected": ["specific suspicious things you noticed, with reasoning"],
    "could_not_check": ["things you couldn't verify from available data"],
    "confidence": "high" or "medium" or "low",
    "worth_applying": "yes" or "verify_first" or "no"
}}

Be specific. Reference actual numbers and facts from the data above in your findings.
"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except:
        return {
            "verified": [],
            "suspected": [],
            "could_not_check": ["Error analyzing company data"],
            "confidence": "low",
            "worth_applying": "verify_first"
        }


def investigate_company(company_name: str, job_data: dict, job_url: str, job_markdown: str) -> dict:
    platform = detect_platform(job_url)

    # Step 1 — get Internshala company profile
    profile_data = None
    if platform == "internshala":
        profile_url = extract_company_profile_url(job_markdown, platform)
        if profile_url:
            profile_data = scrape_internshala_profile(profile_url)

    # Step 2 — Google search for website + LinkedIn
    snippets = google_search_company(company_name)
    online_presence = extract_online_presence(snippets, company_name)

    # Step 3 — build verdict
    verdict = build_verdict(profile_data, online_presence, company_name, job_data)

    return {
        "status": "success",
        "company_name": company_name,
        "platform": platform,
        "internshala_profile": profile_data,
        "online_presence": online_presence,
        "verified": verdict["verified"],
        "suspected": verdict["suspected"],
        "could_not_check": verdict["could_not_check"],
        "confidence": verdict["confidence"]
    }