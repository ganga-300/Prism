# import os
# from dotenv import load_dotenv
# from firecrawl import FirecrawlApp
# from groq import Groq
# import requests

# load_dotenv()

# # Test Firecrawl
# print("Testing Firecrawl...")
# firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
# result = firecrawl.scrape_url("https://internshala.com")
# print("Firecrawl ✅" if result else "Firecrawl ❌")

# # Test Groq
# print("Testing Groq...")
# groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
# response = groq.chat.completions.create(
#     model="llama-3.3-70b-versatile",
#     messages=[{"role": "user", "content": "say hello"}]
# )
# print("Groq ✅" if response else "Groq ❌")

# # Test Serper
# print("Testing Serper...")
# response = requests.post(
#     "https://google.serper.dev/search",
#     headers={"X-API-KEY": os.getenv("SERPER_API_KEY")},
#     json={"q": "test"}
# )
# print("Serper ✅" if response.status_code == 200 else "Serper ❌")


# from utils.scraper import scrape_url

# # result = scrape_url("https://internshala.com/internship/detail/work-from-home-full-stack-development-internship-at-queens-of-change-foundation1780920146")
# # print(result["success"])
# # print(result["content"][:500])


# from utils.scraper import scrape_url, extract_job_data
# from agents.agent1 import run as agent1_run

# url = "https://internshala.com/internship/detail/work-from-home-full-stack-development-internship-at-queens-of-change-foundation1780920146"
# scraped = scrape_url(url)

# if scraped["success"]:
#     job_data = extract_job_data(scraped["content"])
#     print(job_data)

#     result = agent1_run(url, job_data)
#     print("\nAgent 1 Result:")
#     print(result)

# from utils.embeddings import calculate_similarities

# from utils.embeddings import calculate_similarities

# jd1 = """
# We are looking for a passionate Frontend Developer Intern to join our growing team. 
# You will be responsible for building and maintaining user interfaces using React and Node.js. 
# The ideal candidate should have experience with REST APIs, Git, and basic understanding of 
# backend systems. You will collaborate closely with our design and backend teams to deliver 
# high quality web applications. This is a work from home opportunity with a stipend of 5000 
# per month for a duration of 3 months. Immediate joiners preferred.
# """

# jd2 = """
# We are seeking a talented Frontend Development Intern to become part of our dynamic team.
# The candidate will develop and maintain web interfaces using React and Node.js frameworks.
# Strong knowledge of REST APIs, version control with Git, and familiarity with server side 
# concepts is required. You will work alongside our design and engineering teams to create 
# exceptional web products. This remote position offers a monthly stipend of 5000 rupees 
# for 3 months duration. Looking for candidates who can join immediately.
# """

# jd3 = """
# We are hiring a Data Science Intern to work on machine learning projects. You will analyze 
# large datasets using Python, pandas and scikit-learn. The role involves building predictive 
# models, creating data visualizations and presenting insights to stakeholders. Experience with 
# SQL and basic statistics is required. This is an office based role in Bangalore with a stipend 
# of 8000 per month for 6 months. Strong communication skills required.
# """



# scores = calculate_similarities(jd1, [jd2, jd3])
# print(scores)

# print(len(jd1.split()))
# print(len(jd2.split()))




# from utils.diff import detect_changes

# jd_internshala = """
# We are looking for a Frontend Developer Intern to join our team.
# React and Node.js knowledge required. 0-1 years experience.
# Stipend: 5000 per month. Duration 3 months. Work from home.
# Immediate joiners preferred.
# """

# jd_linkedin = """
# We are looking for a Frontend Developer Intern to join our team.
# React, Node.js, AWS and Docker knowledge required. 2 years experience needed.
# Compensation: Competitive. Duration 3 months. Work from home.
# Urgently hiring. Immediate joiners only.
# """

# changes = detect_changes(jd_internshala, jd_linkedin, "internshala", "linkedin")
# print(changes)

from utils.company import normalize_company_name, check_registration

name = normalize_company_name("Infosys")
print("Normalized:", name)

result = check_registration(name)
print("Registration:", result)


