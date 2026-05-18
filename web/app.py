import streamlit as st
import streamlit.components.v1 as components
import sys
import os
import base64
import json

# --- RUTAS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
src_path = os.path.join(project_root, "src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# --- IMPORTACIONES ---
try:
    from ayuda_weather import load_weather_csv, get_weather_at, get_available_dates, degrees_to_compass
    from flight_scoring import score_flight
    from avionstack import buscar_programacion_comercial, CIUDADES_IATA
except ModuleNotFoundError as e:
    st.error(f"Error crítico: No se encuentra el archivo en la carpeta src.")
    st.info(f"Python está buscando en: {src_path}")
    st.stop()

st.set_page_config(page_title="Legion Flight", layout="wide")

# --- USUARIOS JSON ---
USUARIOS_PATH = os.path.join(current_dir, "usuarios.json")

def cargar_usuarios():
    if os.path.exists(USUARIOS_PATH):
        with open(USUARIOS_PATH, "r") as f:
            return json.load(f)
    return {}

def guardar_usuarios(usuarios):
    with open(USUARIOS_PATH, "w") as f:
        json.dump(usuarios, f)

# --- SESSION STATE ---
if "favoritos" not in st.session_state:
    st.session_state["favoritos"] = []

# --- PRECIO ESTIMADO ---
# avionstack no devuelve precio. Se estima con región de ruta, hora, y aerolínea.
def estimar_precio(iata_orig, iata_dest, hora_int, linea, vuelo_code):
    SPAIN  = {"MAD","BCN","PMI","AGP","ALC","LPA","TFS","VLC","SVQ","BIO","IBZ","ACE","FUE","MAH","SCQ"}
    EUROPE = {"LHR","LGW","MAN","LIS","OPO","FAO","FCO","MXP","NAP","CDG","ORY","MRS","FRA","MUC","BER"}
    AFRICA = {"CMN","RAK","TNG"}

    def region(iata):
        if iata in SPAIN:  return "spain"
        if iata in EUROPE: return "europe"
        if iata in AFRICA: return "africa"
        return "other"

    r_o, r_d = region(iata_orig), region(iata_dest)

    if r_o == "spain" and r_d == "spain":
        base = 65.0
    elif "africa" in (r_o, r_d):
        base = 140.0
    else:
        base = 110.0

    # Hora pico
    if 7 <= hora_int <= 9 or 17 <= hora_int <= 20:
        base *= 1.25
    elif hora_int <= 5 or hora_int >= 23:
        base *= 0.85

    # Aerolínea
    LOW_COST = ["Ryanair", "easyJet", "Vueling", "Volotea", "Wizz Air", "Transavia"]
    PREMIUM  = ["British Airways", "Lufthansa", "Air France"]
    if any(lc in linea for lc in LOW_COST):
        base *= 0.75
    elif any(p in linea for p in PREMIUM):
        base *= 1.20

    # Pequeña varianza determinista basada en dígitos del código de vuelo
    try:
        digits = ''.join(filter(str.isdigit, vuelo_code))
        if digits:
            base += (int(digits[-1]) - 4.5) * 3
    except Exception:
        pass

    return max(29, round(base))


def get_avion_base64():
    img_path = os.path.join(current_dir, "assets", "avion.jpeg")
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

imagen_fondo_64 = get_avion_base64()

@st.cache_data(ttl=3600)
def load_data():
    return load_weather_csv()

df_weather = load_data()
available_dates = get_available_dates(df_weather)

# --- HERO WEATHER (Madrid Barajas, primera fecha disponible) ---
hero_weather = None
for try_hour in [12, 9, 15, 6, 0]:
    hero_weather = get_weather_at(df_weather, "Madrid Barajas", available_dates[0], try_hour)
    if hero_weather:
        break

if hero_weather:
    h_wind_speed  = f"{hero_weather['wind_speed']} km/h"
    h_wind_dir    = degrees_to_compass(hero_weather['wind_direction'])
    h_wind_deg    = f"{int(hero_weather['wind_direction'])}°"
    h_temp        = f"{hero_weather['temperature']} °C"
    h_precip_mm   = hero_weather['precipitation']
    h_precip_str  = f"{h_precip_mm} mm"
    p = h_precip_mm
    h_precip_label = "Sin lluvia" if p == 0 else ("Lluvia ligera" if p <= 1 else ("Lluvia moderada" if p <= 5 else "Lluvia intensa"))
else:
    h_wind_speed = h_wind_dir = h_wind_deg = h_temp = h_precip_str = "—"
    h_precip_label = "Sin datos"

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    h1, h2, h3, .hero-content h1 { font-family: 'Syne', sans-serif; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    [data-testid="stSidebar"]      { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    [data-testid="stAppViewContainer"] { background-color: #06080f; }

    .navbar {
        position: fixed; top: 0; left: 0; width: 100%; z-index: 9999;
        background-color: #0e1117; border-bottom: 1px solid #2e2e2e;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.6rem 2rem; box-sizing: border-box;
    }
    .navbar-logo {
        display: flex; align-items: center; gap: 0.5rem;
        font-size: 1.3rem; font-weight: 700; color: #fff;
        font-family: 'Syne', sans-serif;
    }
    .navbar-links {
        display: flex; gap: 2.5rem; align-items: center;
    }
    .navbar-links a {
        color: #c0c0c0; text-decoration: none; font-size: 0.95rem;
        font-weight: 500; transition: color 0.2s;
    }
    .navbar-links a:hover { color: #ffffff; }
    .navbar-right { display: flex; align-items: center; }
    .navbar-login {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        color: white !important; font-weight: 600 !important;
        padding: 0.42rem 1.1rem; border-radius: 8px;
        font-size: 0.9rem; text-decoration: none !important;
        transition: box-shadow 0.2s, transform 0.2s;
        white-space: nowrap;
    }
    .navbar-login:hover {
        box-shadow: 0 4px 16px rgba(37,99,235,0.5);
        transform: translateY(-1px);
    }
    .block-container { padding-top: 4.5rem !important; }

    /* Hero iframe full-width override */
    [data-testid="stCustomComponentV1"] iframe {
        width: calc(100% + 6rem) !important;
        margin-left: -3rem !important;
        margin-top: -1rem !important;
        border: none !important;
        display: block !important;
    }
    [data-testid="stCustomComponentV1"] {
        overflow: visible !important;
    }

    /* Tarjetas de vuelo */
    .flight-card {
        background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
        border: 1px solid rgba(255,255,255,0.07);
        border-left: 4px solid #2563eb;
        border-radius: 16px; padding: 28px 32px; margin-bottom: 6px;
        display: flex; align-items: center; justify-content: space-between;
        transition: all 0.25s ease; color: #e8eaf0;
    }
    .flight-card:hover {
        border-left-color: #3b82f6;
        box-shadow: 0 8px 32px rgba(37,99,235,0.18);
        transform: translateY(-3px);
    }
    .flight-info-main { flex: 1; }
    .flight-time { font-size: 1.8rem; font-weight: 700; margin-bottom: 2px; }
    .flight-route { flex: 2; text-align: center; padding: 0 40px; }
    .route-line {
        flex-grow: 1; height: 2px;
        background-color: rgba(255,255,255,0.15);
        position: relative; margin: 0 15px;
    }
    .plane-icon {
        position: absolute; top: -12px; left: 50%;
        transform: translateX(-50%); font-size: 1.2rem;
    }

    .rating-box {
        border-radius: 12px; font-family: 'Syne', sans-serif;
        font-size: 1.5rem; font-weight: 700; letter-spacing: -0.5px;
        padding: 14px 22px; text-align: center; min-width: 90px; color: white;
    }

    div.stButton > button {
        width: 100% !important; height: 3.2em !important;
        margin-top: 4px !important;
        background-color: #2563eb !important;
        color: white !important; font-weight: bold !important;
        border-radius: 8px !important; border: none !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-1px);
        box-shadow: 0px 4px 12px rgba(37,99,235,0.3);
    }
</style>

<div class="navbar">
    <div class="navbar-logo">✈️ Legion Flight</div>
    <div class="navbar-links">
        <a href="#buscar-vuelo">Buscar vuelo</a>
        <a href="#favoritos">Favoritos</a>
        <a href="#como-funciona">Cómo funciona</a>
        <a href="#contacto">Contacto</a>
    </div>
    <div class="navbar-right">
        <a href="/login" class="navbar-login">Iniciar sesión</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO (datos reales de Madrid Barajas)
# ─────────────────────────────────────────────

hero_component = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 100%; height: 100%; overflow: hidden; background: transparent; font-family: 'Inter', sans-serif; }}

@keyframes pulse-dot {{
    0%, 100% {{ opacity: 1; box-shadow: 0 0 6px #22c55e, 0 0 12px rgba(34,197,94,0.4); }}
    50%       {{ opacity: 0.4; box-shadow: 0 0 2px #22c55e; }}
}}

.hero {{
    position: relative;
    width: 100%; height: 600px; overflow: hidden;
    background-image: url('data:image/jpeg;base64,{imagen_fondo_64}');
    background-size: cover; background-position: center;
}}
.hero-overlay {{
    position: absolute; inset: 0; z-index: 1;
    background: linear-gradient(108deg, rgba(6,8,15,0.97) 0%, rgba(6,8,15,0.88) 38%, rgba(6,8,15,0.60) 60%, rgba(6,8,15,0.28) 100%);
}}
.hero-grid {{
    position: absolute; inset: 0; z-index: 1;
    background-image: radial-gradient(rgba(255,255,255,0.035) 1px, transparent 1px);
    background-size: 26px 26px;
}}
.hero-accent {{
    position: absolute; left: 0; top: 0; bottom: 0; z-index: 2; width: 3px;
    background: linear-gradient(to bottom, transparent 0%, #2563eb 30%, #3b82f6 70%, transparent 100%);
}}
.hero-live {{
    position: absolute; top: 1.6rem; left: 3rem; z-index: 4;
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: rgba(255,255,255,0.045);
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(12px);
    border-radius: 20px; padding: 0.28rem 0.85rem;
    font-size: 0.67rem; font-weight: 600; color: #9ca3af;
    letter-spacing: 0.1em; text-transform: uppercase;
}}
.hero-live-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: #22c55e;
    animation: pulse-dot 2s ease-in-out infinite;
    flex-shrink: 0;
}}
.hero-main {{
    position: absolute; bottom: 4.5rem; left: 3rem; z-index: 4; max-width: 480px;
}}
.hero-eyebrow {{
    font-size: 0.67rem; font-weight: 700; color: #3b82f6;
    text-transform: uppercase; letter-spacing: 0.14em; margin-bottom: 0.85rem;
}}
.hero-main h1 {{
    font-family: 'Syne', sans-serif;
    font-size: 2.9rem; font-weight: 800; line-height: 1.06;
    margin: 0 0 1rem 0;
    background: linear-gradient(135deg, #ffffff 20%, #bfdbfe 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.hero-main p {{
    font-size: 0.97rem; color: #9ca3af;
    margin: 0 0 1.6rem 0; line-height: 1.68; max-width: 420px;
}}
.hero-buttons {{ display: flex; gap: 0.75rem; flex-wrap: wrap; }}
.hero-buttons a {{
    padding: 0.65rem 1.35rem; border-radius: 10px; font-weight: 600;
    font-size: 0.9rem; text-decoration: none;
    display: inline-flex; align-items: center; gap: 0.4rem;
    transition: all 0.2s ease; font-family: 'Inter', sans-serif;
}}
.btn-primary {{
    background: linear-gradient(135deg, #1d4ed8, #3b82f6);
    color: white; box-shadow: 0 4px 18px rgba(37,99,235,0.45);
}}
.btn-secondary {{
    background: rgba(255,255,255,0.07); color: #d1d5db;
    border: 1px solid rgba(255,255,255,0.16); backdrop-filter: blur(8px);
}}
.hero-panel {{
    position: absolute; top: 50%; right: 3rem;
    transform: translateY(-50%); z-index: 4;
    background: rgba(10,13,20,0.75);
    backdrop-filter: blur(20px) saturate(1.4);
    border: 1px solid rgba(255,255,255,0.08);
    border-top: 2px solid #2563eb;
    border-radius: 18px; padding: 1.4rem 1.6rem; min-width: 220px;
}}
.hp-header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.1rem; padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}}
.hp-title {{
    font-family: 'Syne', sans-serif;
    font-size: 0.82rem; font-weight: 700; color: #e8eaf0;
}}
.hp-subtitle {{ font-size: 0.65rem; color: #6b7280; margin-top: 1px; }}
.hp-live-tag {{
    font-size: 0.58rem; font-weight: 700; color: #22c55e;
    text-transform: uppercase; letter-spacing: 0.08em;
    background: rgba(34,197,94,0.1); border-radius: 6px;
    padding: 0.15rem 0.45rem;
}}
.hp-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.58rem 0; border-bottom: 1px solid rgba(255,255,255,0.045);
}}
.hp-row:last-child {{ border-bottom: none; }}
.hp-label {{ font-size: 0.76rem; color: #6b7280; }}
.hp-value {{ font-size: 0.93rem; font-weight: 700; color: #e8eaf0; }}
.hero-strip {{
    position: absolute; bottom: 0; left: 0; right: 0; z-index: 4;
    background: rgba(6,8,15,0.88); backdrop-filter: blur(14px);
    border-top: 1px solid rgba(255,255,255,0.06);
    display: flex; align-items: stretch;
}}
.hs-item {{
    flex: 1; text-align: center;
    padding: 0.7rem 0.5rem; position: relative;
}}
.hs-item + .hs-item::before {{
    content: ''; position: absolute; left: 0; top: 20%; bottom: 20%;
    width: 1px; background: rgba(255,255,255,0.07);
}}
.hs-label {{
    font-size: 0.58rem; color: #6b7280;
    text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 0.2rem;
}}
.hs-value {{ font-size: 0.92rem; font-weight: 700; color: #e8eaf0; }}
.hs-accent {{ color: #3b82f6; }}
</style>
</head>
<body>
<div class="hero">
    <div class="hero-overlay"></div>
    <div class="hero-grid"></div>
    <div class="hero-accent"></div>

    <div class="hero-live">
        <span class="hero-live-dot"></span>
        Live &middot; Madrid Barajas
    </div>

    <div class="hero-main">
        <div class="hero-eyebrow">Analisis meteorologico de vuelos</div>
        <h1>Descubre como sera<br>tu vuelo</h1>
        <p>Convierte la incertidumbre en informacion: conoce las condiciones meteorologicas en origen y destino antes de embarcar.</p>
    </div>

    <div class="hero-panel">
        <div class="hp-header">
            <div>
                <div class="hp-title">Madrid Barajas</div>
                <div class="hp-subtitle">MAD &middot; Datos actuales</div>
            </div>
            <div class="hp-live-tag">Live</div>
        </div>
        <div class="hp-row">
            <span class="hp-label">Temperatura</span>
            <span class="hp-value">{h_temp}</span>
        </div>
        <div class="hp-row">
            <span class="hp-label">Viento</span>
            <span class="hp-value">{h_wind_speed}</span>
        </div>
        <div class="hp-row">
            <span class="hp-label">Direccion</span>
            <span class="hp-value">{h_wind_dir} &middot; {h_wind_deg}</span>
        </div>
        <div class="hp-row">
            <span class="hp-label">Precipitacion</span>
            <span class="hp-value">{h_precip_str}</span>
        </div>
        <div class="hp-row">
            <span class="hp-label">Condicion</span>
            <span class="hp-value" style="color:#22c55e;">{h_precip_label}</span>
        </div>
    </div>

    <div class="hero-strip">
        <div class="hs-item">
            <div class="hs-label">Aeropuerto</div>
            <div class="hs-value hs-accent">MAD</div>
        </div>
        <div class="hs-item">
            <div class="hs-label">Temperatura</div>
            <div class="hs-value">{h_temp}</div>
        </div>
        <div class="hs-item">
            <div class="hs-label">Viento</div>
            <div class="hs-value">{h_wind_speed}</div>
        </div>
        <div class="hs-item">
            <div class="hs-label">Direccion</div>
            <div class="hs-value">{h_wind_dir}</div>
        </div>
        <div class="hs-item">
            <div class="hs-label">Lluvia</div>
            <div class="hs-value">{h_precip_str}</div>
        </div>
        <div class="hs-item">
            <div class="hs-label">Estado</div>
            <div class="hs-value" style="color:#22c55e;">{h_precip_label}</div>
        </div>
    </div>
</div>
</body>
</html>"""

components.html(hero_component, height=600, scrolling=False)

st.markdown("")

# ─────────────────────────────────────────────
# BUSCADOR
# ─────────────────────────────────────────────
st.markdown('<div id="buscar-vuelo"></div>', unsafe_allow_html=True)

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
    import datetime as _dt
    _today = _dt.date.today()
    _one_month = _today + _dt.timedelta(days=30)
    _min_date = max(available_dates[0], _today)
    _max_date = min(available_dates[-1], _one_month)
    # Si hoy no está en los datos disponibles, usar el primer disponible
    _default = _min_date if _min_date in available_dates else available_dates[0]
    fecha = st.date_input(
        "Fecha salida",
        value=_default,
        min_value=_min_date,
        max_value=_max_date,
    )

with col4:
    buscar = st.button("Buscar vuelos")

# ─────────────────────────────────────────────
# RESULTADOS
# Los resultados se almacenan en session_state para que persistan
# entre reruns (necesario para que los botones "Ver detalle" y
# "Guardar" funcionen correctamente al hacer clic).
# ─────────────────────────────────────────────
if buscar:
    if origen == destino:
        st.error("El aeropuerto de origen y destino no pueden ser el mismo.")
        st.session_state.pop("resultados", None)
    else:
        vuelos_reales = buscar_programacion_comercial(origen, destino)
        if not vuelos_reales:
            st.warning("No se encontraron vuelos comerciales programados.")
            st.session_state.pop("resultados", None)
        else:
            vuelos_reales = sorted(vuelos_reales, key=lambda x: (x['hora_int'], x['minuto_int']))
            enriquecidos = []
            for vuelo in vuelos_reales:
                w_orig = get_weather_at(df_weather, origen, fecha, vuelo["hora_int"])
                w_dest = get_weather_at(df_weather, destino, fecha, (vuelo["hora_int"] + 1) % 24)
                if w_orig and w_dest:
                    datos_o = {
                        "temperature":    w_orig.get('temperature', 20),
                        "wind_speed":     w_orig.get('wind_speed', 0),
                        "precipitation":  w_orig.get('precipitation', 0),
                        "wind_direction": w_orig.get('wind_direction', 0),
                    }
                    datos_d = {
                        "temperature":    w_dest.get('temperature', 20),
                        "wind_speed":     w_dest.get('wind_speed', 0),
                        "precipitation":  w_dest.get('precipitation', 0),
                        "wind_direction": w_dest.get('wind_direction', 0),
                    }
                    result     = score_flight(datos_o, datos_d)
                    nota_final = result.get('rating', 0.0)
                    etiqueta   = result.get('label', 'Malo')
                    color_nota = result.get('color', '#dc3545')
                    precio     = estimar_precio(
                        CIUDADES_IATA[origen], CIUDADES_IATA[destino],
                        vuelo["hora_int"], vuelo["linea"], vuelo["vuelo"]
                    )
                    enriquecidos.append({
                        "vuelo":       vuelo,
                        "datos_o":     datos_o,
                        "datos_d":     datos_d,
                        "nota_final":  nota_final,
                        "etiqueta":    etiqueta,
                        "color_nota":  color_nota,
                        "precio":      precio,
                        "origen":      origen,
                        "destino":     destino,
                        "fecha":       str(fecha),
                    })
            st.session_state["resultados"] = enriquecidos

# Renderizar siempre desde session_state (fuera del if buscar)
# Así cuando se hace clic en un botón y Streamlit rerenderiza,
# los resultados siguen visibles y el botón puede ejecutarse.
for item in st.session_state.get("resultados", []):
    vuelo      = item["vuelo"]
    datos_o    = item["datos_o"]
    datos_d    = item["datos_d"]
    nota_final = item["nota_final"]
    etiqueta   = item["etiqueta"]
    color_nota = item["color_nota"]
    precio     = item["precio"]
    origen_r   = item["origen"]
    destino_r  = item["destino"]
    fecha_r    = item["fecha"]

    st.markdown(f"""
    <div class="flight-card">
        <div class="flight-info-main">
            <div class="flight-time">{vuelo['hora_salida']}</div>
            <div style="font-size:0.9rem;color:#6b7280;font-weight:600;">{vuelo['linea']}</div>
            <div style="font-size:0.8rem;color:#9ca3af;">{vuelo['vuelo']}</div>
        </div>
        <div class="flight-route">
            <div style="display:flex;align-items:center;justify-content:center;">
                <span style="font-size:1.3rem;font-weight:700;">{CIUDADES_IATA[origen_r]}</span>
                <div class="route-line"><span class="plane-icon">✈️</span></div>
                <span style="font-size:1.3rem;font-weight:700;">{CIUDADES_IATA[destino_r]}</span>
            </div>
            <div style="font-size:0.8rem;color:#6b7280;margin-top:8px;">Directo · Programado</div>
        </div>
        <div style="text-align:center;padding:0 24px;min-width:110px;">
            <div style="font-size:1.2rem;font-weight:700;color:#e8eaf0;">~{precio} €</div>
            <div style="font-size:0.7rem;color:#6b7280;margin-top:2px;">estimado</div>
        </div>
        <div style="display:flex;align-items:center;gap:20px;">
            <div style="text-align:right;color:#9ca3af;font-size:0.9rem;">
                <div style="font-weight:600;">{datos_o['temperature']}°C / {datos_d['temperature']}°C</div>
                <div style="font-size:0.8rem;">{datos_o['wind_speed']} km/h</div>
            </div>
            <div class="rating-box" style="background-color:{color_nota};">
                {nota_final:.1f}
                <div style="font-size:0.6rem;font-weight:400;text-transform:uppercase;margin-top:2px;">{etiqueta}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    btn_col1, btn_col2 = st.columns(2)

    with btn_col1:
        if st.button("Ver detalle", key=f"det_{vuelo['vuelo']}_{vuelo['hora_salida']}"):
            st.session_state["vuelo_seleccionado"] = {
                "linea":       vuelo["linea"],
                "vuelo":       vuelo["vuelo"],
                "hora_salida": vuelo["hora_salida"],
                "hora_int":    vuelo["hora_int"],
                "estado":      vuelo.get("estado", "N/A"),
                "origen":      origen_r,
                "destino":     destino_r,
                "iata_orig":   CIUDADES_IATA[origen_r],
                "iata_dest":   CIUDADES_IATA[destino_r],
                "fecha":       fecha_r,
                "temp_orig":   datos_o["temperature"],
                "viento_orig": datos_o["wind_speed"],
                "precip_orig": datos_o["precipitation"],
                "dir_orig":    datos_o["wind_direction"],
                "temp_dest":   datos_d["temperature"],
                "viento_dest": datos_d["wind_speed"],
                "precip_dest": datos_d["precipitation"],
                "dir_dest":    datos_d["wind_direction"],
                "nota":        nota_final,
                "etiqueta":    etiqueta,
                "color":       color_nota,
                "precio":      precio,
            }
            st.switch_page("pages/detalle_vuelo.py")

    with btn_col2:
        ya_guardado = any(
            f["vuelo"] == vuelo["vuelo"] and f["hora_salida"] == vuelo["hora_salida"]
            for f in st.session_state["favoritos"]
        )
        label_fav = "★ Guardado" if ya_guardado else "☆ Guardar"

        if st.button(label_fav, key=f"fav_{vuelo['vuelo']}_{vuelo['hora_salida']}"):
            if not st.session_state.get("usuario"):
                st.toast("Inicia sesión para guardar favoritos", icon="🔒")
            else:
                if ya_guardado:
                    st.session_state["favoritos"] = [
                        f for f in st.session_state["favoritos"]
                        if not (f["vuelo"] == vuelo["vuelo"] and f["hora_salida"] == vuelo["hora_salida"])
                    ]
                    st.toast("Eliminado de favoritos", icon="🗑️")
                else:
                    fav = {
                        "origen":      origen_r,
                        "destino":     destino_r,
                        "iata_orig":   CIUDADES_IATA[origen_r],
                        "iata_dest":   CIUDADES_IATA[destino_r],
                        "fecha":       fecha_r,
                        "hora_salida": vuelo["hora_salida"],
                        "linea":       vuelo["linea"],
                        "vuelo":       vuelo["vuelo"],
                        "nota":        nota_final,
                        "etiqueta":    etiqueta,
                        "color":       color_nota,
                        "temp_orig":   datos_o["temperature"],
                        "temp_dest":   datos_d["temperature"],
                        "viento":      datos_o["wind_speed"],
                        "precio":      precio,
                    }
                    st.session_state["favoritos"].append(fav)
                    st.toast("Vuelo guardado en favoritos", icon="⭐")

                usuarios = cargar_usuarios()
                username = st.session_state["usuario"]
                if username in usuarios:
                    usuarios[username]["favoritos"] = st.session_state["favoritos"]
                guardar_usuarios(usuarios)
                st.rerun()

# ─────────────────────────────────────────────
# FAVORITOS
# ─────────────────────────────────────────────
st.markdown('<div id="favoritos"></div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown("## Vuelos favoritos")

if not st.session_state.get("usuario"):
    st.info("Inicia sesión para ver tus vuelos guardados")
    if st.button("Iniciar sesión", key="btn_login_favoritos"):
        st.switch_page("pages/login.py")
elif not st.session_state["favoritos"]:
    st.markdown('<p style="color:#6b7280;">Aún no tienes vuelos guardados.</p>', unsafe_allow_html=True)
else:
    for fav in st.session_state["favoritos"]:
        precio_fav = fav.get("precio", "—")
        precio_fav_str = f"~{precio_fav} €" if isinstance(precio_fav, int) else "—"
        st.markdown(f"""
        <div class="flight-card">
            <div class="flight-info-main">
                <div class="flight-time">{fav['hora_salida']}</div>
                <div style="font-size:0.9rem;color:#6b7280;font-weight:600;">{fav['linea']}</div>
                <div style="font-size:0.8rem;color:#9ca3af;">{fav['vuelo']} · {fav['fecha']}</div>
            </div>
            <div class="flight-route">
                <div style="display:flex;align-items:center;justify-content:center;">
                    <span style="font-size:1.3rem;font-weight:700;">{fav['iata_orig']}</span>
                    <div class="route-line"><span class="plane-icon">✈️</span></div>
                    <span style="font-size:1.3rem;font-weight:700;">{fav['iata_dest']}</span>
                </div>
                <div style="font-size:0.8rem;color:#6b7280;margin-top:8px;">{fav['origen']} → {fav['destino']}</div>
            </div>
            <div style="text-align:center;padding:0 24px;min-width:110px;">
                <div style="font-size:1.2rem;font-weight:700;color:#e8eaf0;">{precio_fav_str}</div>
                <div style="font-size:0.7rem;color:#6b7280;margin-top:2px;">estimado</div>
            </div>
            <div style="display:flex;align-items:center;gap:20px;">
                <div style="text-align:right;color:#9ca3af;font-size:0.9rem;">
                    <div style="font-weight:600;">{fav['temp_orig']}°C / {fav['temp_dest']}°C</div>
                    <div style="font-size:0.8rem;">{fav['viento']} km/h</div>
                </div>
                <div class="rating-box" style="background-color:{fav['color']};">
                    {fav['nota']:.1f}
                    <div style="font-size:0.6rem;font-weight:400;text-transform:uppercase;margin-top:2px;">{fav['etiqueta']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        fav_col1, fav_col2 = st.columns(2)
        with fav_col1:
            if st.button("Ver detalle", key=f"det_fav_{fav['vuelo']}_{fav['hora_salida']}"):
                st.session_state["vuelo_seleccionado"] = {
                    "linea":       fav["linea"],
                    "vuelo":       fav["vuelo"],
                    "hora_salida": fav["hora_salida"],
                    "hora_int":    int(fav["hora_salida"].split(":")[0]),
                    "estado":      "N/A",
                    "origen":      fav["origen"],
                    "destino":     fav["destino"],
                    "iata_orig":   fav["iata_orig"],
                    "iata_dest":   fav["iata_dest"],
                    "fecha":       fav["fecha"],
                    "temp_orig":   fav["temp_orig"],
                    "viento_orig": fav["viento"],
                    "precip_orig": 0,
                    "dir_orig":    0,
                    "temp_dest":   fav["temp_dest"],
                    "viento_dest": fav["viento"],
                    "precip_dest": 0,
                    "dir_dest":    0,
                    "nota":        fav["nota"],
                    "etiqueta":    fav["etiqueta"],
                    "color":       fav["color"],
                    "precio":      fav.get("precio", 0),
                }
                st.switch_page("pages/detalle_vuelo.py")
        with fav_col2:
            if st.button("Eliminar", key=f"del_{fav['vuelo']}_{fav['hora_salida']}"):
                st.session_state["favoritos"] = [
                    f for f in st.session_state["favoritos"]
                    if not (f["vuelo"] == fav["vuelo"] and f["hora_salida"] == fav["hora_salida"])
                ]
                usuarios = cargar_usuarios()
                username = st.session_state["usuario"]
                if username in usuarios:
                    usuarios[username]["favoritos"] = st.session_state["favoritos"]
                guardar_usuarios(usuarios)
                st.rerun()

# ─────────────────────────────────────────────
# CÓMO FUNCIONA
# ─────────────────────────────────────────────
st.markdown('<div id="como-funciona"></div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown("## Cómo funciona")

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-top:3px solid #2563eb;border-radius:14px;padding:28px 24px;">
      <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:white;margin-bottom:10px;">1. Busca</div>
      <div style="color:#9ca3af;font-size:0.9rem;line-height:1.6;">Selecciona tu aeropuerto de origen, destino y fecha de vuelo.</div>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-top:3px solid #2563eb;border-radius:14px;padding:28px 24px;">
      <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:white;margin-bottom:10px;">2. Analiza</div>
      <div style="color:#9ca3af;font-size:0.9rem;line-height:1.6;">Consulta las condiciones meteorológicas reales en origen y destino.</div>
    </div>
    """, unsafe_allow_html=True)
with col_c:
    st.markdown("""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-top:3px solid #2563eb;border-radius:14px;padding:28px 24px;">
      <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:white;margin-bottom:10px;">3. Decide</div>
      <div style="color:#9ca3af;font-size:0.9rem;line-height:1.6;">Elige el horario con mejores condiciones para volar.</div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONTACTO
# ─────────────────────────────────────────────
st.markdown('<div id="contacto"></div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown("## Contacto")
st.write("¿Tienes dudas? Escríbenos a **contacto@legionflight.com**")

# ─────────────────────────────────────────────
# FAQ
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("## FAQ")

faq_items = [
    ("¿De dónde salen los datos meteorológicos?", "Utilizamos Open-Meteo, un servicio meteorológico de código abierto que combina modelos numéricos de alta precisión como ECMWF y GFS."),
    ("¿Qué variables meteorológicas se analizan?", "Analizamos tres factores clave: temperatura, velocidad del viento y precipitación. Cada uno tiene un peso distinto en la puntuación final del vuelo."),
    ("¿Cómo se calcula la puntuación del vuelo?", "La puntuación combina el clima en origen y destino. El viento tiene un peso del 45%, la precipitación del 40% y la temperatura del 15%. Se aplica el peor de los dos aeropuertos."),
    ("¿Hasta cuándo puedo consultar previsiones?", "Cubrimos aproximadamente 30 días hacia adelante con datos reales. Para fechas más lejanas usamos datos históricos del mismo periodo del año anterior como referencia."),
    ("¿Los precios mostrados son reales?", "Los precios son estimaciones calculadas algorítmicamente según ruta, hora del vuelo y aerolínea. No representan tarifas reales ni están vinculados a ningún sistema de reservas."),
]

for pregunta, respuesta in faq_items:
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-left: 3px solid #2563eb;
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
    ">
        <div style="font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:700;color:#e8eaf0;margin-bottom:0.6rem;">{pregunta}</div>
        <div style="font-size:0.88rem;color:#9ca3af;line-height:1.65;">{respuesta}</div>
    </div>
    """, unsafe_allow_html=True)
