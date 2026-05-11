BASE_URL = "https://api.open-meteo.com/v1/forecast"

CITIES = {
  "Madrid Barajas": {"lat": 40.4722, "lon": -3.5608},
  "Barcelona El Prat": {"lat": 41.2974, "lon": 2.0833},
  "Palma de Mallorca": {"lat": 39.5517, "lon": 2.7388},
  "Málaga Costa del Sol": {"lat": 36.6749, "lon": -4.4991},
  "Alicante Elche": {"lat": 38.2822, "lon": -0.5582},
  "Gran Canaria": {"lat": 27.9319, "lon": -15.3866},
  "Tenerife Sur": {"lat": 28.0445, "lon": -16.5725},
  "Valencia": {"lat": 39.4893, "lon": -0.4816},
  "Sevilla": {"lat": 37.4180, "lon": -5.8931},
  "Bilbao": {"lat": 43.3011, "lon": -2.9106},
  "Ibiza": {"lat": 38.8729, "lon": 1.3731},
  "Lanzarote": {"lat": 28.9455, "lon": -13.6052},
  "Fuerteventura": {"lat": 28.4527, "lon": -13.8638},
  "Menorca": {"lat": 39.8626, "lon": 4.2186},
  "Santiago de Compostela": {"lat": 42.8963, "lon": -8.4151},

  # Inglaterra
  "London Heathrow": {"lat": 51.4700, "lon": -0.4543},
  "London Gatwick": {"lat": 51.1537, "lon": -0.1821},
  "Manchester": {"lat": 53.3537, "lon": -2.2750},

  # Portugal
  "Lisboa": {"lat": 38.7742, "lon": -9.1342},
  "Oporto": {"lat": 41.2481, "lon": -8.6814},
  "Faro": {"lat": 37.0144, "lon": -7.9659},

  # Marruecos
  "Casablanca Mohammed V": {"lat": 33.3675, "lon": -7.5898},
  "Marrakech Menara": {"lat": 31.6069, "lon": -8.0363},
  "Tánger Ibn Battouta": {"lat": 35.7269, "lon": -5.9169},

  # Italia
  "Roma Fiumicino": {"lat": 41.8003, "lon": 12.2389},
  "Milán Malpensa": {"lat": 45.6306, "lon": 8.7281},
  "Nápoles": {"lat": 40.8860, "lon": 14.2908},

  # Francia
  "París Charles de Gaulle": {"lat": 49.0097, "lon": 2.5479},
  "París Orly": {"lat": 48.7233, "lon": 2.3794},
  "Marsella": {"lat": 43.4393, "lon": 5.2214},

  # Alemania
  "Frankfurt": {"lat": 50.0379, "lon": 8.5622},
  "Múnich": {"lat": 48.3538, "lon": 11.7861},
  "Berlín Brandenburg": {"lat": 52.3667, "lon": 13.5033},
}

WEATHER_PATH = "data/raw/weather_data.json"