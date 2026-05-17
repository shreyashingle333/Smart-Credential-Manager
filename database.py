import sqlite3

from security import hash_password

DB_NAME = "credentials.db"

# ================= DATABASE CONNECTION =================

def connect_db():

    return sqlite3.connect(DB_NAME)

# ================= CREATE TABLES =================

def init_db():

    conn = connect_db()

    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE,

            password_hash TEXT,

            salt TEXT,

            role TEXT DEFAULT 'user',

            security_answer TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS password_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            password_hash TEXT,

            salt TEXT,

            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            action TEXT,

            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    conn.close()

# ================= DEFAULT ADMIN =================

def ensure_admin():

    conn = connect_db()

    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username=?",
        ("admin",)
    )

    if not c.fetchone():

        ph, salt = hash_password("Admin@123")

        c.execute("""
            INSERT INTO users
            (username, password_hash, salt, role, security_answer)

            VALUES (?, ?, ?, ?, ?)
        """, (
            "admin",
            ph,
            salt,
            "admin",
            "admin"
        ))

        conn.commit()

    conn.close()

# ================= LOG ACTION =================

def log_action(user_id, action):

    conn = connect_db()

    c = conn.cursor()

    c.execute("""
        INSERT INTO logs (user_id, action)

        VALUES (?, ?)
    """, (user_id, action))

    conn.commit()

    conn.close()