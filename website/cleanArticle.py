import requests
from bs4 import BeautifulSoup
#from summarizeGPT import getSummary as ai

def get_clean_text(url):
    response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.content, "html.parser")

    # Remove unwanted sections like navigation, footers, and sidebars
    for tag in soup(["nav", "footer", "aside", "script", "style"]): 
        tag.extract()  # Remove the tag and its contents

    # Try to get the main content area
    article = soup.find("article") or soup.find("main") or soup.find("div")  

    if article:
        return article.get_text(separator="\n", strip=True)
    else:
        return soup.get_text(separator="\n", strip=True)  # Fallback to all text
#print(ai(get_clean_text('https://www.amnesty.org/en/latest/news/2025/03/usa-arrest-and-detention-of-mahmoud-khalil-is-chilling-attack-on-human-rights/')))
    