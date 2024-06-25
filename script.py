import csv
import requests
from urllib.parse import quote
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
csv_file = 'ratings.csv'

modified_rows = []
with open(csv_file, mode='r', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)
    for row in csv_reader:
        name = row[1]
        # year = row[2]
        # letterboxd_uri = row[3]
        # rating = row[4]
        query = quote(name)
        api_key = "3d531900dfd51fafba64c48a9bb1babc"
        link = f"https://api.themoviedb.org/3/search/movie?query={query}&api_key={api_key}"
        
        res = requests.get(link)
        if res.status_code == 200:
            data = res.json()
            backdrop = "https://image.tmdb.org/t/p/w500" + data["results"][0]["backdrop_path"]
            # print(backdrop)
            row.append(backdrop)
        modified_rows.append(row)


if csv_file:
    with open(csv_file, mode='w', newline='', encoding='utf-8') as output_file:
        csv_writer = csv.writer(output_file)
        csv_writer.writerow("Backdrop")
        csv_writer.writerows(modified_rows)