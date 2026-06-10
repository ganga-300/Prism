import os
from groq import Groq
from utils.scraper import scrape_url
from utils.search import search
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def find_careers_page(company: str) -> dict:
    queries = [
        f'"{company}" careers internship India',
        f'"{company}" jobs opening intern India',
        f'"{company}" hiring freshers India'
    ]
    
    for query in queries:
        results = search(query)
        if results:
            return {
                "found": True,
                "url": results[0]["link"]
            }
    
    return {"found": False, "url": None}

def check_role_on_page(content: str, role: str, company: str) -> dict:
    try:
        prompt = f"""
You are checking if a company's careers page has an opening similar to a specific role.

Company: {company}
Role looking for: {role}

Careers page content:
{content[:2000]}

Answer ONLY with a JSON object:
{{
    "role_found": true or false,
    "reason": "one line explanation",
    "similar_roles_found": ["role1", "role2"]
}}
"""
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        import json
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except:
        return {
            "role_found": False,
            "reason": "Could not analyze careers page",
            "similar_roles_found": []
        }

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
    careers = find_careers_page(company)

    if not careers["found"]:
        return {
            "status": "partial",
            "careers_page_found": False,
            "role_found_on_careers_page": False,
            "reason": "Could not find company careers page",
            "confidence": 0.2
        }

    # Step 2 — scrape careers page
    scraped = scrape_url(careers["url"])

    if not scraped["success"] or not scraped["content"]:
        return {
            "status": "partial",
            "careers_page_found": True,
            "careers_url": careers["url"],
            "role_found_on_careers_page": False,
            "reason": "Could not scrape careers page",
            "confidence": 0.3
        }

    # Step 3 — Groq checks if role exists
    result = check_role_on_page(scraped["content"], role, company)

    return {
        "status": "success",
        "careers_page_found": True,
        "careers_url": careers["url"],
        "role_found_on_careers_page": result["role_found"],
        "reason": result["reason"],
        "similar_roles_found": result["similar_roles_found"],
        "confidence": 0.8 if result["role_found"] else 0.7
    }