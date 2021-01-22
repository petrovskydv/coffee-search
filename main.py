import json
import os

import folium
import requests
from dotenv import load_dotenv
from flask import Flask
from geopy import distance


def hello_world():
    with open('map.html', encoding='utf-8') as file:
        return file.read()


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def save_map_file(location_coordinates, nearest_coffee_shops):
    map_file = folium.Map(location=location_coordinates[::-1], zoom_start=15)
    for coffee_shop in nearest_coffee_shops:
        folium.Marker(
            [coffee_shop['longitude'], coffee_shop['latitude']],
            popup=f"<i>{coffee_shop['title']}</i>",
            tooltip=coffee_shop['title']
        ).add_to(map_file)
    map_file.save("map.html")


def fetch_nearest_coffee_shops(location_coordinates):
    with open("coffee.json", "r", encoding='CP1251') as my_file:
        file_contents = my_file.read()
        coffee_shops = json.loads(file_contents)
    coffee_shops_distances = []
    for coffee_shop in coffee_shops:
        coffee_shop_coordinates = coffee_shop['geoData']['coordinates']
        coffee_shops_distances.append(
            {
                'title': coffee_shop['Name'],
                'distance': distance.distance(
                    coffee_shop_coordinates[::-1],
                    (location_coordinates[::-1])
                ).km,
                'latitude': coffee_shop_coordinates[0],
                'longitude': coffee_shop_coordinates[1]
            }
        )
    return sorted(coffee_shops_distances, key=lambda x: x['distance'])[:5]


def main():
    load_dotenv()
    apikey = os.getenv('YANDEX_GEOCODER_TOKEN')
    location = input('Где вы находитесь?: ')
    location_coordinates = fetch_coordinates(apikey, location)

    nearest_coffee_shops = fetch_nearest_coffee_shops(location_coordinates)

    save_map_file(location_coordinates, nearest_coffee_shops)

    app = Flask(__name__)
    app.add_url_rule('/', 'hello', hello_world)
    app.run()


if __name__ == '__main__':
    main()
