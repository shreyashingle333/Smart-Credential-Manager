import sqlite3

def init_vault():

    conn = sqlite3.connect(
        "vault/passwords.db"
    )

    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS vault (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT,
            username TEXT,
            password TEXT
        )
    """)

    conn.commit()

    conn.close()