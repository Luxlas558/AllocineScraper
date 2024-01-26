import os
import requests
import zipfile
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from configparser import ConfigParser
import json
import re
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import sys
import shutil
from urllib.parse import quote
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import subprocess
import mysql.connector
from mysql.connector import Error
import configparser
def download_and_extract_chromedriver():
    if not os.path.isfile("chromedriver.exe"):
        print("Téléchargement du pilote ChromeDriver...")
        url = ChromeDriverManager().install()
        response = requests.get(url)
        with open("chromedriver_win32.zip", "wb") as f:
            f.write(response.content)
        with zipfile.ZipFile("chromedriver_win32.zip", "r") as zip_ref:
            zip_ref.extractall()
        print("Pilote ChromeDriver téléchargé et extrait.")
    else:
        print("")
def scroll_to_bottom(driver):
    current_height = driver.execute_script(
        "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
    for i in range(0, current_height, 500):
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(0.1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
def clean_title_from_date(title):
    cleaned_title = re.sub(r'\([^)]*\)', '', title).strip()
    return cleaned_title
def download_and_save_image(url, title):
    clean_title = re.sub(r'\W+', '', title)
    base_image_path = os.path.join("Covers", f"{clean_title}.jpg")
    if not os.path.exists("Covers"):
        os.makedirs("Covers")
    image_path = base_image_path
    existing_data = load_existing_data()
    same_titles = [item for item in existing_data['data']
                   if item['title'] == title]
    if len(same_titles) > 1:
        counter = 1
        while os.path.isfile(image_path):
            image_path = f"{base_image_path[:-4]}_{counter}.jpg"
            counter += 1
    response = requests.get(url)
    if response.status_code == 200:
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print(f"Image dans le dossier : {image_path}")
    else:
        print(f"Échec du téléchargement de l'image pour {
              title}. Code de statut : {response.status_code}")
def url_to_parse(url="") -> BeautifulSoup:
    driver = None
    try:
        download_and_extract_chromedriver()
        driver = webdriver.Chrome()
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "content-layout")))
        scroll_to_bottom(driver)
        page_content = driver.page_source
        soup = BeautifulSoup(page_content, "lxml")
        return soup
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return None
    finally:
        if driver:
            driver.quit()
def parse_to_data(soup_list=[], page_type="") -> dict:
    film_number = 0
    films_dico = {"data_number": film_number, "data": []}
    if page_type == "cinema":
        for soup in soup_list:
            films_container = soup.find(
                "main", {"id": "content-layout"}).findAll("li", {"class": "mdl"})
            for film_container in films_container:
                if film_container is not None:
                    try:
                        film_data = {"type": "film"}
                        title_element = film_container.find(
                            "h2", {"class": "meta-title"})
                        film_data["title"] = clean_title_from_date(
                            title_element.text.strip())
                        description_element = film_container.find(
                            "div", {"class": "meta-body-item meta-body-info"})
                        description = description_element.text.replace(
                            "\n", " ").strip().split("|") if description_element else []
                        film_data["release_date"] = description[0].strip(
                        ) if description and len(description) > 0 else None
                        film_data["length"] = description[1].strip(
                        ) if description and len(description) > 1 else None
                        film_data["genres"] = [genre.strip() for genre in description[2].split(
                            ",")] if description and len(description) > 2 else []
                        director_element = film_container.find(
                            "div", {"class": "meta-body-item meta-body-direction"})
                        film_data["director"] = director_element.text.replace(
                            "\n", " ").strip()[3:] if director_element else None
                        actors_element = film_container.find(
                            "div", {"class": "meta-body-item meta-body-actor"})
                        actors = actors_element.text.replace("\n", " ").strip()[
                            5:].split(",") if actors_element else []
                        film_data["actors"] = [x.strip() for x in actors]
                        synopsis_element = film_container.find(
                            "div", {"class": "synopsis"})
                        film_data["synopsis"] = synopsis_element.text.replace(
                            "\n", " ").strip() if synopsis_element else None
                        ratings = film_container.findAll(
                            "div", {"class": "rating-item"})
                        ratings = [rate.text.replace("\n", " ").strip(
                        ) for rate in ratings[:-1]] if ratings else []
                        ratings = " ".join(ratings)
                        film_data["rating"] = {
                            "critics": float(r) if (r := re.sub(r'Presse\s*(\d*),(\d*).*', r'\1.\2', ratings)) != ratings else 'N/A',
                            "audience": float(r) if (r := re.sub(r'.*Spectateurs\s*(\d*),(\d*).*', r'\1.\2', ratings)) != ratings else 'N/A'
                        }
                        img_url_element = film_container.find(
                            "img", {"class": "thumbnail-img"})
                        img_url = img_url_element["src"] if img_url_element else None
                        download_and_save_image(
                            img_url, film_data["title"]) if img_url else None
                        film_number += 1
                        films_dico["data"].append(film_data)
                    except Exception as e:
                        pass
    elif page_type == "action":
        for soup in soup_list:
            films_container = soup.find_all("li", {"class": "mdl"})
            for film_container in films_container:
                if film_container is not None:
                    try:
                        film_data = {"type": "film"}
                        title_element = film_container.find(
                            "h2", {"class": "meta-title"})
                        film_data["title"] = clean_title_from_date(
                            title_element.text.strip())
                        actors_element = film_container.find(
                            "div", {"class": "meta-body-item meta-body-actor"})
                        actors = [actor.text.strip() for actor in actors_element.find_all(
                            "a")] if actors_element else []
                        film_data["actors"] = actors
                        director_element = film_container.find(
                            "div", {"class": "meta-body-item meta-body-direction"}).find("a")
                        film_data["director"] = director_element.text.strip(
                        ) if director_element else None
                        info_element = film_container.find(
                            "div", {"class": "meta-body-item meta-body-info"})
                        img_url_element = film_container.find(
                            "img", {"class": "thumbnail-img"})
                        img_url = img_url_element["src"] if img_url_element else None
                        download_and_save_image(
                            img_url, film_data["title"]) if img_url else None
                        if info_element:
                            duration_and_genres = info_element.get_text(
                                strip=True).split('|')
                            film_data["length"] = duration_and_genres[0].strip() if len(
                                duration_and_genres) > 0 else None
                            film_data["genres"] = [genre.strip() for genre in duration_and_genres[1].split(",")] if len(
                                duration_and_genres) > 1 else []
                        else:
                            film_data["length"] = None
                            film_data["genres"] = []
                        critics_rating_element = film_container.find(
                            "span", {"class": "stareval-note"})
                        critics_rating = float(critics_rating_element.text.replace(
                            ",", ".")) if critics_rating_element else None
                        audience_rating_element = film_container.find("div", {"class": "rating-item"}).find("span",
                                                                                                            {"class": "stareval-note"})
                        audience_rating = float(
                            audience_rating_element.text.replace(",", ".")) if audience_rating_element else None
                        film_data["rating"] = {
                            "critics": critics_rating,
                            "audience": audience_rating
                        }
                        synopsis_element = film_container.find(
                            "div", {"class": "synopsis"})
                        film_data["synopsis"] = synopsis_element.find("div", {"class": "content-txt"}).text.strip() if synopsis_element and synopsis_element.find(
                            "div", {"class": "content-txt"}) else None
                        clean_title = re.sub(
                            r'\W+', '', film_data["title"]) if film_data["title"] else None
                        film_data["image"] = os.path.join("Covers", f"{clean_title}.jpg").replace(
                            "\\", "/") if clean_title else None
                        film_number += 1
                        films_dico["data"].append(film_data)
                    except Exception as e:
                        pass
    elif page_type == "serie":
        for soup in soup_list:
            films_container = soup.find_all("li", {"class": "mdl"})
        for film_container in films_container:
            if film_container is not None:
                try:
                    film_data = {"type": "serie"}
                    title_element = film_container.find(
                        "h2", {"class": "meta-title"})
                    film_data["title"] = clean_title_from_date(
                        title_element.text.strip())
                    actors_element = film_container.find(
                        "div", {"class": "meta-body-item meta-body-actor"})
                    film_data["actors"] = [actor.text.strip() for actor in actors_element.find_all(
                        "a")] if actors_element else []
                    info_element = film_container.find(
                        "div", {"class": "meta-body-item meta-body-info"})
                    img_url_element = film_container.find(
                        "img", {"class": "thumbnail-img"})
                    img_url = img_url_element["src"] if img_url_element else None
                    download_and_save_image(
                        img_url, film_data["title"]) if img_url else None
                    if info_element:
                        genre_elements = info_element.find_all('a')
                        film_data["genres"] = [genre_element.text.strip()
                                               for genre_element in genre_elements]
                    else:
                        film_data["genres"] = []
                    critics_rating_element = film_container.find(
                        "span", {"class": "stareval-note"})
                    critics_rating = float(critics_rating_element.text.replace(
                        ",", ".")) if critics_rating_element else None
                    audience_rating_element = film_container.find(
                        "div", {"class": "rating-item"}).find("span", {"class": "stareval-note"})
                    audience_rating = float(audience_rating_element.text.replace(
                        ",", ".")) if audience_rating_element else None
                    film_data["rating"] = {
                        "critics": critics_rating, "audience": audience_rating}
                    synopsis_element = film_container.find(
                        "div", {"class": "synopsis"})
                    if synopsis_element:
                        content_txt_element = synopsis_element.find(
                            "div", {"class": "content-txt"})
                        film_data["synopsis"] = content_txt_element.text.strip(
                        ) if content_txt_element else None
                    else:
                        film_data["synopsis"] = None
                    clean_title = re.sub(
                        r'\W+', '', film_data["title"]) if film_data["title"] else None
                    film_data["image"] = os.path.join("Covers", f"{clean_title}.jpg").replace(
                        "\\", "/") if clean_title else None
                    film_number += 1
                    films_dico["data"].append(film_data)
                except Exception as e:
                    pass
    elif page_type == "everyfilm":
        for soup in soup_list:
            films_container = soup.find_all("li", {"class": "mdl"})
        for film_container in films_container:
            if film_container is not None:
                try:
                    film_data = {"type": "film"}
                    title_element = film_container.find(
                        "h2", {"class": "meta-title"})
                    film_data["title"] = clean_title_from_date(
                        title_element.text.strip())
                    actors_element = film_container.find(
                        "div", {"class": "meta-body-item meta-body-actor"})
                    actors = [actor.text.strip() for actor in actors_element.find_all(
                        "a")] if actors_element else []
                    film_data["actors"] = actors
                    director_element = film_container.find(
                        "div", {"class": "meta-body-item meta-body-direction"}).find("a")
                    film_data["director"] = director_element.text.strip(
                    ) if director_element else None
                    info_element = film_container.find(
                        "div", {"class": "meta-body-item meta-body-info"})
                    release_date_element = info_element.find(
                        "span", {"class": "date"})
                    film_data["release_date"] = release_date_element.text.strip(
                    ) if release_date_element else None
                    img_url_element = film_container.find(
                        "img", {"class": "thumbnail-img"})
                    img_url = img_url_element["src"] if img_url_element else None
                    download_and_save_image(
                        img_url, film_data["title"]) if img_url else None
                    if info_element:
                        date_duration_genres = info_element.get_text(
                            strip=True).split('|')
                        film_data["release_date"] = date_duration_genres[0].strip()
                        film_data["length"] = date_duration_genres[1].strip() if len(
                            date_duration_genres) > 1 else None
                        genres_str = date_duration_genres[2] if len(
                            date_duration_genres) > 2 else ""
                        genres = [genre.strip() for genre in genres_str.split(
                            ',')] if genres_str else []
                        film_data["genres"] = genres
                    else:
                        film_data["release_date"] = None
                        film_data["length"] = None
                        film_data["genres"] = None
                    critics_rating_element = film_container.find(
                        "span", {"class": "stareval-note"})
                    critics_rating = float(critics_rating_element.text.replace(
                        ",", ".")) if critics_rating_element else None
                    audience_rating_element = film_container.find(
                        "div", {"class": "rating-item"}).find("span", {"class": "stareval-note"})
                    audience_rating = float(audience_rating_element.text.replace(
                        ",", ".")) if audience_rating_element else None
                    film_data["rating"] = {
                        "critics": critics_rating,
                        "audience": audience_rating
                    }
                    synopsis_element = film_container.find(
                        "div", {"class": "synopsis"})
                    film_data["synopsis"] = synopsis_element.find("div", {"class": "content-txt"}).text.strip(
                    ) if synopsis_element and synopsis_element.find("div", {"class": "content-txt"}) else None
                    clean_title = re.sub(
                        r'\W+', '', film_data["title"]) if film_data["title"] else None
                    film_data["image"] = os.path.join("Covers", f"{clean_title}.jpg").replace(
                        "\\", "/") if clean_title else None
                    film_number += 1
                    films_dico["data"].append(film_data)
                except Exception as e:
                    pass
    elif page_type == "everyserie":
        for soup in soup_list:
            films_container = soup.find_all("li", {"class": "mdl"})
        for film_container in films_container:
            if film_container is not None:
                try:
                    film_data = {"type": "serie"}
                    title_element = film_container.find(
                        "h2", {"class": "meta-title"})
                    film_data["title"] = clean_title_from_date(
                        title_element.text.strip())
                    actors_element = film_container.find(
                        "div", {"class": "meta-body-item meta-body-actor"})
                    actors = [actor.text.strip() for actor in actors_element.find_all(
                        "a")] if actors_element else []
                    film_data["actors"] = actors
                    director_element = film_container.find(
                        "div", {"class": "meta-body-item meta-body-direction"}).find("a")
                    film_data["director"] = director_element.text.strip(
                    ) if director_element else None
                    info_element = film_container.find(
                        "div", {"class": "meta-body-item meta-body-info"})
                    release_date_element = info_element.find(
                        "span", {"class": "date"})
                    film_data["release_date"] = release_date_element.text.strip(
                    ) if release_date_element else None
                    img_url_element = film_container.find(
                        "img", {"class": "thumbnail-img"})
                    img_url = img_url_element["src"] if img_url_element else None
                    download_and_save_image(
                        img_url, film_data["title"]) if img_url else None
                    if info_element:
                        date_duration_genres = info_element.get_text(
                            strip=True).split('|')
                        film_data["release_date"] = date_duration_genres[0].strip()
                        film_data["length"] = date_duration_genres[1].strip() if len(
                            date_duration_genres) > 1 else None
                        genres_str = date_duration_genres[2] if len(
                            date_duration_genres) > 2 else ""
                        genres = [genre.strip() for genre in genres_str.split(
                            ',')] if genres_str else []
                        film_data["genres"] = genres
                    else:
                        film_data["release_date"] = None
                        film_data["length"] = None
                        film_data["genres"] = None
                    critics_rating_element = film_container.find(
                        "span", {"class": "stareval-note"})
                    critics_rating = float(critics_rating_element.text.replace(
                        ",", ".")) if critics_rating_element else None
                    audience_rating_element = film_container.find(
                        "div", {"class": "rating-item"}).find("span", {"class": "stareval-note"})
                    audience_rating = float(audience_rating_element.text.replace(
                        ",", ".")) if audience_rating_element else None
                    film_data["rating"] = {
                        "critics": critics_rating,
                        "audience": audience_rating
                    }
                    synopsis_element = film_container.find(
                        "div", {"class": "synopsis"})
                    film_data["synopsis"] = synopsis_element.find("div", {"class": "content-txt"}).text.strip(
                    ) if synopsis_element and synopsis_element.find("div", {"class": "content-txt"}) else None
                    clean_title = re.sub(
                        r'\W+', '', film_data["title"]) if film_data["title"] else None
                    film_data["image"] = os.path.join("Covers", f"{clean_title}.jpg").replace(
                        "\\", "/") if clean_title else None
                    film_number += 1
                    films_dico["data"].append(film_data)
                except Exception as e:
                    pass
    else:
        print(f"Final Titles: {[film['title']
              for film in films_dico['data']]}")
        print(f"Unknown page type: {page_type}.")
    films_dico["data_number"] = film_number
    return films_dico
def data_to_json(data=None, filename="data.json") -> None:
    with open(filename, 'w', encoding='utf8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
def data_to_csv(data: dict = None, filename="data.csv") -> None:
    data_frame = {
        "title": [film["title"] for film in data["data"]],
        "release_date": [film["release_date"] for film in data["data"]],
        "length": [film["length"] for film in data["data"]],
        "type": [film["type"] for film in data["data"]],
        "director": [film["director"] for film in data["data"]],
        "actors": [film["actors"] for film in data["data"]],
        "synopsis": [film["synopsis"] for film in data["data"]],
        "sessions": [film["sessions"] for film in data["data"]],
        'rating': [film["rating"] for film in data["data"]],
        "image": [os.path.join("Covers", f"{re.sub(r'\W+', '', film['title'])}.jpg").replace("\\", "/") for film in data["data"]]
    }
    data_frame = pd.DataFrame.from_dict(data_frame)
    data_frame.to_csv(filename, index=False, header=True, encoding='utf-8')
def load_existing_data(filename="data.json") -> dict:
    if os.path.isfile(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r', encoding='utf8') as json_file:
            existing_data = json.load(json_file)
    else:
        default_data = {"data_number": 0, "data": []}
        with open(filename, 'w', encoding='utf8') as json_file:
            json.dump(default_data, json_file, indent=4)
        existing_data = default_data
    return existing_data
def update_existing_data(existing_data: dict, new_films: list) -> dict:
    new_films = [new_film for new_film in new_films if new_film['synopsis'] not in [
        film['synopsis'] for film in existing_data['data']]]
    for film in existing_data['data']:
        if all(value is None or (isinstance(value, list) and len(value) == 0) for value in film.values()):
            existing_data['data'].remove(film)
            existing_data['data_number'] -= 1
    existing_data['data'].extend(new_films)
    existing_data['data_number'] = len(existing_data['data'])
    return existing_data
def clean_data():
    try:
        if os.path.exists("data.json"):
            os.remove("data.json")
            print("Le fichier data.json à était supprimé avec succès.")
        if os.path.exists("Covers"):
            shutil.rmtree("Covers")
            print("Dossier Covers supprimé avec succès.")
    except Exception as e:
        pass
def clean_alldata():
    try:
        if os.path.exists("data.json"):
            os.remove("data.json")
            print("Le fichier data.json à était supprimé avec succès.")
        else:
            pass
        if os.path.exists("Covers"):
            shutil.rmtree("Covers")
            print("Dossier Covers supprimé avec succès.")
        else:
            pass
        if os.path.exists("Tri"):
            shutil.rmtree("Tri")
            print("Dossier Tri supprimé avec succès.")
        else:
            pass
    except Exception as e:
        pass
def trier_series_films(data):
    initial_covers_directory = 'Covers'
    series_data = {"data_number": 0, "data": []}
    films_data = {"data_number": 0, "data": []}
    for item in data['data']:
        if item['type'] == 'serie':
            series_data['data'].append(item)
        elif item['type'] == 'film':
            films_data['data'].append(item)
    series_data['data_number'] = len(series_data['data'])
    films_data['data_number'] = len(films_data['data'])
    if not os.path.exists('Tri'):
        os.makedirs('Tri')
    if not os.path.exists('Tri/series-films'):
        os.makedirs('Tri/series-films')
    if not os.path.exists('Tri/series-films/cover_serie'):
        os.makedirs('Tri/series-films/cover_serie')
    if not os.path.exists('Tri/series-films/cover_film'):
        os.makedirs('Tri/series-films/cover_film')
    for i, item in enumerate(data['data']):
        if 'image' in item:
            cover_path = os.path.join(
                initial_covers_directory, os.path.basename(item['image']))
            cover_type = 'cover_serie' if item['type'] == 'serie' else 'cover_film'
            if os.path.exists(cover_path):
                destination_directory = os.path.join(
                    'Tri/series-films', cover_type)
                if not os.path.exists(destination_directory):
                    os.makedirs(destination_directory)
                destination_path = os.path.join(
                    destination_directory, os.path.basename(cover_path))
                try:
                    if os.path.exists(destination_path):
                        os.remove(destination_path)
                    shutil.move(cover_path, destination_path)
                    data['data'][i]['image'] = os.path.basename(destination_path)
                except Exception as e:
                    pass
    for item in data['data']:
        if 'image' in item:
            item['image'] = item['image'].replace("Covers/", "")
    covers_directory = initial_covers_directory
    try:
        for file_name in os.listdir(covers_directory):
            file_path = os.path.join(covers_directory, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                pass
    except Exception as e:
        pass
    with open('Tri/series-films/film.json', 'w', encoding='utf-8') as films_file:
        json.dump(films_data, films_file, ensure_ascii=False, indent=4)
    with open('Tri/series-films/serie.json', 'w', encoding='utf-8') as series_file:
        json.dump(series_data, series_file, ensure_ascii=False, indent=4)
    print("Le tri est terminé.")
def scrape_page(parser, url_template, max_page, page_type, start_page):
    try:
        start_page = int(start_page)
        max_page = int(max_page)
    except ValueError:
        print("Error: 'start_page' and 'max_page' must be integers.")
        return
    for i in range(start_page, max_page + 1):
        url = f"{url_template}{i}"
        print(f"Scraping URL: {url}")
        soup = url_to_parse(url)
        if soup:
            if page_type == "cinema":
                new_data = parse_to_data([soup], page_type)
            elif page_type == "action":
                new_data = parse_to_data([soup], page_type)
            elif page_type == "serie":
                new_data = parse_to_data([soup], page_type)
            elif page_type == "everyfilm":
                new_data = parse_to_data([soup], page_type)
            elif page_type == "everyserie":
                new_data = parse_to_data([soup], page_type)
            else:
                print(f"Unknown page type: {page_type}.")
                return
            existing_data = load_existing_data()
            updated_data = update_existing_data(
                existing_data, new_data['data'])
            output_file = parser['Files']['output_file']
            if len(sys.argv) > 1 and sys.argv[1].lower() == 'json':
                data_to_json(updated_data, output_file)
            else:
                data_to_json(updated_data, output_file)
def databaseserie():
    try:
        with open('./Tri/series-films/serie.json', 'r', encoding='utf-8') as file:
            serie_data = json.load(file)
    except FileNotFoundError:
        print("Le fichier serie.json n'a pas été trouvé.")
        sys.exit()
    config = configparser.ConfigParser()
    config.read('config.ini')
    db_config = {
        'host': config['Database']['host'],
        'database': config['Database']['database'],
        'user': config['Database']['user'],
        'password': config['Database']['password'],
    }
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS series (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titre VARCHAR(191),
                annee INT,
                genre VARCHAR(255),
                acteurs TEXT,
                synopsis TEXT,
                image VARCHAR(255),
                UNIQUE KEY unique_title (titre)
            )
            '''
            cursor.execute(create_table_query)
            print("La table 'series' a été créée avec succès.")
            insert_query = '''
            INSERT IGNORE INTO series (titre, annee, genre, acteurs, synopsis, image)
            VALUES (%s, %s, %s, %s, %s, %s)
            '''
            for serie in serie_data["data"]:
                image_path = serie.get('image', '')
                image_filename = os.path.basename(image_path)
                record = tuple(None if v == '' else v for v in (
                    serie.get('title', ''),
                    serie.get('release_date', '').split(
                        ' ')[-1] if 'release_date' in serie else 0,
                    ' '.join(serie.get('genres', [])
                             ) if 'genres' in serie else '',
                    ', '.join(serie.get('actors', [])
                              ) if 'actors' in serie else '',
                    serie.get('synopsis', ''),
                    image_filename,
                ))
                try:
                    print(f"Insertion de la série : {serie.get('title', '')}")
                    cursor.execute(insert_query, record)
                except mysql.connector.Error as err:
                    print(
                        f"Une erreur s'est produite pendant l'insertion : {err}")
            connection.commit()
    except mysql.connector.Error as e:
        print(f"Erreur pendant l'insertion des données : {e}")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Toutes les données ont été insérées avec succès.")
def databasefilm():
    try:
        with open('./Tri/series-films/film.json', 'r', encoding='utf-8') as file:
            film_data = json.load(file)
    except FileNotFoundError:
        print("Le fichier film.json n'a pas été trouvé.")
        sys.exit()
    config = configparser.ConfigParser()
    config.read('config.ini')
    db_config = {
        'host': config['Database']['host'],
        'database': config['Database']['database'],
        'user': config['Database']['user'],
        'password': config['Database']['password'],
    }
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            create_table_query = '''
            CREATE TABLE IF NOT EXISTS films (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titre VARCHAR(191),
                annee INT,
                genre VARCHAR(255),
                duree VARCHAR(100),
                note FLOAT,
                acteurs TEXT,
                realisateur VARCHAR(255),
                synopsis TEXT,
                image VARCHAR(255),
                critics_rating FLOAT,
                audience_rating FLOAT,
                UNIQUE KEY unique_title (titre)
            )
            '''
            cursor.execute(create_table_query)
            print("La table 'films' a été créée avec succès.")
            insert_query = '''
            INSERT IGNORE INTO films (titre, annee, genre, duree, note, acteurs, realisateur, synopsis, image, critics_rating, audience_rating)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            for film in film_data["data"]:
                image_path = film.get('image', '')
                image_filename = os.path.basename(image_path)
                record = (
                    film.get('title', ''),
                    film.get('release_date', '').split(
                        ' ')[-1] if 'release_date' in film else 0,
                    ' '.join(film.get('genres', [])
                             ) if 'genres' in film else '',
                    film.get('length', 0),
                    film.get('rating', {}).get('critics', 0.0),
                    ', '.join(film.get('actors', [])
                              ) if 'actors' in film else '',
                    film.get('director', ''),
                    film.get('synopsis', ''),
                    image_filename,
                    film.get('rating', {}).get('critics', 0.0),
                    film.get('rating', {}).get('audience', 0.0)
                )
                try:
                    print(f"Insertion du film : {film.get('title', '')}")
                    cursor.execute(insert_query, record)
                except mysql.connector.Error as err:
                    print(f"An error occurred: {err}")
            connection.commit()
    except mysql.connector.Error as e:
        print(f"Erreur pendant l'insertion des données : {e}")
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Toutes les données ont été insérées avec succès.")
def afficher_interface():
    def lancer_scraper():
        site = site_var.get()
        type_media = type_media_var.get()
        genre = genre_var.get()
        if type_media == 'Film':
            commande = f"python scraper.py {type_media} {genre}"
        elif type_media == 'Serie':
            commande = f"python scraper.py {type_media} {genre} --tri"
        subprocess.run(commande, shell=True)
        root.update_idletasks()
    def lancer_all():
        commande = "python scraper.py all"
        subprocess.run(commande, shell=True)
        root.update_idletasks()
    def lancer_everyall():
        commande = "python scraper.py everyall"
        subprocess.run(commande, shell=True)
        root.update_idletasks()
    def lancer_tri():
        commande = "python scraper.py tri"
        subprocess.run(commande, shell=True)
        root.update_idletasks()
    def lancer_clean():
        commande = "python scraper.py clean"
        subprocess.run(commande, shell=True)
        root.update_idletasks()
    def update_genres(*args):
        selected_type_media = type_media_var.get()
        new_genres = genres_film if selected_type_media == 'Film' else genres_serie
        genre_menu['values'] = new_genres
        genre_var.set(new_genres[0])
    root = tk.Tk()
    root.title("Scraper interface")
    style = ttk.Style()
    style.theme_use('clam')
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    ttk.Label(frame, text="Sélectionnez le site :").grid(
        row=0, column=0, pady=10, padx=10, sticky="w")
    ttk.Label(frame, text="Sélectionnez le type de média (film/serie) :").grid(row=1,
                                                                               column=0, pady=10, padx=10, sticky="w")
    ttk.Label(frame, text="Sélectionnez le genre :").grid(
        row=2, column=0, pady=10, padx=10, sticky="w")
    sites = ["Allociné"]
    site_var = tk.StringVar(value=sites[0])
    site_option_menu = ttk.Combobox(
        frame, textvariable=site_var, values=sites, state="readonly")
    site_option_menu.grid(row=0, column=1, pady=10, padx=10, sticky="ew")
    types_media = ["Film", "Serie"]
    type_media_var = tk.StringVar(value=types_media[0])
    type_media_var.trace_add('write', update_genres)
    type_media_option_menu = ttk.Combobox(
        frame, textvariable=type_media_var, values=types_media, state="readonly")
    type_media_option_menu.grid(row=1, column=1, pady=10, padx=10, sticky="ew")
    genres_film = ['Cinema', 'Action', 'Animation', 'Aventure', 'Biopic', 'Comedie', 'Comedie-dramatique',
                   'Drame', 'Epouvante-horreur', 'Famille', 'Fantastique', 'Guerre', 'Historique',
                   'Musical', 'Policier', 'Romance', 'Science-fiction', 'Thriller', 'Western']
    genres_serie = ['Meilleur', 'Action', 'Animation', 'Aventure', 'Biopic', 'Comedie', 'Comedie-dramatique',
                    'Drame', 'Epouvante-horreur', 'Espionnage', 'Famille', 'Fantastique', 'Historique',
                    'Judiciaire', 'Policier', 'Romance', 'Science-fiction', 'Thriller']
    global genre_var
    genre_var = tk.StringVar(value=genres_film[0])
    global genre_menu
    genre_menu = ttk.Combobox(
        frame, textvariable=genre_var, values=genres_film, state="readonly")
    genre_menu.grid(row=2, column=1, pady=10, padx=10, sticky="ew")
    ttk.Button(frame, text="Lancer le scraper", command=lancer_scraper).grid(
        row=3, column=0, columnspan=2, pady=20, sticky="ew")
    ttk.Button(frame, text="Lancer all", command=lancer_all).grid(
        row=4, column=0, pady=10, padx=10, sticky="ew")
    ttk.Button(frame, text="Lancer everyall", command=lancer_everyall).grid(
        row=4, column=1, pady=10, padx=10, sticky="ew")
    ttk.Button(frame, text="Lancer tri", command=lancer_tri).grid(
        row=5, column=0, pady=10, padx=10, sticky="ew")
    ttk.Button(frame, text="Lancer clean", command=lancer_clean).grid(
        row=5, column=1, pady=10, padx=10, sticky="ew")
    for i in range(5):
        frame.grid_rowconfigure(i, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
    root.mainloop()
def main():
    parser = ConfigParser()
    parser.read("config.ini")
    download_and_extract_chromedriver()
    try:
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            if command == 'clean':
                print("Supression des données...")
                clean_data()
                return
            elif command == 'clean-all':
                print("Supression des données...")
                clean_alldata()
                return
            elif command == 'tri':
                with open('data.json', 'r', encoding='utf-8') as file:
                    data = json.load(file)
                trier_series_films(data)
                return
            elif command in ['meilleur', 'action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique', 'drame', 'epouvante-horreur', 'espionnage', 'famille', 'fantastique', 'historique', 'judiciaire', 'policier', 'romance', 'science-fiction', 'thriller']:
                page_url = parser['Urls'][f'page_url_serie_{command}']
                start_page = int(parser['Urls'][f'start_page_serie_{command}'])
                max_page = int(
                    parser['Urls'][f'max_page_number_serie_{command}'])
                scrape_page(parser, page_url, max_page, 'serie')

                
            elif command in ['cinema', 'action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique',
                             'drame', 'epouvante-horreur', 'famille', 'fantastique', 'guerre', 'historique',
                             'musical', 'policier', 'romance', 'science-fiction', 'thriller', 'western']:
                page_url = parser['Urls'][f'page_url_{command}']
                start_page = int(parser['Urls'][f'start_page_{command}'])
                max_page = int(parser['Urls'][f'max_page_number_{command}'])
                scrape_page(parser, page_url, max_page, 'action')
            elif command == 'databasefilm':
                print("Executing film database command...")
                databasefilm()
            elif command == 'databaseserie':
                print("Executing serie database command...")
                databaseserie()
            elif command == 'databaseall':
                print("Executing databaseall command...")
                print("Executing film database command...")
                databasefilm()
                print("Executing serie database command...")
                databaseserie()
            elif command == 'everyserie':
                try:
                    print("Executing everyserie command...")
                    page_url = parser['Urls']['page_url_everyserie']
                    try:
                        start_page = int(
                            parser['Urls']['start_page_everyserie'].strip())
                    except ValueError:
                        print(
                            "Error: 'start_page_everyserie' in config.ini is not a valid integer.")
                        sys.exit(1)
                    max_page = int(
                        parser['Urls']['max_page_number_everyserie'].strip())
                    scrape_page(parser, page_url, max_page,
                                'everyserie', start_page)
                    with open('data.json', 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    trier_series_films(data)
                    print("Executing clean command...")
                    clean_data()
                except ValueError:
                    print("Error: 'start_page' and 'max_page' must be integers.")
                    return
            elif command == 'everyfilm':
                try:
                    print("Executing everyfilm command...")
                    page_url = parser['Urls']['page_url_everyfilm']
                    start_page = int(parser['Urls']['start_page_everyfilm'])
                    max_page = int(parser['Urls']['max_page_number_everyfilm'])
                    scrape_page(parser, page_url, max_page,
                                'everyfilm', start_page)
                    print("Executing tri command...")
                    with open('data.json', 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    trier_series_films(data)
                    print("Executing clean command...")
                    clean_data()
                except:
                    print(
                        "An error occured while executing everyfilm command. Please check your internet connection.")
            elif command == 'everyall':
                try:
                    print("Executing everyfilm command...")
                    page_url_everyfilm = parser['Urls']['page_url_everyfilm']
                    start_page = int(parser['Urls']['start_page_everyfilm'])
                    max_page_everyfilm = int(
                        parser['Urls']['max_page_number_everyfilm'])
                    scrape_page(parser, page_url_everyfilm,
                                max_page_everyfilm, 'everyfilm', start_page)
                    print("Executing everyserie command...")
                    page_url_everyserie = parser['Urls']['page_url_everyserie']
                    start_page = int(parser['Urls']['start_page_everyserie'])
                    max_page_everyserie = int(
                        parser['Urls']['max_page_number_everyserie'])
                    scrape_page(parser, page_url_everyserie,
                                max_page_everyserie, 'everyserie', start_page)
                    with open('data.json', 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    trier_series_films(data)
                    print("Executing clean command...")
                    clean_data()
                except:
                    print(
                        "An error occurred while executing everyall command. Please check your internet connection.")
            elif command == 'serie':
                if len(sys.argv) > 2:
                    genre_to_scrape = sys.argv[2].lower()
                    if genre_to_scrape in ['meilleur', 'action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique',
                                           'drame', 'epouvante-horreur', 'espionnage', 'famille', 'fantastique', 'historique',
                                           'judiciaire', 'policier', 'romance', 'science-fiction', 'thriller']:
                        page_url = parser['Urls'][f'page_url_serie_{
                            genre_to_scrape}']
                        start_page = int(
                            parser['Urls'][f'start_page_serie_{genre_to_scrape}'])
                        max_page = int(
                            parser['Urls'][f'max_page_number_serie_{genre_to_scrape}'])
                        scrape_page(parser, page_url, max_page,
                                    'serie', start_page)
                    else:
                        print(f"Unknown genre. Use one of the following genres: {' '.join(
                            ['action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique',
                                'drame', 'epouvante-horreur', 'espionnage', 'famille', 'fantastique', 'historique',
                                'judiciaire', 'policier', 'romance', 'science-fiction', 'thriller'])}.")
                        return
                else:
                    print(f"Unknown genre. Use one of the following genres: {' '.join(
                        ['action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique',
                            'drame', 'epouvante-horreur', 'espionnage', 'famille', 'fantastique', 'historique',
                            'judiciaire', 'policier', 'romance', 'science-fiction', 'thriller'])}.")
                    return
            elif command == 'serie-all':
                genres_to_scrape = ['meilleur', 'action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique',
                                    'drame', 'epouvante-horreur', 'espionnage', 'famille', 'fantastique', 'historique',
                                    'judiciaire', 'policier', 'romance', 'science-fiction', 'thriller']
                for genre in genres_to_scrape:
                    page_url_key = f'page_url_serie_{genre}'
                    start_page_key = f'start_page_serie_{genre}'
                    max_page_key = f'max_page_number_serie_{genre}'
                    if page_url_key in parser['Urls'] and max_page_key in parser['Urls']:
                        page_url = parser['Urls'][page_url_key]
                        start_page = int(parser['Urls'][start_page_key])
                        max_page = int(parser['Urls'][max_page_key])
                        scrape_page(parser, page_url, max_page,
                                    'serie', start_page)
                    else:
                        pass
            elif command == 'film-all':
                genres_to_scrape = ['action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique',
                                    'drame', 'epouvante-horreur', 'famille', 'fantastique', 'guerre', 'historique',
                                    'musical', 'policier', 'romance', 'science-fiction', 'thriller', 'western']
                for genre in genres_to_scrape:
                    page_url_key = f'page_url_film_{genre}'
                    start_page_key = f'start_page_film_{genre}'
                    max_page_key = f'max_page_number_film_{genre}'
                    if page_url_key in parser['Urls'] and max_page_key in parser['Urls']:
                        page_url = parser['Urls'][page_url_key]
                        start_page = int(parser['Urls'][start_page_key])
                        max_page = int(parser['Urls'][max_page_key])
                        scrape_page(parser, page_url, max_page,
                                    'action', start_page)
                    else:
                        pass
            elif command == 'all':
                try:
                    print("Executing film-all command...")
                    genres_to_scrape_film = ['action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique',
                                             'drame', 'epouvante-horreur', 'famille', 'fantastique', 'guerre', 'historique',
                                             'musical', 'policier', 'romance', 'science-fiction', 'thriller', 'western']
                    for genre in genres_to_scrape_film:
                        page_url_key_film = f'page_url_film_{genre}'
                        start_page_key_film = f'start_page_film_{genre}'
                        max_page_key_film = f'max_page_number_film_{genre}'
                        if page_url_key_film in parser['Urls'] and max_page_key_film in parser['Urls']:
                            page_url_film = parser['Urls'][page_url_key_film]
                            start_page_film = int(
                                parser['Urls'][start_page_key_film])
                            max_page_film = int(
                                parser['Urls'][max_page_key_film])
                            scrape_page(parser, page_url_film,
                                        max_page_film, 'action', start_page_film)
                        else:
                            pass
                    print("Executing serie-all command...")
                    genres_to_scrape_serie = ['meilleur', 'action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique',
                                              'drame', 'epouvante-horreur', 'espionnage', 'famille', 'fantastique', 'historique',
                                              'judiciaire', 'policier', 'romance', 'science-fiction', 'thriller']
                    for genre in genres_to_scrape_serie:
                        page_url_key_serie = f'page_url_serie_{genre}'
                        start_page_key_serie = f'start_page_serie_{genre}'
                        max_page_key_serie = f'max_page_number_serie_{genre}'
                        if page_url_key_serie in parser['Urls'] and max_page_key_serie in parser['Urls']:
                            page_url_serie = parser['Urls'][page_url_key_serie]
                            start_page_serie = int(
                                parser['Urls'][start_page_key_serie])
                            max_page_serie = int(
                                parser['Urls'][max_page_key_serie])
                            scrape_page(parser, page_url_serie,
                                        max_page_serie, 'serie', start_page_serie)
                        else:
                            pass
                    print("Executing tri command...")
                    with open('data.json', 'r', encoding='utf-8') as file:
                        data = json.load(file)
                    trier_series_films(data)
                    print("Executing clean command...")
                    clean_data()
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif command == 'film':
                if len(sys.argv) > 2:
                    genre_to_scrape = sys.argv[2].lower()
                    if genre_to_scrape in ['action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique',
                                           'drame', 'epouvante-horreur', 'famille', 'fantastique', 'guerre', 'historique',
                                           'musical', 'policier', 'romance', 'science-fiction', 'thriller', 'western']:
                        page_url = parser['Urls'][f'page_url_film_{
                            genre_to_scrape}']
                        start_page = int(
                            parser['Urls'][f'start_page_film_{genre_to_scrape}'])
                        max_page = int(
                            parser['Urls'][f'max_page_number_film_{genre_to_scrape}'])
                        scrape_page(parser, page_url, max_page,
                                    'action', start_page)
                    else:
                        print(f"Unknown genre. Use one of the following genres: {' '.join(
                            ['action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique', 'drame', 'epouvante-horreur', 'famille', 'fantastique', 'guerre', 'historique',              'musical', 'policier', 'romance', 'science-fiction', 'thriller', 'western'])}.")
                        return
                else:
                    print(f"Unknown genre. Use one of the following genres: {' '.join(
                        ['action', 'animation', 'aventure', 'biopic', 'comedie', 'comedie-dramatique', 'drame', 'epouvante-horreur', 'famille', 'fantastique', 'guerre', 'historique', 'musical',               'policier', 'romance', 'science-fiction', 'thriller', 'western'])}.")
                    return
            elif command == 'interface':
                afficher_interface()
                return
            elif command == 'help':
                print("List of commands:")
                print("- clean: Clean data.json and the Covers folder.")
                print(
                    "- clean-all: Clean data.json, the Covers folder and the Tri folder.")
                print("- serie [genre]: Scrape best series pages by genre.")
                print("- film [genre]: Scrape best film pages by genre.")
                print("- tri: Tri series and films.")
                print("- help: Show this help message.")
                print("- serie-all: Scrape all pages of best series.")
                print("- film-all: Scrape all pages of best films.")
                print("- all : Scrape all pages.")
                print("- everyserie : Scrape all pages of series.")
                print("- everyfilm : Scrape all pages of films.")
                print("- everyall : Scrape all pages of series and films.")
                print("- databasefilm : Send sorted film data to the database.")
                print("- databaseserie : Send sorted serie data to the database.")
                print("- databaseall : Send all sorted data to the database.")
                print("- interface : Start the interface.")
                print("-------------------------------------")
                print("List of genres:")
                print("- action: Scrape action pages.")
                print("- animation: Scrape animation pages.")
                print("- aventure: Scrape aventure pages.")
                print("- biopic: Scrape biopic pages.")
                print("- comedie: Scrape comedie pages.")
                print("- comedie-dramatique: Scrape comedie-dramatique pages.")
                print("- drame: Scrape drame pages.")
                print("- epouvante-horreur: Scrape epouvante-horreur pages.")
                print("- famille: Scrape famille pages.")
                print("- fantastique: Scrape fantastique pages.")
                print("- guerre: Scrape guerre pages.")
                print("- historique: Scrape historique pages.")
                print("- musical: Scrape musical pages.")
                print("- policier: Scrape policier pages.")
                print("- romance: Scrape romance pages.")
                print("- science-fiction: Scrape science-fiction pages.")
                print("- thriller: Scrape thriller pages.")
                print("- western: Scrape western pages.")
                return
            else:
                print(f"Unknown command: {command}.")
                return
    except Exception as e:
        pass
if __name__ == "__main__":
    main()
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'tri':
        data_file_path = 'data.json'
        try:
            with open(data_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            if not data['data']:
                print("Le fichier JSON est vide.")
            else:
                trier_series_films(data)
        except FileNotFoundError:
            print(f"Le fichier {data_file_path} n'a pas été trouvé.")
        except json.decoder.JSONDecodeError:
            print(f"Erreur dans le fichier JSON dans {
                  data_file_path}. Le fichier peut être vide ou corrompu.")
        except Exception as e:
            pass
