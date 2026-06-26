import os
import requests
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()

cache = {}

def serper_search(query: str) -> list:
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": os.getenv("SERPER_API_KEY")},
            json={"q": query, "num": 5},
            timeout=10
        )
        if response.status_code == 200:
            results = response.json().get("organic", [])
            return [{"title": r.get("title"), "snippet": r.get("snippet"), "link": r.get("link")} for r in results]
        return []
    except:
        return []

def ddg_search(query: str) -> list:
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        return [{"title": r.get("title"), "snippet": r.get("body"), "link": r.get("href")} for r in results]
    except:
        return []

def search(query: str) -> list:
    # Check cache first
    if query in cache:
        return cache[query]

    # Try Serper first
    results = serper_search(query)

    # Fall back to DuckDuckGo
    if not results:
        results = ddg_search(query)

    # Cache the result
    cache[query] = results
    return results