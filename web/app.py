import streamlit as st
import pandas as pd

st.set_page_config(page_title="Legion Flight", layout="wide")

# Ocultar header por defecto de Streamlit y añadir navbar custom
st.markdown("""
<style>
    /* Ocultar menú hamburguesa y footer de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Navbar */
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
        text-decoration: none;
    }
    .navbar-logo span {
        font-size: 1.5rem;
    }
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
    .navbar-links a:hover {
        color: #ffffff;
    }
    .navbar-spacer {
        width: 150px;
    }

    /* Empujar el contenido debajo de la navbar */
    .block-container {
        padding-top: 4.5rem !important;
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

# SEPARADOR
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
    fecha = st.date_input("Fecha salida")

with col4:
    buscar = st.button("🔍 Buscar vuelos")

st.markdown("---")

# RESULTADOS
if buscar:
    st.subheader("✈️ Resultados de vuelos")

    # Simulación de datos
    data = {
        "Origen": [origen]*3,
        "Destino": [destino]*3,
        "Hora salida": ["08:00", "12:30", "18:45"],
        "Hora llegada": ["10:00", "14:30", "20:45"],
        "Duración": ["2h", "2h", "2h"],
        "Precio (€)": [45, 60, 80]
    }

    df = pd.DataFrame(data)

    st.dataframe(df, use_container_width=True)

# CÓMO FUNCIONA
st.markdown('<div id="como-funciona"></div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown("## ⚙️ Cómo funciona")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown("### 1. Busca")
    st.write("Introduce tu origen, destino y fecha de vuelo.")
with col_b:
    st.markdown("### 2. Compara")
    st.write("Revisa los vuelos disponibles con precios y horarios.")
with col_c:
    st.markdown("### 3. Decide")
    st.write("Elige el vuelo que mejor se adapte a ti.")

# CONTACTO
st.markdown('<div id="contacto"></div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown("## 📩 Contacto")
st.write("¿Tienes dudas? Escríbenos a **contacto@legionflight.com**")

# FAQ
st.markdown("---")
st.markdown("## ❓ FAQ")

st.write("""
- ¿Puedo cambiar mi vuelo? → Sí
- ¿Incluye equipaje? → Depende de la tarifa
- ¿Hay cancelación gratuita? → En algunos casos
""")