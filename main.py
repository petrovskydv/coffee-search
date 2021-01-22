import json
import requests
from geopy import distance
from pprint import pprint
import folium
from flask import Flask


def hello_world():
    with open('index.html') as file:
        return file.read()


def fetch_coordinates(apikey, place):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json(
    )['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


with open("coffee.json", "r", encoding='CP1251') as my_file:
    file_contents = my_file.read()
    coffee_shops = json.loads(file_contents)

location = input('Где вы находитесь?: ')
# location = 'Красная площадь'
apikey = '087c1490-c47b-4b04-a48b-23b65d591cc6'  # ваш ключ

coords = fetch_coordinates(apikey, location)
print('Ваши координтаты:', coords)

coffee_shops1 = []
for coffee_shop in coffee_shops:
    coffee_shop_coords = coffee_shop['geoData']['coordinates']
    coffee_shops1.append({
        'title':
        coffee_shop['Name'],
        'distance':
        distance.distance(coffee_shop_coords[::-1], (coords[::-1])).km,
        'latitude':
        coffee_shop_coords[0],
        'longitude':
        coffee_shop_coords[1]
    })

nearest_coffe_shops = sorted(coffee_shops1, key=lambda x: x['distance'])[:5]    

pprint(nearest_coffe_shops)

tooltip = "Click me!"

m = folium.Map(location=coords[::-1], zoom_start=12)

for coffee_shop in nearest_coffe_shops:
    folium.Marker(
        [coffee_shop['longitude'], coffee_shop['latitude']], popup=f"<i>{coffee_shop['title']}</i>", tooltip=coffee_shop['title']
    ).add_to(m)

m.save("index.html")

app = Flask(__name__)
app.add_url_rule('/', 'hello', hello_world)
app.run('0.0.0.0')
