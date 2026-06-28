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