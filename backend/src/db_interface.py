import sqlite3
from abc import ABC, abstractmethod
from qdrant_client import QdrantClient
from qdrant_client.http import models

class DB_interface(ABC):
    @abstractmethod
    def user_exists(self, uuid):
        pass
    
    @abstractmethod
    def movie_exists(self, movie_id):
        pass

    @abstractmethod
    def group_exists(self, group_id):
        pass

    @abstractmethod
    def create_group(self, group_id: str) -> bool:
        pass

    @abstractmethod
    def get_users_in_group(self, group_id: str) -> list:
        pass

    @abstractmethod
    def get_movie_info(self, movie_id: int) -> list:
        pass


class NaC_DB_Interface(DB_interface):

    def __init__(self):
        # Database connection
        self.DATABASE = 'users.db'
        self.client = QdrantClient(url="http://tobias-home.hindahl.de:6333/", api_key="check24")
        self.init_db()

    def get_db_connection(self):
        conn = sqlite3.connect(self.DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    # Initialize the database schema
    def init_db(self):
        with self.get_db_connection() as conn:
            cursor = conn.cursor()

            # Create User table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS User (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL
                )
            ''')

            # Create Groups table

            # For now this is a table, we might want to know additional data about the group.
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Groups (
                    group_id INTEGER PRIMARY KEY AUTOINCREMENT
                )''')

            # Create UserGroups association table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS UserGroups (
                    user_id INTEGER NOT NULL,
                    group_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, group_id),
                    FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
                    FOREIGN KEY (group_id) REFERENCES Groups(id) ON DELETE CASCADE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS UsersMovies (
                user_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, movie_id),
                FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
)
            ''')

    def user_exists(self, uuid):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM User WHERE user_id = ?', (uuid,))
                return cursor.fetchone() is not None
            
        except sqlite3.Error as e:
            print(f"Database error while checking user existence: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def movie_exists(self, movie_id):
        result = self.get_movie_info(movie_id)
        return result is not None
        
    def group_exists(self, group_id):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM Groups WHERE group_id = ?', (group_id,))
                return cursor.fetchone() is not None
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False

    def get_user_movie_ids(self, user_id):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT movie_id FROM UsersMovies WHERE user_id = ?",
                    (user_id,)
                )

                rows = cursor.fetchall()
                return [row[0] for row in rows]  # Extract movie_ids from the rows

        except sqlite3.Error as e:
            raise RuntimeError(f"Database error while fetching user movies: {e}")

        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")

    def add_user_movie_pair(self, user_id, movie_id):
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "INSERT OR IGNORE INTO UsersMovies (user_id, movie_id) VALUES (?, ?)",
                    (user_id, movie_id)
                )

        except sqlite3.Error as e:
            raise RuntimeError(f"Database error while adding user to group: {e}")

        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")

    def add_user_to_group(self, user_id: str, group_id: str) -> bool:
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()

                # Insert association into UserGroups
                cursor.execute(
                    "INSERT OR IGNORE INTO UserGroups (user_id, group_id) VALUES (?, ?)",
                    (user_id, group_id)
                )
            
        except sqlite3.Error as e:
            raise RuntimeError(f"Database error while adding user to group: {e}")
        
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")
        
    def create_group(self) -> int:
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO Groups DEFAULT VALUES;')
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error while creating group: {e}")
            return -1
        except Exception as e:
            print(f"Unexpected error: {e}")
            return -1
        
    def get_users_in_group(self, group_id: str) -> list:
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                query = '''
                    SELECT u.user_id
                    FROM User u
                    JOIN UserGroups ug ON u.id = ug.user_id
                    JOIN Groups g ON g.id = ug.group_id
                    WHERE g.group_id = ?
                '''
                cursor.execute(query, (group_id,))
                rows = cursor.fetchall()
                return [row["user_id"] for row in rows]
        except sqlite3.Error as e:
            print(f"Database error while retrieving users in group '{group_id}': {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
        
    def get_movie_info(self, movie_id: int):
        try:
            result = self.client.retrieve(
                collection_name="movies_top1000_1024",
                ids=[movie_id],
            )

            return {
                        "name": result[0].payload["title"],
                        "short_desc": result[0].payload["short_plot"],
                        "poster_url": result[0].payload["image_url"]
                    }

        except Exception as e:
            raise e
