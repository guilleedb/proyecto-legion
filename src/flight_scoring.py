def score_wind(speed_kmh):
    """Calcula la puntuación del viento (0-100)"""
    speed = float(speed_kmh)
    if speed <= 5: return 100
    elif speed <= 15: return 100 - (speed - 5) * 4      # 100→60
    elif speed <= 35: return max(0, 60 - (speed - 15) * 3)  # 60→0
    else: return 0

def score_precipitation(mm):
    """Calcula la puntuación de la lluvia (0-100)"""
    precip = float(mm)
    if precip == 0: return 100
    elif precip <= 1: return max(0, 100 - precip * 40)  # 100→60
    elif precip <= 5: return max(0, 60 - (precip - 1) * 15)  # 60→0
    else: return 0

def score_temperature(celsius):
    """Calcula la puntuación de la temperatura (0-100)"""
    temp = float(celsius)
    if 20 <= temp <= 25: return 100
    elif 15 <= temp < 20: return 50 + (temp - 15) * 10   # 50→100
    elif 25 < temp <= 33: return max(0, 100 - (temp - 25) * 8)  # 100→36
    elif 10 <= temp < 15: return max(0, 50 - (15 - temp) * 5)
    else: return max(0, 36 - (temp - 33) * 4)

def composite_score(wind, precip, temp):
    """Combina los scores con pesos"""
    return min(100.0, (wind * 0.40) + (precip * 0.30) + (temp * 0.30))

def score_to_rating(score):
    """
    Convierte el score 0-100 en el formato que app.py necesita:
    (Nota 0-10, Etiqueta, Color Hex)
    """
    nota = round(score / 10, 1)
    if score >= 80:
        return nota, "Excelente", "#22c55e"
    elif score >= 60:
        return nota, "Bueno", "#84cc16"
    elif score >= 40:
        return nota, "Regular", "#f59e0b"
    else:
        return nota, "Malo", "#ef4444"

def score_flight(origin_weather, dest_weather):
    """
    Función principal llamada por app.py
    """
    try:
        # Extraer y puntuar origen
        o_v = score_wind(origin_weather.get('wind_speed', 0))
        o_p = score_precipitation(origin_weather.get('precipitation', 0))
        o_t = score_temperature(origin_weather.get('temperature', 20))
        res_origin = composite_score(o_v, o_p, o_t)

        # Extraer y puntuar destino
        d_v = score_wind(dest_weather.get('wind_speed', 0))
        d_p = score_precipitation(dest_weather.get('precipitation', 0))
        d_t = score_temperature(dest_weather.get('temperature', 20))
        res_dest = composite_score(d_v, d_p, d_t)

        # La nota final es la peor de las dos (pesimismo de seguridad)
        final_score = min(res_origin, res_dest)

        nota, etiqueta, color = score_to_rating(final_score)

        return {
            "rating": nota,
            "label": etiqueta,
            "color": color
        }
    except Exception:
        return {
            "rating": 0.0,
            "label": "Error",
            "color": "#333333"
        }
