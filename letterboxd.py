import requests
from bs4 import BeautifulSoup
import csv 
from urllib.parse import quote
import sys
import io
from notion_client import Client
import os

notion_token = "" # get your own notion token
database_id = "" # get your own notion database id (after putting in the correct fields)
notion = Client(auth=notion_token)

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
movies = []
url = "https://letterboxd.com/karsab/films/by/date/" # change to your username

def scrape(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

def get_data(soup):
    movies = []
    for e in soup.select('li.poster-container'):
        title = e.img.get('alt')
        rating = e.find('span', class_='rating').get_text()  
        movie_url = 'https://letterboxd.com/films/' + e.find("div").get("data-film-slug")
        #tmdb api
        api_key = "" # get your own api key for tmdb
        link = f"https://api.themoviedb.org/3/search/movie?query={quote(title)}&api_key={api_key}"
        res = requests.get(link)
        backdrop = year = ""
        if res.status_code == 200:
            res = res.json()
            backdrop = "https://image.tmdb.org/t/p/w500" + res["results"][0]["backdrop_path"]
            year = res["results"][0]["release_date"][:4]
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
    notion.pages.create(parent={"database_id": database_id}, properties=properties)

page_num = 1
while True:
    new_url = f"{url}page/{page_num}"
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