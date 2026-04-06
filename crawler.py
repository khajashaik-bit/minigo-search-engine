import requests
from bs4 import BeautifulSoup


def fetch_page(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers, timeout=5)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        title = soup.title.string.strip() if soup.title and soup.title.string else "No title"
        content = soup.get_text(" ", strip=True)

        # 🔥 Extract links
        links = []
        for a in soup.find_all("a", href=True):
            links.append(a["href"])

        return title, content, links

    except Exception as e:
        print("Failed:", url, e)
        return "No title", "", []