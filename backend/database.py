import sqlite3

# Database connection
DATABASE = 'users.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database schema
def init_app():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create User table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            embedding BLOB NOT NULL
        )
    ''')

    # Create UserGroups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS UserGroups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id TEXT UNIQUE NOT NULL,
            user_ids TEXT NOT NULL
        )
    ''')

    # Create Film table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Film (
            film_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            desc TEXT,
            genre TEXT,
            poster_url TEXT
        )
    ''')

    conn.commit()
    conn.close()