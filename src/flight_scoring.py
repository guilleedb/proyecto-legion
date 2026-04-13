def score_wind(speed_kmh):
    if speed_kmh <= 15:
        return 100
    elif speed_kmh <= 25:
        return 100 - (speed_kmh - 15) / 10 * 25  # 100 -> 75
    elif speed_kmh <= 35:
        return 75 - (speed_kmh - 25) / 10 * 25   # 75 -> 50
    elif speed_kmh <= 45:
        return 50 - (speed_kmh - 35) / 10 * 25   # 50 -> 25
    else:
        return max(0, 25 - (speed_kmh - 45) / 10 * 25)


def score_precipitation(mm):
    if mm == 0:
        return 100
    elif mm <= 0.5:
        return 100 - mm / 0.5 * 20  # 100 -> 80
    elif mm <= 2.0:
        return 80 - (mm - 0.5) / 1.5 * 30  # 80 -> 50
    elif mm <= 5.0:
        return 50 - (mm - 2.0) / 3.0 * 25  # 50 -> 25
    else:
        return max(0, 25 - (mm - 5.0) / 2.0 * 25)


def score_temperature(celsius):
    if celsius < 2:
        return 50
    elif celsius < 10:
        return 75 + (celsius - 2) / 8 * 25  # 75 -> 100
    elif celsius <= 30:
        return 100
    else:
        return max(80, 100 - (celsius - 30) / 10 * 20)


def composite_score(wind, precip, temp):
    return round(0.45 * wind + 0.40 * precip + 0.15 * temp)


def score_to_rating(score):
    if score >= 90:
        return "Excelente", "#28a745"      # verde
    elif score >= 80:
        return "Muy bueno", "#b8d434"      # amarillo verdoso
    elif score >= 70:
        return "Bueno", "#ffc107"          # amarillo
    elif score >= 60:
        return "Moderado", "#ffaa00"       # amarillo oscuro
    elif score >= 50:
        return "Regular", "#fd7e14"        # naranja
    else:
        return "Malo", "#dc3545"           # rojo



def score_flight(origin_weather, dest_weather):
    o_wind = score_wind(origin_weather["wind_speed"])
    o_precip = score_precipitation(origin_weather["precipitation"])
    o_temp = score_temperature(origin_weather["temperature"])
    o_score = composite_score(o_wind, o_precip, o_temp)

    d_wind = score_wind(dest_weather["wind_speed"])
    d_precip = score_precipitation(dest_weather["precipitation"])
    d_temp = score_temperature(dest_weather["temperature"])
    d_score = composite_score(d_wind, d_precip, d_temp)

    flight_score = min(o_score, d_score)
    rating, color = score_to_rating(flight_score)

    return {
        "origin_score": o_score,
        "dest_score": d_score,
        "flight_score": flight_score,
        "rating": rating,
        "color": color,
    }
