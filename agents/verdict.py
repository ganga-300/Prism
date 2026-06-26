import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def run(agent_outputs: dict, job_data: dict) -> dict:
    a1 = agent_outputs.get("agent1", {})
    a2 = agent_outputs.get("agent2", {})
    a3 = agent_outputs.get("agent3", {})

    prompt = f"""
You are giving final advice to a student about whether to apply for this internship.
Combine findings from three independent checks below. Use your judgment — don't follow rigid rules.

Job: {job_data.get('role_title')} at {job_data.get('company_name')}

CHECK 1 — Posting age and cross-platform check:
{json.dumps(a1, indent=2)}

CHECK 2 — Duplicate/clone detection across platforms:
{json.dumps(a2, indent=2)}

CHECK 3 — Company investigation:
{json.dumps(a3, indent=2)}

Based on ALL of this, return ONLY a JSON object:
{{
    "worth_applying": "yes" or "verify_first" or "no",
    "headline": "one sentence summary of the verdict",
    "verified": ["combined list of verified findings across all checks"],
    "suspected": ["combined list of suspicious findings across all checks"],
    "could_not_check": ["combined list of things that could not be verified"],
    "summary": "3-4 sentences in plain English, like a trusted senior giving honest advice. No technical jargon, no mention of 'agents' or 'checks'.",
    "action": "one clear sentence telling the student exactly what to do next"
}}
"""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        result["status"] = "success"
        return result
    except Exception as e:
        return {
            "status": "failed",
            "worth_applying": "verify_first",
            "headline": "Could not complete full analysis",
            "verified": [],
            "suspected": [],
            "could_not_check": ["Analysis encountered an error"],
            "summary": "We couldn't fully analyze this posting. Please verify the company independently before applying.",
            "action": "Research the company manually before applying"
        }