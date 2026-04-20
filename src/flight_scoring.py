def score_wind(speed_kmh):
    """Calcula la puntuación del viento (0-100)"""
    speed = float(speed_kmh)
    if speed <= 15: return 100
    elif speed <= 45: return max(0, 100 - (speed - 15) * 3.33)
    else: return 0

def score_precipitation(mm):
    """Calcula la puntuación de la lluvia (0-100)"""
    precip = float(mm)
    if precip == 0: return 100
    elif precip <= 2: return max(0, 100 - (precip * 40))
    else: return 0

def score_temperature(celsius):
    """Calcula la puntuación de la temperatura (0-100)"""
    temp = float(celsius)
    if 15 <= temp <= 28: return 100
    elif temp < 15: return max(50, 100 - (15 - temp) * 5)
    else: return max(50, 100 - (temp - 28) * 5)

def composite_score(wind, precip, temp):
    """Combina los scores con pesos"""
    return (wind * 0.45) + (precip * 0.40) + (temp * 0.15)

def score_to_rating(score):
    """
    Convierte el score 0-100 en el formato que app.py necesita:
    (Nota 0-10, Etiqueta, Color Hex)
    """
    if score >= 85:
        return 9.5, "Excelente", "#28a745"  # Verde
    elif score >= 70:
        return 7.5, "Bueno", "#b8d434"      # Lima/Verde claro
    elif score >= 55:
        return 5.5, "Regular", "#ffc107"    # Amarillo/Naranja
    else:
        return 3.0, "Malo", "#dc3545"       # Rojo

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
        
        # Obtener el pack de datos final
        nota, etiqueta, color = score_to_rating(final_score)

        return {
            "rating": nota,
            "label": etiqueta,
            "color": color
        }
    except Exception as e:
        # Si algo falla catastróficamente, devolvemos un error visual
        return {
            "rating": 0.0,
            "label": "Error",
            "color": "#333333"
        }