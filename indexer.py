import sqlite3
from collections import Counter
from crawler import fetch_page
from text_processing import clean_and_tokenize


def fix_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url


def load_urls(file_path="urls.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
        return list(set(urls))  # remove duplicates
    except Exception as e:
        print("Error reading urls.txt:", e)
        return []


def index_page(url):
    url = fix_url(url)

    # Fetch page
    title, content,links = fetch_page(url)

    # Skip empty pages
    if not content.strip():
        print("Skipped empty page:", url)
        return False

    # Process text
    words = clean_and_tokenize(content)

    conn = sqlite3.connect("search.db")
    cur = conn.cursor()

    # Check if already indexed
    cur.execute("SELECT id FROM pages WHERE url=?", (url,))
    row = cur.fetchone()
    if row:
        print("Already indexed:", url)
        conn.close()
        return False

    # Insert page
    cur.execute(
        "INSERT INTO pages (url, title, content) VALUES (?, ?, ?)",
        (url, title, content)
    )
    conn.commit()

    # Get page ID
    cur.execute("SELECT id FROM pages WHERE url=?", (url,))
    page_id = cur.fetchone()[0]
    # 🔥 Store links
    for link in links:
        cur.execute("""
            INSERT INTO links (from_page, to_url)
            VALUES (?, ?)
            """, (page_id, link))
    # Count word frequencies
    word_counts = Counter(words)

    # Insert into index_table
    for word, freq in word_counts.items():
        cur.execute("""
            INSERT INTO index_table (word, page_id, frequency)
            VALUES (?, ?, ?)
        """, (word, page_id, freq))

    conn.commit()
    conn.close()

    print("Indexed:", url)
    return True


def index_all_urls():
    urls = load_urls()

    print("Loaded URLs:", urls)
    print(f"Total URLs: {len(urls)}\n")

    success = 0

    for url in urls:
        print("Processing:", url)
        try:
            if index_page(url):
                success += 1
        except Exception as e:
            print("Error indexing:", url)
            print("Reason:", e)

    print("\nIndexing completed!")
    print(f"Successfully indexed {success} pages")


# 🔥 MAIN ENTRY POINT
if __name__ == "__main__":
    index_all_urls()