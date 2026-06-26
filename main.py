from utils.scraper import scrape_url, extract_job_data
from agents.agent1 import run as agent1_run
from agents.agent2 import run as agent2_run
from agents.agent3 import run as agent3_run
from agents.verdict import run as verdict_run
import json

url = "https://unstop.com/internships/java-developer-internship-unstop-tech-fair-2025-yugensoft-innovations-1697348"





scraped = scrape_url(url)
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

print("\n=== FINAL VERDICT ===")
print(json.dumps(verdict, indent=2))