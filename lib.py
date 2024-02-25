from bs4 import BeautifulSoup
from langchain.utilities import DuckDuckGoSearchAPIWrapper
import requests

def get_serp_links(query: str, num_results: int = 6):
    ddg_search = DuckDuckGoSearchAPIWrapper()
    results = ddg_search.results(query, num_results)
    return [r["link"] for r in results]

def scrape_webpage_text(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            text = soup.get_text(separator=" ", strip=True)
            return text
        else:
            return f"failed to scrape webpage with status: {r.status_code}"
    except Exception as e:
        return f"failed to scrape webpage with error:\n{e}"
