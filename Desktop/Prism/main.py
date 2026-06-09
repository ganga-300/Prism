import os
from dotenv import load_dotenv
from firecrawl import FirecrawlApp
from groq import Groq
import requests

load_dotenv()

# Test Firecrawl
print("Testing Firecrawl...")
firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
result = firecrawl.scrape_url("https://internshala.com")
print("Firecrawl ✅" if result else "Firecrawl ❌")

# Test Groq
print("Testing Groq...")
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
response = groq.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "say hello"}]
)
print("Groq ✅" if response else "Groq ❌")

# Test Serper
print("Testing Serper...")
response = requests.post(
    "https://google.serper.dev/search",
    headers={"X-API-KEY": os.getenv("SERPER_API_KEY")},
    json={"q": "test"}
)
print("Serper ✅" if response.status_code == 200 else "Serper ❌")


from utils.scraper import scrape_url

# result = scrape_url("https://internshala.com/internship/detail/work-from-home-full-stack-development-internship-at-queens-of-change-foundation1780920146")
# print(result["success"])
# print(result["content"][:500])


from utils.scraper import scrape_url, extract_job_data
from agents.agent1 import run as agent1_run

url = "https://internshala.com/internship/detail/work-from-home-full-stack-development-internship-at-queens-of-change-foundation1780920146"
scraped = scrape_url(url)

if scraped["success"]:
    job_data = extract_job_data(scraped["content"])
    print(job_data)

    result = agent1_run(url, job_data)
    print("\nAgent 1 Result:")
    print(result)


