import streamlit as st
import pandas as pd
import sys
import os
import datetime
import base64

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from ayuda_weather import load_weather_csv, get_weather_at, get_available_dates, degrees_to_compass
from flight_scoring import score_flight, score_to_rating


def get_hero_image_base64():
    img_path = os.path.join(os.path.dirname(__file__), "assets", "hero.jpg")
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.set_page_config(page_title="Legion Flight", layout="wide")

ruta_imagen = os.path.join(os.path.dirname(__file__), "avion.jpeg")
st.image(ruta_imagen, width=500)

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

    .rating-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        color: white;
    }

    /* Hero section */
    .hero {
        position: relative;
        width: calc(100% + 6rem);
        margin-left: -3rem;
        margin-top: -1rem;
        height: 520px;
        overflow: hidden;
        border-radius: 0 0 16px 16px;
    }
    .hero img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .hero-overlay {
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(to bottom, rgba(14,17,23,0.3) 0%, rgba(14,17,23,0.85) 100%);
    }
    .hero-content {
        position: absolute;
        bottom: 2.5rem;
        left: 3rem;
        z-index: 2;
    }
    .hero-content h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0 0 0.5rem 0;
        line-height: 1.2;
    }
    .hero-content p {
        font-size: 1.05rem;
        color: #c0c0c0;
        margin: 0 0 1.5rem 0;
        max-width: 550px;
        font-style: italic;
    }
    .hero-buttons {
        display: flex;
        gap: 1rem;
    }
    .hero-buttons a {
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }
    .btn-primary {
        background-color: #2563eb;
        color: white;
    }
    .btn-primary:hover { background-color: #1d4ed8; }
    .btn-secondary {
        background-color: rgba(255,255,255,0.12);
        color: #e0e0e0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .btn-secondary:hover { background-color: rgba(255,255,255,0.2); }

    /* Tarjetas meteorológicas sobre el hero */
    .hero-weather {
        position: absolute;
        top: 1.5rem;
        left: 3rem;
        display: flex;
        gap: 1rem;
        z-index: 2;
    }
    .hero-weather-right {
        position: absolute;
        top: 1.5rem;
        right: 3rem;
        z-index: 2;
    }
    .hero-weather-bottom-right {
        position: absolute;
        bottom: 2.5rem;
        right: 3rem;
        z-index: 2;
    }
    .hw-card {
        background: rgba(14,17,23,0.65);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        color: white;
        min-width: 130px;
    }
    .hw-card .hw-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #a0a0a0;
        margin-bottom: 0.3rem;
    }
    .hw-card .hw-value {
        font-size: 1.2rem;
        font-weight: 700;
    }
    .hw-card .hw-sub {
        font-size: 0.8rem;
        color: #b0b0b0;
        margin-top: 0.2rem;
    }
    .hero-turbulence {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 2;
        text-align: center;
    }
    .hero-turbulence .hw-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #a0a0a0;
    }
    .hero-turbulence .hw-value {
        font-size: 1.1rem;
        font-weight: 600;
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

# HERO SECTION
hero_b64 = get_hero_image_base64()

st.markdown(f"""
<div class="hero">
    <img src="data:image/jpeg;base64,{hero_b64}" alt="Avión en vuelo">
    <div class="hero-overlay"></div>

    <!-- Tarjetas meteorológicas decorativas -->
    <div class="hero-weather">
        <div class="hw-card">
            <div class="hw-label">Viento</div>
            <div class="hw-value">18 kt</div>
            <div class="hw-sub">Rachas 26 kt</div>
        </div>
        <div class="hw-card">
            <div class="hw-label">Temperatura</div>
            <div class="hw-value">-12 °C</div>
            <div class="hw-sub">Punto de rocío -18 °C</div>
        </div>
    </div>

    <div class="hero-weather-right">
        <div class="hw-card">
            <div class="hw-label">Cielo</div>
            <div class="hw-value">Nubes dispersas</div>
            <div class="hw-sub">8,500 ft</div>
        </div>
    </div>

    <div class="hero-turbulence">
        <div class="hw-label">Turbulencia</div>
        <div class="hw-value">Moderada</div>
    </div>

    <div class="hero-weather-bottom-right">
        <div class="hw-card">
            <div class="hw-label">Visibilidad</div>
            <div class="hw-value">10 km</div>
        </div>
    </div>

    <!-- Texto principal -->
    <div class="hero-content">
        <h1>Descubre cómo será tu vuelo<br>antes de despegar</h1>
        <p>Convierte la incertidumbre en información: conoce las condiciones de tu vuelo y destino antes de embarcar.</p>
        <div class="hero-buttons">
            <a href="#buscar-vuelo" class="btn-primary">🔍 Buscar vuelo</a>
            <a href="#como-funciona" class="btn-secondary">Cómo funciona</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

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

# Lista de aeropuertos de España
aeropuertos = [
    "Madrid - Barajas (MAD)",
    "Barcelona - El Prat (BCN)",
    "Málaga - Costa del Sol (AGP)",
    "Palma de Mallorca (PMI)",
    "Alicante (ALC)",
    "Valencia (VLC)",
    "Sevilla (SVQ)",
    "Bilbao (BIO)",
    "Gran Canaria (LPA)",
    "Tenerife Norte (TFN)",
    "Tenerife Sur (TFS)",
    "Ibiza (IBZ)",
    "Menorca (MAH)",
    "Santiago (SCQ)",
    "Asturias (OVD)",
    "Zaragoza (ZAZ)"
]

with col1:
    origen = st.selectbox(
        "Ciudad / Aeropuerto salida",
        aeropuertos
    )

with col2:
    destino = st.selectbox(
        "Ciudad / Aeropuerto llegada",
        aeropuertos
    )
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
