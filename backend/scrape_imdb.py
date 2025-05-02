import sqlite3
import requests
from bs4 import BeautifulSoup
import time

# Database connection
DATABASE = 'users.db'

# IMDb URL for the top 1000 movies
IMDB_URL = "https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,asc"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.imdb.com/'
}

def scrape_imdb():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    page = 1
    while page <= 50:  # IMDb shows 50 movies per page, so 20 pages for 1000 movies
        print(f"Scraping page {page}...")
        response = requests.get(f"{IMDB_URL}&start={(page - 1) * 50 + 1}", headers=HEADERS)

        # Debugging: Check response status and redirection
        print(f"Response status: {response.status_code}")
        if response.history:
            print("Request was redirected. Check the final URL:", response.url)
        if response.status_code != 200:
            print("Failed to fetch the page. Skipping...")
            page += 1
            time.sleep(2)  # Add a delay before the next request
            continue

        soup = BeautifulSoup(response.text, 'html.parser')

        # Debugging: Print the HTML content of the page
        print(soup.prettify()[:1000])  # Print the first 1000 characters of the HTML for inspection

        # Update the class name based on the IMDb page structure
        movies = soup.find_all('div', class_="ipc-metadata-list-summary-item__tc")  # Replace with the correct class name

        # Debugging: Print the number of movies found
        print(f"Number of movies found: {len(movies)}")

        if not movies:
            print("No movies found on this page. Check the HTML structure.")
            break

        for movie in movies:
            try:
                name = movie.find_all('h3', class_="ipc-title__text")
                desc = movie.find_all('div', class_='ipc-html-content-inner-div')
                genre = movie.find_all('li', class_='ipc-inline-list__item')
                print(genre)
                poster_url = movie.find('img', class_='ipc-image')

                cursor.execute(
                    """
                    INSERT INTO Film (name, desc, genre, poster_url)
                    VALUES (?, ?, ?, ?)
                    """,
                    (name, desc, genre, poster_url)
                )
            except Exception as e:
                print(f"Error processing movie: {e}")

        conn.commit()
        page += 1
        time.sleep(2)  # Add a delay before the next request

    conn.close()
    print("Scraping completed and data inserted into the database.")

if __name__ == "__main__":
    scrape_imdb()