import requests
from bs4 import BeautifulSoup


def fetch_page(url):
    """
    Fetch page content and extract:
    - title
    - full text
    - links
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        content = soup.get_text(" ", strip=True)

        # collect all links
        links = [a["href"] for a in soup.find_all("a", href=True)]

        return title, content, links

    except Exception as e:
        print("Failed:", url)
        return "No title", "", []