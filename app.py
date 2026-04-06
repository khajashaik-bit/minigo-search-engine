from flask import Flask, request, render_template, redirect, url_for
import sqlite3
import math
import re
from text_processing import clean_and_tokenize

app = Flask(__name__)


# ---------------------- SNIPPET GENERATION ----------------------
def generate_snippet(content, query_words, snippet_length=60):
    """
    Extract a small part of content around the first matched query word.
    Also highlights query words in the snippet.
    """
    content_lower = content.lower()

    for word in query_words:
        pos = content_lower.find(word.lower())

        if pos != -1:
            start = max(pos - snippet_length, 0)
            end = min(pos + snippet_length, len(content))
            snippet = content[start:end]

            # highlight words (case-insensitive)
            for w in query_words:
                pattern = re.compile(re.escape(w), re.IGNORECASE)
                snippet = pattern.sub(lambda m: f"<b>{m.group(0)}</b>", snippet)

            return "..." + snippet.strip() + "..."

    # fallback if no match found
    return content[:150] + "..." if len(content) > 150 else content


# ---------------------- PAGERANK ----------------------
def compute_pagerank():
    """
    Basic PageRank implementation using link structure.
    Each page distributes its rank to linked pages.
    """
    conn = sqlite3.connect("search.db")
    cur = conn.cursor()

    # get all pages
    cur.execute("SELECT id, url FROM pages")
    pages_data = cur.fetchall()

    pages = [row[0] for row in pages_data]
    url_to_id = {url: pid for pid, url in pages_data}

    N = len(pages)
    if N == 0:
        return {}

    # initial rank
    rank = {p: 1 / N for p in pages}
    damping = 0.85

    # build outgoing links map
    outgoing = {p: [] for p in pages}

    cur.execute("SELECT from_page, to_url FROM links")
    for from_page, to_url in cur.fetchall():
        if to_url in url_to_id:
            outgoing[from_page].append(url_to_id[to_url])

    # iterate multiple times
    for _ in range(10):
        new_rank = {p: (1 - damping) / N for p in pages}

        for p in pages:
            if outgoing[p]:
                share = rank[p] / len(outgoing[p])
                for q in outgoing[p]:
                    new_rank[q] += damping * share
            else:
                # if no outgoing links, distribute to all
                for q in pages:
                    new_rank[q] += damping * (rank[p] / N)

        rank = new_rank

    conn.close()
    return rank


# ---------------------- SEARCH FUNCTION ----------------------
def search_query(query):
    """
    Main search logic:
    - tokenize query
    - calculate TF-IDF score
    - combine with PageRank
    """
    query_words = clean_and_tokenize(query)

    conn = sqlite3.connect("search.db")
    cur = conn.cursor()

    scores = {}

    # total documents
    cur.execute("SELECT COUNT(*) FROM pages")
    total_docs = cur.fetchone()[0]

    # get pagerank values
    pagerank = compute_pagerank()

    for word in query_words:
        cur.execute("SELECT COUNT(*) FROM index_table WHERE word=?", (word,))
        df = cur.fetchone()[0]

        if df == 0:
            continue

        # smoothed idf
        idf = math.log((total_docs + 1) / (df + 1)) + 1

        cur.execute(
            "SELECT page_id, frequency FROM index_table WHERE word=?", (word,)
        )

        for page_id, tf in cur.fetchall():
            tf_score = 1 + math.log(tf)
            score = tf_score * idf

            scores[page_id] = scores.get(page_id, 0) + score

    # sort by TF-IDF
    sorted_pages = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    results = []

    for page_id, score in sorted_pages:
        cur.execute("SELECT title, url, content FROM pages WHERE id=?", (page_id,))
        row = cur.fetchone()

        if row:
            title, url, content = row

            # simple phrase boost
            if query.lower() in content.lower():
                score += 5

            # combine with pagerank
            final_score = score + pagerank.get(page_id, 0)

            snippet = generate_snippet(content, query_words)

            results.append((title, url, round(final_score, 2), snippet))

    conn.close()
    return results


# ---------------------- SUGGESTIONS ----------------------
def get_suggestions(prefix):
    """
    Return top matching words starting with given prefix.
    Used for autocomplete suggestions.
    """
    conn = sqlite3.connect("search.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT word, SUM(frequency) as freq
        FROM index_table
        WHERE word LIKE ?
        GROUP BY word
        ORDER BY freq DESC
        LIMIT 5
    """, (prefix + "%",))

    suggestions = [row[0] for row in cur.fetchall()]

    conn.close()
    return suggestions


# ---------------------- ROUTES ----------------------
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/results", methods=["GET", "POST"])
def results():
    query = request.values.get("query", "")

    # redirect POST -> GET (clean URL)
    if request.method == "POST":
        return redirect(url_for("results", query=query))

    results_data = search_query(query) if query else []

    return render_template(
        "results.html",
        query=query,
        results=results_data
    )


@app.route("/suggest")
def suggest():
    query = request.args.get("q", "")
    suggestions = get_suggestions(query)
    return {"suggestions": suggestions}


# ---------------------- MAIN ----------------------
if __name__ == "__main__":
    app.run(debug=True)