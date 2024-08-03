import requests
from bs4 import BeautifulSoup
import csv 
from urllib.parse import quote
import sys
import io
from notion_client import Client

notion_token = "" # get your own notion token
database_id = "" # get your own notion database id (after putting in the correct fields)
notion = Client(auth=notion_token)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
movies = []
url = "https://letterboxd.com/karsab/films/diary" # change to your username

def scrape(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def get_data(soup):
    movies = []
    for e in soup.select('tr.diary-entry-row'):
        mapping = {
            'Jan': 'January',
            'Feb': 'February',
            'Mar': 'March',
            'Apr': 'April',
            'May': 'May',
            'Jun': 'June',
            'Jul': 'July',
            'Aug': 'August',
            'Sep': 'September',
            'Oct': 'October',
            'Nov': 'November',
            'Dec': 'December'
        }
        rating = e.find('div', class_='hide-for-owner').get_text().strip()
        title = e.find('td', class_='td-actions').get("data-film-name")  
        if(e.find('div', class_='date')):
            year = mapping[e.find('div', class_='date').a.get_text()] + " " + e.find('td', class_='td-calendar').find('small').get_text(strip=True)

        movie_url = 'https://letterboxd.com/film/' + e.find('td', class_='td-actions').get("data-film-slug")  
        #tmdb api
        api_key = "" # get your own api key for tmdb
        link = f"https://api.themoviedb.org/3/search/movie?query={quote(title)}&api_key={api_key}"
        res = requests.get(link)
        backdrop = ""
        if res.status_code == 200:
            res = res.json()
            backdrop = "https://image.tmdb.org/t/p/w500" + res["results"][0]["backdrop_path"]
        movies.append({
            'title': title,
            'rating': rating,
            'year': year,
            'movie_url': movie_url,
            'backdrop': backdrop
        })
    return movies

def add_to_notion(movie):
    properties = {
        "Title": {
            "title": [
                {
                    "text": {
                        "content": movie['title']
                    }
                }
            ]
        },
        "Rating": {
            "rich_text": [
                {
                    "text": {
                        "content": movie['rating']
                    }
                }
            ]
        },
        "Year": {
            "rich_text": [
                {
                    "text": {
                        "content": movie['year']
                    }
                }
            ]
        },
        "Movie URL": {
            "url": movie['movie_url']
        },
    }
    if movie['backdrop']:
        properties["Backdrop"] = {
            "files": [
                {
                    "name": movie['title'],
                    "external": {
                        "url": movie['backdrop']
                    }
                }
            ]
        }
    res = notion.databases.query(
        database_id = database_id,
        filter={
            "property": "Title",
            "rich_text": {
                "equals": movie["title"]
            }
        }
    )
    if len(res['results']) > 0:
        print("Found it!")
    else:
        print("Adding it!")
        print(movie["title"])
        notion.pages.create(parent={"database_id": database_id}, properties=properties)


page_num = 1
while True:
    new_url = f"{url}/page/{page_num}"
    soup = scrape(new_url)
    data = get_data(soup)
    if not data:
        break
    movies.extend(data)
    page_num += 1

movies.reverse()
for movie in movies:
    add_to_notion(movie)
print("all done yay!")
