import os
from firecrawl import FirecrawlApp
from dotenv import load_dotenv

load_dotenv()

firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

def scrape_url(url: str) -> dict:
    try:
        result = firecrawl.scrape_url(url)
        
        # newer versions return object directly
        content = ""
        if hasattr(result, 'markdown'):
            content = result.markdown or ""
        elif isinstance(result, dict):
            content = result.get("markdown", "")
        
        return {
            "success": bool(content),
            "content": content,
            "url": url
        }
    except Exception as e:
        return {
            "success": False,
            "content": "",
            "url": url,
            "error": str(e)
        }
    

from groq import Groq
import json

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_job_data(markdown: str) -> dict:
    try:
        prompt = f"""
Extract the following information from this job posting and return ONLY a JSON object, nothing else:

{{
    "company_name": "company name here",
    "role_title": "job title here",
    "posted_date": "date if found, else null",
    "stipend": "stipend amount if found, else null",
    "location": "location if found, else null",
    "duration": "duration if found, else null",
    "skills_required": ["skill1", "skill2"],
    "experience_required": "experience if mentioned, else null"
}}

Job posting:
{markdown[:3000]}
"""
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        data["posted_date"] = normalize_date(data.get("posted_date"))
        return data
    
    
    except Exception as e:
        return {
            "error": str(e),
            "company_name": None,
            "role_title": None,
            "posted_date": None
        }
    

import dateparser
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def normalize_date(raw_date: str) -> str:
    if not raw_date:
        return None
    try:
        parsed = dateparser.parse(
            raw_date,
            settings={
                "TIMEZONE": "Asia/Kolkata",
                "RETURN_AS_TIMEZONE_AWARE": True,
                "PREFER_DAY_OF_MONTH": "first"
            }
        )
        if parsed:
            return parsed.astimezone(IST).strftime("%Y-%m-%d")
        return None
    except:
        return None