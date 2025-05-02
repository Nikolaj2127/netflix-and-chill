import sqlite3
import csv

# Database connection
DATABASE = 'users.db'

def import_movies(tsv_file):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    with open(tsv_file, 'r') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            cursor.execute(
                """
                INSERT INTO Film (film_id, name, desc, genre, poster_url)
                VALUES (?, ?, ?, ?, ?)
                """,
                (row['film_id'], row['name'], row['desc'], row['genre'], row['poster_url'])
            )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    tsv_file = input("Enter the path to the TSV file: ")
    import_movies(tsv_file)
    print("Movies imported successfully!")