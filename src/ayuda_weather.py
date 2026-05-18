import pandas as pd
import os

# funciones de ayuda para leer y consultar el csv del clima
# el csv tiene una fila por ciudad y por hora, hay que filtrar bien

def load_weather_csv(path=None):
    if path is None:
        # subimos dos carpetas desde src/ para llegar a data/clean/
        path = os.path.join(os.path.dirname(__file__), "..", "data", "clean", "weather_data.csv")
    df = pd.read_csv(path)
    # convertimos la columna datetime a tipo fecha de verdad para poder filtrar
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["date"] = df["datetime"].dt.date
    df["hour"] = df["datetime"].dt.hour
    return df


def get_weather_at(df, city, date, hour):
    # buscamos la fila exacta: ciudad + dia + hora
    mask = (df["city"] == city) & (df["date"] == date) & (df["hour"] == hour)
    row = df[mask]
    if row.empty:
        return None  # no hay datos para esa combinacion
    row = row.iloc[0]
    return {
        "city": row["city"],
        "temperature": row["temperature"],
        "precipitation": row["precipitation"],
        "wind_speed": row["wind_speed"],
        "wind_direction": row["wind_direction"],
    }


def get_available_dates(df):
    # devuelve la lista de fechas que tenemos en el csv, ordenadas
    return sorted(df["date"].unique())


def degrees_to_compass(degrees):
    # convierte grados (0-360) a punto cardinal, dividimos en 8 sectores de 45 grados
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(degrees / 45) % 8
    return directions[index]
