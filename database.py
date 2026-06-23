import sqlite3

DB_NAME = "study_app.db"


# ---------------- CONNECT ----------------
def connect():
    return sqlite3.connect(DB_NAME)


# ---------------- CREATE TABLES ----------------
def init_db():
    conn = connect()
    cur = conn.cursor()

    # Notes table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            content TEXT
        )
    """)

    # Chat history table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            question TEXT,
            answer TEXT
        )
    """)

    conn.commit()
    conn.close()


# ---------------- SAVE NOTES ----------------
def save_note(username, content):
    conn = connect()
    cur = conn.cursor()

    cur.execute("INSERT INTO notes (username, content) VALUES (?, ?)",
                (username, content))

    conn.commit()
    conn.close()


# ---------------- GET NOTES ----------------
def get_notes(username):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT content FROM notes WHERE username=?", (username,))
    data = cur.fetchall()

    conn.close()
    return data


# ---------------- SAVE CHAT ----------------
def save_chat(username, question, answer):
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO chats (username, question, answer)
        VALUES (?, ?, ?)
    """, (username, question, answer))

    conn.commit()
    conn.close()


# ---------------- GET CHAT ----------------
def get_chats(username):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT question, answer FROM chats WHERE username=?", (username,))
    data = cur.fetchall()

    conn.close()
    return data