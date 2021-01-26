import json
import os

import folium
import requests
from dotenv import load_dotenv
from flask import Flask
from geopy import distance

NEAREST_COFFEE_SHOPS_AMOUNT = 5


def open_map_page():
    with open('map.html', encoding='utf-8') as file:
        return file.read()


def fetch_coordinates(apikey, place):
    base_url = 'https://geocode-maps.yandex.ru/1.x'
    params = {'geocode': place, 'apikey': apikey, 'format': 'json'}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def create_markers(location_latitude, location_longitude, nearest_coffee_shops, map_file):
    folium.Marker(
        [location_latitude, location_longitude],
        popup=f'<i>I\'m here</i>',
        tooltip='I\'m here',
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(map_file)

    for coffee_shop in nearest_coffee_shops:
        folium.Marker(
            [coffee_shop['latitude'], coffee_shop['longitude']],
            popup=f'<i>{coffee_shop["title"]}</i>',
            tooltip=coffee_shop['title']
        ).add_to(map_file)


def fetch_nearest_coffee_shops(coffee_shops, location_coordinates):
    coffee_shops_distances = []
    for coffee_shop in coffee_shops:
        coffee_shop_longitude, coffee_shop_latitude = coffee_shop['geoData']['coordinates']
        coffee_shops_distances.append(
            {
                'title': coffee_shop['Name'],
                'distance': distance.distance(
                    (coffee_shop_latitude, coffee_shop_longitude),
                    location_coordinates
                ).km,
                'latitude': coffee_shop_latitude,
                'longitude': coffee_shop_longitude
            }
        )
    return sorted(coffee_shops_distances, key=lambda x: x['distance'])[:NEAREST_COFFEE_SHOPS_AMOUNT]


def fetch_coffee_shops(file_path):
    with open(file_path, 'r', encoding='CP1251') as my_file:
        file_contents = my_file.read()
        coffee_shops = json.loads(file_contents)
    return coffee_shops


def main():
    load_dotenv()
    apikey = os.getenv('YANDEX_GEOCODER_TOKEN')
    location = input('Где вы находитесь?: ')
    location_longitude, location_latitude = fetch_coordinates(apikey, location)

    coffee_shops = fetch_coffee_shops('coffee.json')
    nearest_coffee_shops = fetch_nearest_coffee_shops(coffee_shops, (location_latitude, location_longitude))

    map_file = folium.Map(location=(location_latitude, location_longitude), zoom_start=15)
    create_markers(location_latitude, location_longitude, nearest_coffee_shops, map_file)
    map_file.save('map.html')

    app = Flask(__name__)
    app.add_url_rule('/', 'Nearest coffees', open_map_page)
    app.run()


if __name__ == '__main__':
    main()
