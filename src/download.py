import os
import json
import requests

from config import BASE_URL, CITIES, WEATHER_PATH

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


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


def parse_hourly(weather_data, city):
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
    return results


for i, (city, coords) in enumerate(CITIES.items()):

    lat = coords["lat"]
    lon = coords["lon"]

    # 1. Datos históricos (13 abril - ayer)
    url_archive = (
        f"{ARCHIVE_URL}"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&start_date=2026-04-13"
        f"&end_date=2026-04-26"
        f"&hourly=temperature_2m,precipitation,windspeed_10m,winddirection_10m"
        f"&timezone=auto"
    )

    archive_data = api_request(url_archive)
    results = parse_hourly(archive_data, city)

    # 2. Datos de previsión (hoy + 7 días)
    url_forecast = (
        f"{BASE_URL}"
        f"?latitude={lat}"
        f"&longitude={lon}"
        f"&forecast_days=7"
        f"&hourly=temperature_2m,precipitation,windspeed_10m,winddirection_10m"
        f"&timezone=auto"
    )

    forecast_data = api_request(url_forecast)
    results += parse_hourly(forecast_data, city)

    mode = "w" if i == 0 else "a"

    data_writing(WEATHER_PATH, results, mode)