from utils.scraper import scrape_url, extract_job_data
from agents.agent1 import run as agent1_run
from agents.agent2 import run as agent2_run

url = "https://internshala.com/internship/detail/work-from-home-full-stack-development-internship-at-queens-of-change-foundation1780920146"

scraped = scrape_url(url)
job_data = extract_job_data(scraped["content"])

agent1_result = agent1_run(url, job_data)
platform_urls = agent1_result.get("cross_platform_urls", [])

print("Agent 1:", agent1_result)
print("Platform URLs passed to Agent 2:", platform_urls)

agent2_result = agent2_run(url, job_data, platform_urls)
print("Agent 2:", agent2_result)