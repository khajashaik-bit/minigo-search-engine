import sqlite3
def launch_db():
    conn=sqlite3.connect("search.db")
    cur=conn.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS pages(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                content TEXT
                );
                """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS index_table(
                    word TEXT,
                    page_id INTEGER,
                    frequency INTEGER,
                    PRIMARY KEY (word, page_id)
                );
                """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS links(
                from_page INTEGER,
                to_url TEXT
                );
                """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_word ON index_table(word);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_page ON index_table(page_id);")
    conn.commit()
    conn.close()
    print("Database created succesfully!")
if __name__=="__main__":
    launch_db()