import streamlit as st
import pandas as pd

st.set_page_config(page_title="Legion Flight", layout="wide")

# HEADER
st.title("✈️ Legion Flight")
st.markdown("### Descubre cómo será tu vuelo antes de despegar")

# SEPARADOR
st.markdown("---")

# BUSCADOR (como tu dibujo)
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

# LATERAL (como el sidebar dibujado)
st.sidebar.title("⚙️ Filtros")

precio_max = st.sidebar.slider("Precio máximo (€)", 0, 200, 100)
hora = st.sidebar.selectbox("Horario preferido", ["Cualquiera", "Mañana", "Tarde"])

st.sidebar.markdown("---")
st.sidebar.write("✈️ Opciones adicionales")
st.sidebar.checkbox("Solo vuelos directos")
st.sidebar.checkbox("Equipaje incluido")

# FOOTER tipo FAQ
st.markdown("---")
st.markdown("## ❓ FAQ")

st.write("""
- ¿Puedo cambiar mi vuelo? → Sí  
- ¿Incluye equipaje? → Depende de la tarifa  
- ¿Hay cancelación gratuita? → En algunos casos  
""")