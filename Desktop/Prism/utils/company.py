import os
import json
from groq import Groq
from rapidfuzz import fuzz
from utils.scraper import scrape_url
from utils.search import search
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def normalize_company_name(raw_name: str) -> str:
    try:
        prompt = f"""
Given this company name extracted from a job posting, return the most complete 
and formal version of the name. Include Pvt Ltd or Private Limited if it's likely 
an Indian registered company.
Return only the company name, nothing else.

Company name: {raw_name}
"""
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except:
        return raw_name


def check_registration(company_name: str) -> dict:
    # Step 1 — find company page on Zauba Corp via search
    results = search(f'"{company_name}" site:zaubacorp.com')
    
    if not results:
        # Step 2 — fallback to MCA via search
        results = search(f'"{company_name}" private limited site:mca.gov.in')
        if not results:
            return {
                "found": False,
                "source": None,
                "registration_status": "Unknown",
                "directors": [],
                "incorporation_date": None,
                "confidence": 0.1
            }
        source = "mca_via_search"
        content = results[0]["snippet"]
    else:
        # Step 3 — scrape the actual Zauba Corp page
        source = "zaubacorp"
        scraped = scrape_url(results[0]["link"])
        content = scraped["content"] if scraped["success"] else results[0]["snippet"]

    # Step 4 — extract structured info with Groq
    try:
        prompt = f"""
Extract the following from this company registration data and return ONLY a JSON object:

{{
    "registration_status": "Active or Struck Off or Unknown",
    "cin": "company identification number if found, else null",
    "incorporation_date": "date if found, else null",
    "directors": ["director1", "director2"],
    "paid_up_capital": "amount if found, else null"
}}

Data:
{content[:2000]}
"""
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)

        return {
            "found": True,
            "source": source,
            "confidence": 0.8 if source == "zaubacorp" else 0.5,
            **data
        }
    except:
        return {
            "found": True,
            "source": source,
            "registration_status": "Unknown",
            "directors": [],
            "incorporation_date": None,
            "confidence": 0.3
        }
    
result = check_registration("Infosys Limited")
print(result)