from fastapi import FastAPI
from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    url: str




from utils.scraper import scrape_url, extract_job_data
from agents.agent1 import run as agent1_run
from agents.agent2 import run as agent2_run
from agents.agent3 import run as agent3_run
from agents.verdict import run as verdict_run

def analyze_job(url: str) -> dict:
    scraped = scrape_url(url)
    if not scraped["success"]:
        return {
            "status": "failed",
            "reason": "Could not access this URL. Please check the link and try again."
        }

    job_data = extract_job_data(scraped["content"])
    job_markdown = scraped["content"]
    agent1_result = agent1_run(url, job_data)
    platform_urls = agent1_result.get("cross_platform_urls", [])
    agent2_result = agent2_run(url, job_data, platform_urls)
    agent3_result = agent3_run(job_data, url, job_markdown)

    agent_outputs = {
        "agent1": agent1_result,
        "agent2": agent2_result,
        "agent3": agent3_result
    }

    verdict = verdict_run(agent_outputs, job_data)

    return {
        "status": "success",
        "job": {
            "company_name": job_data.get("company_name"),
            "role_title": job_data.get("role_title"),
            "location": job_data.get("location"),
            "stipend": job_data.get("stipend")
        },
        "verdict": verdict
    }

app = FastAPI()

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    return analyze_job(request.url)