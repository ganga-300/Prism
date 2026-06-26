import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def detect_changes(original_jd: str, other_jd: str, platform1: str, platform2: str) -> list:
    try:
        prompt = f"""
You are investigating whether a company is manipulating job postings to deceive applicants.

Compare these two versions of the same job posted on different platforms on different dates.

Identify changes that suggest deceptive intent — such as:
- Hiding or changing compensation
- Inflating experience requirements
- Adding false urgency
- Misleading applicants in any way

Ignore changes that are clearly cosmetic — different wording, minor rephrasing, punctuation.

For each suspicious change explain WHY it matters to a job seeker.

Return ONLY a JSON array of strings. Each string is one meaningful change.
Return empty array [] if no suspicious changes found.

Job posting from {platform1}:
{original_jd[:1500]}

Job posting from {platform2}:
{other_jd[:1500]}
"""
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)

    except Exception as e:
        return []