import streamlit as st
import pandas as pd
import sys        # <--- ESTO DEBE ESTAR ANTES
import os         # <--- ESTO TAMBIÉN
import datetime
import base64

# Ahora que ya importaste sys y os, ya puedes usarlos:
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Ahora ya puedes importar tus archivos de la carpeta src
from ayuda_weather import load_weather_csv, get_weather_at, get_available_dates, degrees_to_compass
from flight_scoring import score_flight, score_to_rating
from avionstack import buscar_programacion_comercial, CIUDADES_IATA

st.set_page_config(page_title="Legion Flight", layout="wide")


def get_avion_base64():
    # Usamos tu archivo real
    img_path = os.path.join(os.path.dirname(__file__), "avion.jpeg")
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

imagen_fondo_64 = get_avion_base64()

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
    /* Estilo específico para el botón de buscar */
    div.stButton > button {
        width: 100% !important;
        height: 3.2em !important;
        margin-top: 28px !important; /* Lo baja para alinearlo con el texto de arriba */
        background-color: #2563eb !important; /* Azul profesional */
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-1px);
        box-shadow: 0px 4px 12px rgba(37, 99, 235, 0.3);
    }
 /* Estilo del botón: lo subimos un poco para que no esté desalineado abajo */
    div.stButton > button {
        width: 100% !important;
        height: 3.2em !important;
        margin-top: 25px !important; /* Ajustado para que quede recto con los otros */
        background-color: #2563eb !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
    }
/* Tarjeta de Vuelo Estilo Kayak */
    .flight-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 15px;
        border: 1px solid #e0e6ed;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.3s ease;
        color: #1a2b49;
    }

    .flight-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }

    .flight-info-main {
        flex: 1;
    }

    .flight-time {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 2px;
    }

    .flight-route {
        flex: 2;
        text-align: center;
        padding: 0 40px;
    }

    .route-line {
        flex-grow: 1;
        height: 2px;
        background-color: #cbd5e0;
        position: relative;
        margin: 0 15px;
    }

    .plane-icon {
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 1.2rem;
    }

    .rating-box {
        background-color: #2fb380;
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 1.2rem;
        text-align: center;
        min-width: 90px;
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

st.markdown(f"""
<div class="hero">
    <img src="data:image/jpeg;base64,{imagen_fondo_64}" alt="Avión en vuelo">

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

# Creamos las columnas para los selectores
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Usamos las llaves de CIUDADES_IATA (los nombres bonitos)
    # La variable 'origen' guardará el nombre: ej. "Madrid Barajas"
    origen = st.selectbox(
        "Ciudad / Aeropuerto salida",
        options=list(CIUDADES_IATA.keys()),
        index=0  # Selecciona Madrid por defecto
    )

with col2:
    # La variable 'destino' guardará el nombre: ej. "Barcelona El Prat"
    destino = st.selectbox(
        "Ciudad / Aeropuerto llegada",
        options=list(CIUDADES_IATA.keys()),
        index=1  # Selecciona Barcelona por defecto
    )

with col3:
    fecha = st.date_input(
        "Fecha salida",
        value=available_dates[0],
        min_value=available_dates[0],
        max_value=available_dates[-1],
    )

with col4:
    # Este botón activará la búsqueda real
    buscar = st.button("🔍 Buscar vuelos")

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
        # 1. Llamada a la API
        vuelos_reales = buscar_programacion_comercial(origen, destino)

        if not vuelos_reales:
            st.warning("No se encontraron vuelos comerciales programados.")
        else:
            # 1. ORDENACIÓN (Esto va dentro del else, alineado con el st.warning)
            for v in vuelos_reales:
                partes = v['hora_salida'].split(':')
                v['h_sort'] = int(partes[0])
                v['m_sort'] = int(partes[1])
            
            vuelos_reales = sorted(vuelos_reales, key=lambda x: (x['h_sort'], x['m_sort']))

            # 2. BUCLE ÚNICO (Solo un 'for', no dos)
            for vuelo in vuelos_reales:
                w_orig = get_weather_at(df_weather, origen, fecha, vuelo["hora_int"])
                w_dest = get_weather_at(df_weather, destino, fecha, (vuelo["hora_int"] + 1) % 24)

                if w_orig and w_dest:
                    result = score_flight(w_orig, w_dest)
                    
                    # Preparar datos seguros
                    temp_orig = w_orig.get('temperature', 0)
                    temp_dest = w_dest.get('temperature', 0)
                    viento = w_orig.get('windspeed', w_orig.get('wind_speed', 0))

                    try:
                        nota = float(result.get('rating', 0))
                    except:
                        nota = 0.0

                    # --- Lógica de color que faltaba ---
                    if nota >= 8:
                        color_nota = "#28a745"
                        etiqueta = "Excelente"
                    elif nota >= 5:
                        color_nota = "#ffc107"
                        etiqueta = "Bueno"
                    else:
                        color_nota = "#dc3545"
                        etiqueta = "Malo"
                        
                    # 3. DIBUJAR LA TARJETA
                    st.markdown(f"""
<div class="flight-card">
    <div class="flight-info-main">
        <div class="flight-time">{vuelo['hora_salida']}</div>
        <div style="font-size: 0.9rem; color: #718096; font-weight: 600;">{vuelo['linea']}</div>
        <div style="font-size: 0.8rem; color: #a0aec0;">{vuelo['vuelo']}</div>
    </div>
    <div class="flight-route">
        <div style="display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 1.3rem; font-weight: 700;">{CIUDADES_IATA[origen]}</span>
            <div class="route-line"><span class="plane-icon">✈️</span></div>
            <span style="font-size: 1.3rem; font-weight: 700;">{CIUDADES_IATA[destino]}</span>
        </div>
        <div style="font-size: 0.8rem; color: #718096; margin-top: 8px;">Directo • Programado</div>
    </div>
    <div style="display: flex; align-items: center; gap: 20px;">
        <div style="text-align: right; color: #4a5568; font-size: 0.9rem;">
            <div style="font-weight: 600;">🌡️ {temp_orig}°C / {temp_dest}°C</div>
            <div style="font-size: 0.8rem;">💨 {viento} km/h</div>
        </div>
        <div class="rating-box" style="background-color: {color_nota};">
            {nota:.1f}
            <div style="font-size: 0.6rem; font-weight: 400; text-transform: uppercase; margin-top: 2px;">{etiqueta}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
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
