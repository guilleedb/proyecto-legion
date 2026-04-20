import requests
import streamlit as st

# Mapeo de nombres de tu web a códigos IATA
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
}

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
        'limit': 100 # Aumentamos el límite para tener más margen de filtrado
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        vuelos_encontrados = []
        horas_vistas = set() 
        
        # FILTRO DE AEROLÍNEAS: Solo las que operan rutas nacionales/europeas reales
        AEROLINEAS_REALES = ["Iberia", "Vueling", "Air Europa", "Ryanair", "Binter", "Canaryfly", "Volotea"]

        if "data" in data:
            for f in data["data"]:
                nombre_linea = f.get("airline", {}).get("name", "")
                
                # 1. Filtro de aerolínea (Elimina British, Miami Air, etc. en rutas nacionales)
                if not any(real in nombre_linea for real in AEROLINEAS_REALES):
                    continue

                # 2. Obtener hora programada
                sched_time = f.get("departure", {}).get("scheduled", "")
                if not sched_time:
                    continue
                
                # 3. Ajuste de hora (+2 para España) y extracción de minutos
                h_original = int(sched_time[11:13])
                min_original = int(sched_time[14:16])
                
                h_local = (h_original + 2) % 24
                hora_texto = f"{h_local:02d}:{min_original:02d}"

                # 4. Evitar duplicados exactos en la misma hora
                if hora_texto in horas_vistas:
                    continue
                
                vuelos_encontrados.append({
                    "linea": nombre_linea,
                    "vuelo": f.get("flight", {}).get("iata", "N/A"),
                    "hora_salida": hora_texto,
                    "hora_int": h_local,      # Guardamos como número para ordenar
                    "minuto_int": min_original, # Guardamos como número para ordenar
                    "estado": f.get("flight_status", "N/A")
                })
                
                horas_vistas.add(hora_texto)

        # --- ORDENACIÓN MATEMÁTICA FINAL ---
        # Ordenamos primero por hora y luego por minuto
        vuelos_encontrados.sort(key=lambda x: (x['hora_int'], x['minuto_int']))
        
        return vuelos_encontrados

    except Exception as e:
        st.error(f"Error en la API: {e}")
        return []