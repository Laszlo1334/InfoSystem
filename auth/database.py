import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    with open('init.db.sql') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")

