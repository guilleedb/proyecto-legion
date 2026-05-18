import requests
import streamlit as st

# diccionario para convertir el nombre bonito del aeropuerto a su codigo IATA
# tuvimos que buscar cada uno a mano, hay 33 en total
CIUDADES_IATA = {
    "Madrid Barajas": "MAD",
    "Barcelona El Prat": "BCN",
    "Palma de Mallorca": "PMI",
    "Málaga Costa del Sol": "AGP",
    "Alicante Elche": "ALC",
    "Gran Canaria": "LPA",
    "Tenerife Sur": "TFS",
    "Valencia": "VLC",
    "Sevilla": "SVQ",
    "Bilbao": "BIO",
    "Ibiza": "IBZ",
    "Lanzarote": "ACE",
    "Fuerteventura": "FUE",
    "Menorca": "MAH",
    "Santiago de Compostela": "SCQ",
    # Inglaterra
    "London Heathrow": "LHR",
    "London Gatwick": "LGW",
    "Manchester": "MAN",
    # Portugal
    "Lisboa": "LIS",
    "Oporto": "OPO",
    "Faro": "FAO",
    # Marruecos
    "Casablanca Mohammed V": "CMN",
    "Marrakech Menara": "RAK",
    "Tánger Ibn Battouta": "TNG",
    # Italia
    "Roma Fiumicino": "FCO",
    "Milán Malpensa": "MXP",
    "Nápoles": "NAP",
    # Francia
    "París Charles de Gaulle": "CDG",
    "París Orly": "ORY",
    "Marsella": "MRS",
    # Alemania
    "Frankfurt": "FRA",
    "Múnich": "MUC",
    "Berlín Brandenburg": "BER",
}

# cacheamos 5 minutos para no gastar llamadas a la api innecesariamente
@st.cache_data(ttl=300)
def buscar_programacion_comercial(origen_nombre, destino_nombre):
    dep_iata = CIUDADES_IATA.get(origen_nombre)
    arr_iata = CIUDADES_IATA.get(destino_nombre)

    api_key = "f38b504ca2a92c30016cfd342be26c70"
    url = "http://api.aviationstack.com/v1/flights"

    params = {
        'access_key': api_key,
        'dep_iata': dep_iata,
        'arr_iata': arr_iata,
        'limit': 100
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        vuelos_encontrados = []
        horas_vistas = set()

        # solo aereolineas que operan de verdad en europa, filtramos las raras
        AEROLINEAS_REALES = [
            "Iberia", "Vueling", "Air Europa", "Ryanair", "Binter", "Canaryfly", "Volotea",
            "British Airways", "easyJet", "TAP", "Royal Air Maroc", "Alitalia", "ITA Airways",
            "Air France", "Transavia", "Lufthansa", "Eurowings", "Wizz Air",
        ]

        if "data" in data:
            for f in data["data"]:
                nombre_linea = f.get("airline", {}).get("name", "")

                # descartamos aerolineas que no nos interesan
                if not any(real in nombre_linea for real in AEROLINEAS_REALES):
                    continue

                sched_time = f.get("departure", {}).get("scheduled", "")
                if not sched_time:
                    continue

                # la api devuelve hora UTC, sumamos 2 para convertir a hora española
                h_original = int(sched_time[11:13])
                min_original = int(sched_time[14:16])
                h_local = (h_original + 2) % 24
                hora_texto = f"{h_local:02d}:{min_original:02d}"

                # si ya tenemos un vuelo a esa hora exacta lo saltamos
                if hora_texto in horas_vistas:
                    continue

                vuelos_encontrados.append({
                    "linea": nombre_linea,
                    "vuelo": f.get("flight", {}).get("iata", "N/A"),
                    "hora_salida": hora_texto,
                    "hora_int": h_local,
                    "minuto_int": min_original,
                    "estado": f.get("flight_status", "N/A")
                })

                horas_vistas.add(hora_texto)

        # ordenamos por hora y minuto para que salgan en orden cronologico
        vuelos_encontrados.sort(key=lambda x: (x['hora_int'], x['minuto_int']))

        return vuelos_encontrados

    except Exception as e:
        st.error(f"Error en la API: {e}")
        return []
