import sqlite3
from collections import Counter
from crawler import fetch_page
from text_processing import clean_and_tokenize


def fix_url(url):
    if not url.startswith("http"):
        return "https://" + url
    return url


def load_urls(file_path="urls.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
        return list(set(urls))
    except:
        return []


def index_page(url):
    url = fix_url(url)

    title, content, links = fetch_page(url)

    if not content.strip():
        print("Skipped:", url)
        return False

    words = clean_and_tokenize(content)

    conn = sqlite3.connect("search.db")
    cur = conn.cursor()

    # skip if already indexed
    cur.execute("SELECT id FROM pages WHERE url=?", (url,))
    if cur.fetchone():
        conn.close()
        return False

    # insert page
    cur.execute(
        "INSERT INTO pages (url, title, content) VALUES (?, ?, ?)",
        (url, title, content)
    )
    conn.commit()

    cur.execute("SELECT id FROM pages WHERE url=?", (url,))
    page_id = cur.fetchone()[0]

    # store links
    for link in links:
        cur.execute("INSERT INTO links (from_page, to_url) VALUES (?, ?)", (page_id, link))

    # word frequency
    counts = Counter(words)
    for word, freq in counts.items():
        cur.execute(
            "INSERT INTO index_table (word, page_id, frequency) VALUES (?, ?, ?)",
            (word, page_id, freq)
        )

    conn.commit()
    conn.close()

    print("Indexed:", url)
    return True


def main():
    urls = load_urls()
    print(f"Total URLs: {len(urls)}\n")

    success = 0

    for url in urls:
        if index_page(url):
            success += 1

    print(f"\nIndexed {success} pages")


if __name__ == "__main__":
    main()