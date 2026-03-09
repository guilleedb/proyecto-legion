import os
import json
import requests
from datetime import datetime

from config import BASE_URL, CITIES, WEATHER_PATH


def api_request(url):

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Error API: {response.status_code}")

    return response.json()


def data_writing(file_path, data, mode="w"):

    os.makedirs("data/raw", exist_ok=True)

    with open(file_path, mode, encoding="utf-8") as f:
        for element in data:
            f.write(json.dumps(element) + "\n")

    print(f"Se guardaron {len(data)} registros en {file_path}")


today = datetime.today().strftime("%Y-%m-%d")
start_date = f"{datetime.today().year}-01-01"


for i, (city, coords) in enumerate(CITIES.items()):

    lat = coords["lat"]
    lon = coords["lon"]

    url_weather = (
        f"{BASE_URL}"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&start_date={start_date}"
        f"&end_date={today}"
        f"&hourly=temperature_2m,precipitation,windspeed_10m,winddirection_10m"
        f"&timezone=auto"
    )

    weather_data = api_request(url_weather)

    results = []

    for j, time in enumerate(weather_data["hourly"]["time"]):

        record = {
            "city": city,
            "datetime": time,
            "temperature": weather_data["hourly"]["temperature_2m"][j],
            "precipitation": weather_data["hourly"]["precipitation"][j],
            "wind_speed": weather_data["hourly"]["windspeed_10m"][j],
            "wind_direction": weather_data["hourly"]["winddirection_10m"][j]
        }

        results.append(record)

    mode = "w" if i == 0 else "a"

    data_writing(WEATHER_PATH, results, mode)