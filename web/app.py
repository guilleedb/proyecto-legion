import streamlit as st
import pandas as pd
import sys
import os
import datetime
import base64
import random

def obtener_precio_estimado(origen, destino):
    # Definimos precios base por ciudad para simular realismo
    precios_base = {
        "Madrid": 50, "Barcelona": 45, "Londres": 80, 
        "Paris": 75, "Nueva York": 450, "Roma": 60
    }
    
    # Extraemos el nombre de la ciudad del string del selector (ej: "Madrid Barajas" -> "Madrid")
    ciudad_ori = origen.split()[0]
    ciudad_des = destino.split()[0]
    
    # Lógica: Precio base del destino + un extra por origen + un toque aleatorio
    base = precios_base.get(ciudad_des, 100) 
    extra_origen = precios_base.get(ciudad_ori, 50) * 0.2
    
    precio_final = int(base + extra_origen + random.randint(5, 25))
    return precio_final
# --- CONFIGURACIÓN DE RUTAS ---
# Obtenemos la ruta absoluta de la carpeta donde está este archivo (app.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Subimos un nivel para encontrar la carpeta 'src'
project_root = os.path.abspath(os.path.join(current_dir, ".."))
src_path = os.path.join(project_root, "src")

# Añadimos 'src' al sistema para que Python encuentre tus archivos
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# --- IMPORTACIONES ---
try:
    from ayuda_weather import load_weather_csv, get_weather_at, get_available_dates, degrees_to_compass
    from flight_scoring import score_flight, score_to_rating
    from avionstack import buscar_programacion_comercial, CIUDADES_IATA
except ModuleNotFoundError as e:
    st.error(f"❌ Error crítico: No se encuentra el archivo en la carpeta src.")
    st.info(f"Python está buscando en: {src_path}")
    st.stop()
st.set_page_config(page_title="Legion Flight", layout="wide")


def get_avion_base64():
    # Usamos tu archivo real
    img_path = os.path.join(os.path.dirname(__file__), "assets", "avion.jpeg")
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
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 1.2rem;
        text-align: center;
        min-width: 90px;
    }
/* Tarjeta de vuelo mejorada */
.flight-card {
    background: white;
    border-radius: 15px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    border: 1px solid #eef2f6;
    transition: 0.3s;
    overflow: hidden;
}

.flight-card:hover {
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    border-color: #2563eb;
}

/* Sección de información (Izquierda) */
.flight-main-content {
    padding: 25px;
    flex-grow: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

/* Sección de precio (Derecha) */
.flight-price-section {
    background: #f8f9fc;
    padding: 25px;
    min-width: 160px;
    text-align: center;
    border-left: 1px solid #eef2f6;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.price-value {
    font-size: 2rem;
    font-weight: 800;
    color: #1a2b49;
    letter-spacing: -1px;
}

.price-currency { font-size: 1rem; color: #1a2b49; margin-left: 2px; }

.price-tag {
    font-size: 0.7rem;
    color: #2ecc71;
    font-weight: 700;
    text-transform: uppercase;
    margin-top: 5px;
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
    # España
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
    # Inglaterra
    "London Heathrow",
    "London Gatwick",
    "Manchester",
    # Portugal
    "Lisboa",
    "Oporto",
    "Faro",
    # Marruecos
    "Casablanca Mohammed V",
    "Marrakech Menara",
    "Tánger Ibn Battouta",
    # Italia
    "Roma Fiumicino",
    "Milán Malpensa",
    "Nápoles",
    # Francia
    "París Charles de Gaulle",
    "París Orly",
    "Marsella",
    # Alemania
    "Frankfurt",
    "Múnich",
    "Berlín Brandenburg",
]

# BUSCADOR
st.markdown('<div id="buscar-vuelo"></div>', unsafe_allow_html=True)

# Creamos las columnas para los selectores
col1, col2, col3, col4 = st.columns(4)

with col1:
    origen = st.selectbox(
        "Ciudad / Aeropuerto salida",
        options=list(CIUDADES_IATA.keys()),
        index=0,
        placeholder="Escribe para buscar...",
    )

with col2:
    destino = st.selectbox(
        "Ciudad / Aeropuerto llegada",
        options=list(CIUDADES_IATA.keys()),
        index=1,
        placeholder="Escribe para buscar...",
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
        vuelos_reales = buscar_programacion_comercial(origen, destino)

        if not vuelos_reales:
            st.warning("No se encontraron vuelos comerciales programados.")
        else:
            # 1. Calculamos el precio base una vez para toda la búsqueda
            # (Asegúrate de haber pegado la función obtener_precio_estimado arriba del todo)
            precio_ruta = obtener_precio_estimado(origen, destino)

            # Ordenar vuelos por hora
            for v in vuelos_reales:
                partes = v['hora_salida'].split(':')
                v['h_sort'] = int(partes[0])
                v['m_sort'] = int(partes[1])
            
            vuelos_reales = sorted(vuelos_reales, key=lambda x: (x['h_sort'], x['m_sort']))

            # Bucle para mostrar cada tarjeta
            for vuelo in vuelos_reales:
                w_orig = get_weather_at(df_weather, origen, fecha, vuelo["hora_int"])
                w_dest = get_weather_at(df_weather, destino, fecha, (vuelo["hora_int"] + 1) % 24)

                if w_orig and w_dest:
                    # Normalizamos datos de clima
                    datos_o = {
                        "temperature": w_orig.get('temperature', 20),
                        "wind_speed": w_orig.get('windspeed', w_orig.get('wind_speed', 0)),
                        "precipitation": w_orig.get('precipitation', 0)
                    }
                    datos_d = {
                        "temperature": w_dest.get('temperature', 20),
                        "wind_speed": w_dest.get('windspeed', w_dest.get('wind_speed', 0)),
                        "precipitation": w_dest.get('precipitation', 0)
                    }

                    # Calculamos la nota
                    result = score_flight(datos_o, datos_d)
                    nota_final = result.get('rating', 0.0)
                    etiqueta = result.get('label', 'Malo')
                    color_nota = result.get('color', '#dc3545')

                    # --- LÓGICA DE PRECIO INDIVIDUAL ---
                    # Variamos el precio +- 10€ según la aerolínea para que parezca real
                    precio_vuelo = precio_ruta + random.randint(-10, 15)

                    # 3. Dibujamos la tarjeta con la sección de precio a la derecha
                    st.markdown(f"""
                    <div class="flight-card">
                        <div class="flight-main-content">
                            <div class="flight-info-main">
                                <div class="flight-time">{vuelo['hora_salida']}</div>
                                <div style="font-size: 0.9rem; color: #718096; font-weight: 600;">{vuelo['linea']}</div>
                                <div style="font-size: 0.8rem; color: #a0aec0;">{vuelo['vuelo']}</div>
                            </div>
                            
                            <div class="flight-route" style="flex-grow: 1; text-align: center;">
                                <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
                                    <span style="font-size: 1.2rem; font-weight: 700;">{CIUDADES_IATA[origen]}</span>
                                    <div style="height: 2px; background: #eef2f6; width: 60px; position: relative;">
                                        <span style="position: absolute; top: -10px; left: 20px;">✈️</span>
                                    </div>
                                    <span style="font-size: 1.2rem; font-weight: 700;">{CIUDADES_IATA[destino]}</span>
                                </div>
                                <div style="font-size: 0.75rem; color: #a0aec0; margin-top: 5px;">
                                    🌡️ {datos_o['temperature']}°C → {datos_d['temperature']}°C
                                </div>
                            </div>

                            <div style="margin: 0 25px;">
                                <div class="rating-box" style="background-color: {color_nota}; margin: 0;">
                                    {nota_final:.1f}
                                    <div style="font-size: 0.5rem; font-weight: 400; text-transform: uppercase;">{etiqueta}</div>
                                </div>
                            </div>
                        </div>

                        <div class="flight-price-section">
                            <div class="price-value">{precio_vuelo}<span style="font-size: 1rem;">€</span></div>
                            <div class="price-tag">Estimado</div>
                            <div style="margin-top: 10px;">
                                <button style="background: #2563eb; color: white; border: none; padding: 5px 12px; border-radius: 6px; font-size: 0.7rem; cursor: pointer;">Seleccionar</button>
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
