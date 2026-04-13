import pandas as pd
import os


def load_weather_csv(path=None):
    if path is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "clean", "weather_data.csv")
    df = pd.read_csv(path)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["date"] = df["datetime"].dt.date
    df["hour"] = df["datetime"].dt.hour
    return df


def get_weather_at(df, city, date, hour):
    mask = (df["city"] == city) & (df["date"] == date) & (df["hour"] == hour)
    row = df[mask]
    if row.empty:
        return None
    row = row.iloc[0]
    return {
        "city": row["city"],
        "temperature": row["temperature"],
        "precipitation": row["precipitation"],
        "wind_speed": row["wind_speed"],
        "wind_direction": row["wind_direction"],
    }


def get_available_dates(df):
    return sorted(df["date"].unique())


def degrees_to_compass(degrees):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8
    return directions[index]
