import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_summary(signals: list, score: int, job_data: dict) -> str:
    if not signals:
        return "No suspicious signals detected. This posting appears legitimate based on available data. You can proceed with your application."

    signal_text = "\n".join([
        f"- {s['detail']} ({s['severity']} severity)"
        for s in signals
    ])

    prompt = f"""
You are writing a plain English verdict for a student job seeker about whether a job posting is legitimate.

Job: {job_data.get('role_title')} at {job_data.get('company_name')}

Signals found:
{signal_text}

Write a 3-4 sentence summary that:
1. States clearly whether they should apply or not
2. Explains the most important reasons why
3. Is direct and honest — not vague
4. Reads like a trusted senior giving advice, not a robot
5. Never mentions technical terms like "agent", "signal", "confidence score"

Do not mention any numbers or scores.
Return only the summary text, nothing else.
"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except:
        return "We encountered an issue generating the summary. Please review the signals above."