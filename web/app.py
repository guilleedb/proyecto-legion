import streamlit as st
import pandas as pd
import sys
import os
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from ayuda_weather import load_weather_csv, get_weather_at, get_available_dates, degrees_to_compass
from flight_scoring import score_flight, score_to_rating

st.set_page_config(page_title="Legion Flight", layout="wide")

# Cargar datos meteorológicos
@st.cache_data
def load_data():
    return load_weather_csv()

df_weather = load_data()
available_dates = get_available_dates(df_weather)

# Ocultar header por defecto de Streamlit y añadir navbar custom
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 9999;
        background-color: #0e1117;
        border-bottom: 1px solid #2e2e2e;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 2rem;
        box-sizing: border-box;
    }
    .navbar-logo {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
    }
    .navbar-logo span { font-size: 1.5rem; }
    .navbar-links {
        display: flex;
        gap: 2.5rem;
        align-items: center;
    }
    .navbar-links a {
        color: #c0c0c0;
        text-decoration: none;
        font-size: 0.95rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        transition: color 0.2s;
    }
    .navbar-links a:hover { color: #ffffff; }
    .navbar-spacer { width: 150px; }
    .block-container { padding-top: 4.5rem !important; }

    .weather-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #2e2e2e;
    }
    .rating-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        color: white;
    }
</style>

<div class="navbar">
    <div class="navbar-logo">
        <span>✈️</span> Legion Flight
    </div>
    <div class="navbar-links">
        <a href="#buscar-vuelo">🔍 Buscar vuelo</a>
        <a href="#como-funciona">⚙️ Cómo funciona</a>
        <a href="#contacto">📩 Contacto</a>
    </div>
    <div class="navbar-spacer"></div>
</div>
""", unsafe_allow_html=True)

# HEADER
st.markdown("### Descubre cómo será tu vuelo antes de despegar")
st.markdown("*Convierte la incertidumbre en información: conoce las condiciones de tu vuelo y destino antes de embarcar.*")

st.markdown("---")

# Lista de aeropuertos disponibles
AEROPUERTOS = [
    "Madrid Barajas",
    "Barcelona El Prat",
    "Palma de Mallorca",
    "Málaga Costa del Sol",
    "Alicante Elche",
    "Gran Canaria",
    "Tenerife Sur",
    "Valencia",
    "Sevilla",
    "Bilbao",
    "Ibiza",
    "Lanzarote",
    "Fuerteventura",
    "Menorca",
    "Santiago de Compostela",
]

# BUSCADOR
st.markdown('<div id="buscar-vuelo"></div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    origen = st.selectbox("Aeropuerto salida", AEROPUERTOS, index=0)

with col2:
    destino = st.selectbox("Aeropuerto llegada", AEROPUERTOS, index=1)

with col3:
    fecha = st.date_input(
        "Fecha salida",
        value=available_dates[0],
        min_value=available_dates[0],
        max_value=available_dates[-1],
    )

with col4:
    buscar = st.button("🔍 Buscar vuelos")

st.markdown("---")

# RESULTADOS
VUELOS = [
    {"salida": 8, "llegada": 10, "salida_str": "08:00", "llegada_str": "10:00", "duracion": "2h", "franja": "Mañana"},
    {"salida": 12, "llegada": 14, "salida_str": "12:30", "llegada_str": "14:30", "duracion": "2h", "franja": "Mediodía"},
    {"salida": 18, "llegada": 20, "salida_str": "18:45", "llegada_str": "20:45", "duracion": "2h", "franja": "Tarde"},
]

if buscar:
    if origen == destino:
        st.error("El aeropuerto de origen y destino no pueden ser el mismo.")
    else:
        st.subheader("✈️ Condiciones de vuelo")

        # Tarjetas meteorológicas resumen del día (hora punta: mediodía)
        weather_origin = get_weather_at(df_weather, origen, fecha, 12)
        weather_dest = get_weather_at(df_weather, destino, fecha, 12)

        if weather_origin is None or weather_dest is None:
            st.warning("No hay datos meteorológicos disponibles para la fecha seleccionada.")
        else:
            col_o, col_d = st.columns(2)

            for col, weather, label in [(col_o, weather_origin, f"🛫 {origen}"), (col_d, weather_dest, f"🛬 {destino}")]:
                with col:
                    st.markdown(f"**{label}**")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("🌡️ Temperatura", f"{weather['temperature']}°C")
                    m2.metric("💨 Viento", f"{weather['wind_speed']} km/h", degrees_to_compass(weather['wind_direction']))
                    m3.metric("🌧️ Precipitación", f"{weather['precipitation']} mm")

            st.markdown("---")

            # Tabla de vuelos con condiciones
            st.subheader("🕐 Vuelos disponibles")

            for vuelo in VUELOS:
                w_orig = get_weather_at(df_weather, origen, fecha, vuelo["salida"])
                w_dest = get_weather_at(df_weather, destino, fecha, vuelo["llegada"])

                if w_orig is None or w_dest is None:
                    continue

                result = score_flight(w_orig, w_dest)

                col_h, col_info, col_score = st.columns([1, 2, 1])

                with col_h:
                    st.markdown(f"**{vuelo['franja']}**")
                    st.write(f"{vuelo['salida_str']} → {vuelo['llegada_str']} ({vuelo['duracion']})")

                with col_info:
                    st.write(f"🛫 {origen}: {w_orig['temperature']}°C, 💨 {w_orig['wind_speed']} km/h, 🌧️ {w_orig['precipitation']} mm")
                    st.write(f"🛬 {destino}: {w_dest['temperature']}°C, 💨 {w_dest['wind_speed']} km/h, 🌧️ {w_dest['precipitation']} mm")

                with col_score:
                    st.markdown(
                        f'<span class="rating-badge" style="background-color:{result["color"]}">'
                        f'{result["rating"]} ({result["flight_score"]})</span>',
                        unsafe_allow_html=True,
                    )

                st.markdown("---")

# CÓMO FUNCIONA
st.markdown('<div id="como-funciona"></div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown("## ⚙️ Cómo funciona")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown("### 1. Busca")
    st.write("Selecciona tu aeropuerto de origen, destino y fecha de vuelo.")
with col_b:
    st.markdown("### 2. Analiza")
    st.write("Consulta las condiciones meteorológicas reales en origen y destino.")
with col_c:
    st.markdown("### 3. Decide")
    st.write("Elige el horario con mejores condiciones para volar.")

# CONTACTO
st.markdown('<div id="contacto"></div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown("## 📩 Contacto")
st.write("¿Tienes dudas? Escríbenos a **contacto@legionflight.com**")

# FAQ
st.markdown("---")
st.markdown("## ❓ FAQ")

st.write("""
- ¿De dónde salen los datos? → Del servicio meteorológico Open-Meteo
- ¿Qué variables se analizan? → Temperatura, viento y precipitación
- ¿Puedo ver previsión a más de 7 días? → De momento cubrimos los próximos 7 días
""")
