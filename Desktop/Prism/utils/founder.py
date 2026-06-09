import os
import json
from groq import Groq
from utils.search import search
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def check_founder_credibility(company_name: str, directors: list) -> dict:
    if not directors:
        return {
            "founders_found": False,
            "credibility_score": 0,
            "red_flags": ["No director information found"],
            "confidence": 0.1
        }

    # Step 1 — search each director
    combined_text = ""
    for director in directors[:2]:  # check top 2 directors only
        queries = [
            f'"{director}" "{company_name}" site:linkedin.com',
            f'"{director}" "{company_name}" founder OR CEO OR director',
            f'"{director}" "{company_name}" startup India'
]
        for query in queries:
            results = search(query)
            for r in results[:1]:
                combined_text += r.get("snippet", "") + "\n"

    if not combined_text.strip():
        return {
            "founders_found": False,
            "credibility_score": 2,
            "red_flags": ["No public information found about founders"],
            "confidence": 0.2
        }

    # Step 2 — Groq scores credibility
    try:
        prompt = f"""
You are evaluating whether the founders/directors of a company are credible and legitimate.

Analyze this information and return ONLY a JSON object:
{{
    "founders_found": true or false,
    "credibility_score": number between 1-10,
    "work_history_found": true or false,
    "public_mentions_found": true or false,
    "red_flags": ["flag1", "flag2"],
    "positive_signals": ["signal1", "signal2"]
}}

Scoring guide:
8-10: Strong work history, public mentions, credible background
5-7: Some history found, limited public presence  
1-4: No verifiable history, suspicious or missing information

Company: {company_name}
Directors: {directors[:2]}
Information found:
{combined_text[:2000]}
"""
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        data["confidence"] = 0.7 if data["founders_found"] else 0.3
        return data

    except:
        return {
            "founders_found": False,
            "credibility_score": 0,
            "red_flags": [],
            "positive_signals": [],
            "confidence": 0.2
        }