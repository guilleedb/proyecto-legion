# este archivo calcula la "nota" de cada vuelo segun el clima
# basicamente convertimos datos meteorologicos en numeros del 0 al 100
# y luego los combinamos con pesos para sacar una puntuacion final

def score_wind(speed_kmh):
    speed = float(speed_kmh)
    # si hay poco viento perfecto, si hay mucho viento mal
    if speed <= 5: return 100
    elif speed <= 15: return 100 - (speed - 5) * 4
    elif speed <= 35: return max(0, 60 - (speed - 15) * 3)
    else: return 0

def score_precipitation(mm):
    precip = float(mm)
    # si no llueve perfecto, cualquier lluvia ya baja bastante la nota
    if precip == 0: return 100
    elif precip <= 1: return max(0, 100 - precip * 40)
    elif precip <= 5: return max(0, 60 - (precip - 1) * 15)
    else: return 0

def score_temperature(celsius):
    temp = float(celsius)
    # entre 20 y 25 grados es la zona perfecta para volar comodamente
    if 20 <= temp <= 25: return 100
    elif 15 <= temp < 20: return 50 + (temp - 15) * 10
    elif 25 < temp <= 33: return max(0, 100 - (temp - 25) * 8)
    elif 10 <= temp < 15: return max(0, 50 - (15 - temp) * 5)
    else: return max(0, 36 - (temp - 33) * 4)

def composite_score(wind, precip, temp):
    # media ponderada de los tres factores, viento pesa mas porque afecta mas al vuelo
    return min(100.0, (wind * 0.40) + (precip * 0.30) + (temp * 0.30))

def score_to_rating(score):
    # convertimos el score (0-100) a nota sobre 10 con su etiqueta y color
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
    # funcion principal: recibe el clima de origen y destino y devuelve la nota final
    try:
        o_v = score_wind(origin_weather.get('wind_speed', 0))
        o_p = score_precipitation(origin_weather.get('precipitation', 0))
        o_t = score_temperature(origin_weather.get('temperature', 20))
        res_origin = composite_score(o_v, o_p, o_t)

        d_v = score_wind(dest_weather.get('wind_speed', 0))
        d_p = score_precipitation(dest_weather.get('precipitation', 0))
        d_t = score_temperature(dest_weather.get('temperature', 20))
        res_dest = composite_score(d_v, d_p, d_t)

        # nos quedamos con el peor de los dos aeropuertos, si uno esta mal el vuelo esta mal
        final_score = min(res_origin, res_dest)

        nota, etiqueta, color = score_to_rating(final_score)

        return {
            "rating": nota,
            "label": etiqueta,
            "color": color
        }
    except Exception:
        # si algo falla devolvemos un error en lugar de petarlo todo
        return {
            "rating": 0.0,
            "label": "Error",
            "color": "#333333"
        }
