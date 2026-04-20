def score_wind(speed_kmh):
    speed_kmh = float(speed_kmh)
    if speed_kmh <= 15: return 100
    elif speed_kmh <= 25: return 100 - (speed_kmh - 15) / 10 * 25
    elif speed_kmh <= 35: return 75 - (speed_kmh - 25) / 10 * 25
    elif speed_kmh <= 45: return 50 - (speed_kmh - 35) / 10 * 25
    else: return max(0, 25 - (speed_kmh - 45) / 10 * 25)

def score_precipitation(mm):
    mm = float(mm)
    if mm == 0: return 100
    elif mm <= 0.5: return 100 - mm / 0.5 * 20
    elif mm <= 2.0: return 80 - (mm - 0.5) / 1.5 * 30
    elif mm <= 5.0: return 50 - (mm - 2.0) / 3.0 * 25
    else: return max(0, 25 - (mm - 5.0) / 2.0 * 25)

def score_temperature(celsius):
    celsius = float(celsius)
    if celsius < 2: return 50
    elif celsius < 10: return 75 + (celsius - 2) / 8 * 25
    elif celsius <= 30: return 100
    else: return max(80, 100 - (celsius - 30) / 10 * 20)

def composite_score(wind, precip, temp):
    return round(0.45 * wind + 0.40 * precip + 0.15 * temp)

def score_to_rating(score):
    # Devolvemos: (Nota sobre 10, Etiqueta, Color)
    if score >= 90: return 10.0, "Excelente", "#28a745"
    elif score >= 80: return 8.5, "Muy Bueno", "#b8d434"
    elif score >= 70: return 7.5, "Bueno", "#ffc107"
    elif score >= 60: return 6.0, "Moderado", "#ffaa00"
    elif score >= 50: return 5.0, "Regular", "#fd7e14"
    else: return 3.0, "Malo", "#dc3545"

def score_flight(origin_weather, dest_weather):
    try:
        # Extraemos datos con .get para evitar errores si falta el guion bajo
        o_wind = score_wind(origin_weather.get("wind_speed", origin_weather.get("windspeed", 0)))
        o_precip = score_precipitation(origin_weather.get("precipitation", origin_weather.get("precip", 0)))
        o_temp = score_temperature(origin_weather.get("temperature", origin_weather.get("temp", 20)))
        
        d_wind = score_wind(dest_weather.get("wind_speed", dest_weather.get("windspeed", 0)))
        d_precip = score_precipitation(dest_weather.get("precipitation", dest_weather.get("precip", 0)))
        d_temp = score_temperature(dest_weather.get("temperature", dest_weather.get("temp", 20)))
        
        f_score = min(composite_score(o_wind, o_precip, o_temp), composite_score(d_wind, d_precip, d_temp))
        
        nota_num, etiqueta, color = score_to_rating(f_score)
        return {"rating": nota_num, "label": etiqueta, "color": color}
    except:
        return {"rating": 0.0, "label": "Error", "color": "#dc3545"}