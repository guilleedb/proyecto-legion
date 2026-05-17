import streamlit as st
import pandas as pd
import sys
import os
import datetime
import base64
import random
import json
import hashlib

st.set_page_config(page_title="Legion Flight", layout="wide")

# ─────────────────────────────────────────────
#  RUTAS
# ─────────────────────────────────────────────
current_dir  = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
src_path     = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from ayuda_weather import load_weather_csv, get_weather_at, get_available_dates, degrees_to_compass
    from flight_scoring import score_flight, score_to_rating
    from avionstack import buscar_programacion_comercial, CIUDADES_IATA
except ModuleNotFoundError:
    st.error("❌ Error crítico: No se encuentra el archivo en la carpeta src.")
    st.stop()

# ─────────────────────────────────────────────
#  USUARIOS (JSON local) – favoritos persistentes
# ─────────────────────────────────────────────
DB_PATH = os.path.join(current_dir, "usuarios.json")

def cargar_usuarios():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return {}

def guardar_usuarios(u):
    with open(DB_PATH, "w") as f:
        json.dump(u, f)

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def do_login(email, pw):
    u = cargar_usuarios()
    if email not in u:
        return False, "Email no encontrado."
    if u[email]["password"] != hash_pw(pw):
        return False, "Contraseña incorrecta."
    return True, u[email]

def do_register(nombre, email, pw):
    u = cargar_usuarios()
    if email in u:
        return False, "Este email ya está registrado."
    u[email] = {"nombre": nombre, "password": hash_pw(pw), "favoritos": []}
    guardar_usuarios(u)
    return True, u[email]

def guardar_favorito_db(email, fav):
    u = cargar_usuarios()
    if email in u:
        if "favoritos" not in u[email]:
            u[email]["favoritos"] = []
        u[email]["favoritos"].append(fav)
        guardar_usuarios(u)

def eliminar_favorito_db(email, idx):
    u = cargar_usuarios()
    if email in u and "favoritos" in u[email]:
        u[email]["favoritos"].pop(idx)
        guardar_usuarios(u)

def limpiar_favoritos_db(email):
    u = cargar_usuarios()
    if email in u:
        u[email]["favoritos"] = []
        guardar_usuarios(u)

# ─────────────────────────────────────────────
#  ESTADO DE SESIÓN
# ─────────────────────────────────────────────
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None
if "usuario_email" not in st.session_state:
    st.session_state["usuario_email"] = None
if "favoritos" not in st.session_state:
    st.session_state["favoritos"] = []
if "modal_vuelo" not in st.session_state:
    st.session_state["modal_vuelo"] = None
if "vista" not in st.session_state:
    st.session_state["vista"] = "inicio"  # inicio | login | favoritos

# ─────────────────────────────────────────────
#  FUNCIONES
# ─────────────────────────────────────────────
def obtener_precio_estimado(origen, destino):
    precios_base = {
        "Madrid": 50, "Barcelona": 45, "Londres": 80,
        "Paris": 75, "Nueva York": 450, "Roma": 60
    }
    base = precios_base.get(destino.split()[0], 100)
    extra = precios_base.get(origen.split()[0], 50) * 0.2
    return int(base + extra + random.randint(5, 25))

def get_avion_base64():
    img_path = os.path.join(current_dir, "assets", "avion.jpeg")
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

@st.cache_data
def load_data():
    return load_weather_csv()

df_weather      = load_data()
available_dates = get_available_dates(df_weather)
imagen_fondo_64 = get_avion_base64()

# ─────────────────────────────────────────────
#  CSS GLOBAL
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0a0f !important;
    color: #e2e8f0;
}
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
[data-testid="stSidebar"] { display: none !important; }

.block-container { padding-top: 5rem !important; padding-bottom: 2rem !important; }

/* ── NAVBAR ── */
.navbar {
    position: fixed; top: 0; left: 0; width: 100%; z-index: 9000;
    background: rgba(10,10,15,0.92);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.8rem 2.5rem;
}
.navbar-logo {
    font-size: 1.1rem; font-weight: 700; color: #fff;
    letter-spacing: -0.3px; display: flex; align-items: center; gap: 0.5rem;
}
.logo-accent { color: #4f8ef7; }
.navbar-nav { display: flex; gap: 1.5rem; align-items: center; }
.navbar-nav button {
    background: none; border: none; cursor: pointer;
    color: #94a3b8; font-size: 0.85rem; font-weight: 500;
    padding: 0.3rem 0.7rem; border-radius: 6px; transition: 0.2s;
    font-family: 'Inter', sans-serif;
}
.navbar-nav button:hover { color: #fff; background: rgba(255,255,255,0.07); }
.navbar-user {
    display: flex; align-items: center; gap: 0.7rem; font-size: 0.85rem; color: #94a3b8;
}
.user-avatar {
    width: 30px; height: 30px; border-radius: 50%;
    background: #1e3a5f; border: 1px solid #4f8ef7;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.75rem; font-weight: 700; color: #4f8ef7;
}

/* ── HERO ── */
.hero {
    position: relative;
    width: calc(100% + 6rem); margin-left: -3rem; margin-top: -1rem;
    height: 480px; overflow: hidden; border-radius: 0 0 20px 20px;
}
.hero img { width: 100%; height: 100%; object-fit: cover; display: block; }
.hero::after {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(to bottom, rgba(10,10,15,0.25) 0%, rgba(10,10,15,0.7) 100%);
}
.hero-content {
    position: absolute; bottom: 3rem; left: 3rem; z-index: 2;
}
.hero-content h1 {
    font-size: 2.4rem; font-weight: 700;
    color: #fff; margin: 0 0 0.5rem 0;
    line-height: 1.2; letter-spacing: -0.8px;
}
.hero-content h1 em { color: #4f8ef7; font-style: normal; }
.hero-content p { font-size: 0.95rem; color: #cbd5e1; max-width: 480px; line-height: 1.6; margin: 0; }

/* ── SEARCH ── */
.search-section {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 1.6rem 1.8rem;
    margin: 1.8rem 0;
}
.search-section label { color: #94a3b8 !important; font-size: 0.78rem !important; font-weight: 500 !important; }
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stDateInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
}

/* ── BUTTONS ── */
div.stButton > button {
    width: 100% !important;
    background: #1e3a5f !important;
    color: #93c5fd !important; font-weight: 600 !important;
    border-radius: 8px !important;
    border: 1px solid rgba(79,142,247,0.25) !important;
    height: 3em !important; font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important; letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover {
    background: #1e4080 !important;
    border-color: rgba(79,142,247,0.5) !important;
    color: #bfdbfe !important;
}

/* ── RESULTS HEADER ── */
.results-header {
    font-size: 0.78rem; font-weight: 600; color: #64748b;
    text-transform: uppercase; letter-spacing: 0.08em;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding-bottom: 0.6rem; margin: 1.5rem 0 1rem 0;
}
.results-header span { color: #4f8ef7; }

/* ── FLIGHT CARD ── */
.flight-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; overflow: hidden;
    display: flex; align-items: stretch;
    margin-bottom: 2px; transition: all 0.2s ease;
}
.flight-card:hover {
    border-color: rgba(79,142,247,0.3);
    background: rgba(255,255,255,0.04);
}
.flight-main-content {
    padding: 18px 24px; flex-grow: 1;
    display: flex; align-items: center; justify-content: space-between;
}
.flight-time { font-size: 1.7rem; font-weight: 700; color: #fff; letter-spacing: -0.8px; }
.flight-airline { font-size: 0.8rem; color: #94a3b8; margin-top: 2px; }
.flight-number  { font-size: 0.72rem; color: #4b5563; margin-top: 2px; }
.flight-route   { flex-grow: 1; text-align: center; padding: 0 24px; }
.route-inner    { display: flex; align-items: center; justify-content: center; gap: 12px; }
.iata           { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }
.route-line     { height: 1px; background: rgba(255,255,255,0.12); width: 50px; position: relative; }
.plane-icon     { position: absolute; top: -9px; left: 14px; font-size: 0.9rem; }
.route-temps    { font-size: 0.7rem; color: #4b5563; margin-top: 6px; }
.rating-wrap    { margin: 0 16px; }
.rating-box {
    color: white; padding: 8px 14px; border-radius: 8px;
    font-weight: 700; font-size: 1.25rem; text-align: center; min-width: 76px;
}
.rating-label { font-size: 0.48rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 3px; opacity: 0.8; }
.flight-price-section {
    background: rgba(255,255,255,0.02);
    padding: 18px 22px; min-width: 130px;
    text-align: center; border-left: 1px solid rgba(255,255,255,0.05);
    display: flex; flex-direction: column; justify-content: center;
}
.price-value    { font-size: 1.8rem; font-weight: 700; color: #fff; letter-spacing: -1px; }
.price-currency { font-size: 0.9rem; color: #64748b; }
.price-tag      { font-size: 0.62rem; color: #22c55e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 3px; }

/* ── MODAL OVERLAY ── */
.modal-backdrop {
    position: fixed; inset: 0; z-index: 9998;
    background: rgba(0,0,0,0.75);
    backdrop-filter: blur(6px);
    display: flex; align-items: flex-start; justify-content: center;
    padding-top: 5rem; overflow-y: auto;
}
.modal-box {
    background: #0f1117;
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 18px; width: 92%; max-width: 860px;
    padding: 2rem 2.2rem; position: relative;
    box-shadow: 0 24px 80px rgba(0,0,0,0.6);
    margin-bottom: 2rem;
}
.modal-close {
    position: absolute; top: 1.1rem; right: 1.3rem;
    background: rgba(255,255,255,0.06); border: none; cursor: pointer;
    color: #94a3b8; font-size: 1.1rem; width: 32px; height: 32px;
    border-radius: 6px; display: flex; align-items: center; justify-content: center;
    transition: 0.2s;
}
.modal-close:hover { background: rgba(255,255,255,0.12); color: #fff; }
.modal-route {
    font-size: 2rem; font-weight: 700; color: #fff;
    letter-spacing: -1px; margin-bottom: 0.3rem;
    display: flex; align-items: center; gap: 0.8rem;
}
.modal-arrow { color: #4f8ef7; font-size: 1.2rem; }
.modal-sub { font-size: 0.85rem; color: #64748b; margin-bottom: 1.5rem; }
.modal-sub strong { color: #94a3b8; }

.modal-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.modal-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; padding: 1.2rem 1.4rem;
}
.modal-card-title { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.9rem; font-weight: 600; }
.w-grid { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.w-item {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px; padding: 0.7rem 0.9rem; flex: 1; min-width: 80px; text-align: center;
}
.w-icon  { font-size: 1.1rem; margin-bottom: 0.2rem; }
.w-val   { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }
.w-lbl   { font-size: 0.6rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }

.score-row { display: flex; justify-content: space-between; align-items: center; padding: 0.45rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.82rem; }
.score-row:last-child { border-bottom: none; }
.score-name { color: #94a3b8; }
.score-bar  { flex-grow: 1; height: 4px; background: rgba(255,255,255,0.06); border-radius: 99px; margin: 0 0.8rem; }
.score-fill { height: 4px; border-radius: 99px; }
.score-num  { font-weight: 700; color: #e2e8f0; min-width: 28px; text-align: right; }

.modal-price { font-size: 2.2rem; font-weight: 700; color: #fff; letter-spacing: -1px; }
.modal-price span { font-size: 1rem; color: #64748b; }
.modal-price-tag { font-size: 0.68rem; color: #22c55e; font-weight: 600; text-transform: uppercase; margin-top: 3px; }
.modal-score-badge {
    padding: 0.6rem 1.2rem; border-radius: 10px;
    font-size: 1.8rem; font-weight: 700; color: white; text-align: center;
}
.modal-score-label { font-size: 0.55rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; opacity: 0.8; }

.fi-row { display: flex; justify-content: space-between; padding: 0.45rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.83rem; }
.fi-row:last-child { border-bottom: none; }
.fi-label { color: #64748b; }
.fi-value { color: #e2e8f0; font-weight: 500; }

/* ── FAVORITOS ── */
.fav-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; overflow: hidden;
    display: flex; align-items: stretch;
    margin-bottom: 2px; transition: 0.2s;
}
.fav-card:hover { border-color: rgba(251,191,36,0.25); background: rgba(255,255,255,0.04); }
.fav-accent { width: 3px; background: #f59e0b; flex-shrink: 0; }
.fav-body {
    padding: 16px 20px; flex-grow: 1;
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.8rem;
}
.fav-route { font-size: 1.4rem; font-weight: 700; color: #fff; letter-spacing: -0.5px; display: flex; align-items: center; gap: 0.5rem; }
.fav-arrow { color: #f59e0b; font-size: 1rem; }
.fav-meta  { font-size: 0.76rem; color: #64748b; margin-top: 3px; }
.fav-meta strong { color: #94a3b8; }
.fav-score { padding: 6px 12px; border-radius: 8px; font-size: 1rem; font-weight: 700; color: white; text-align: center; min-width: 64px; }
.fav-score-lbl { font-size: 0.45rem; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 2px; opacity: 0.8; }
.fav-price { font-size: 1.5rem; font-weight: 700; color: #fff; letter-spacing: -0.5px; }
.fav-price span { font-size: 0.8rem; color: #64748b; }
.fav-price-tag { font-size: 0.6rem; color: #22c55e; font-weight: 600; text-transform: uppercase; }

/* ── HOW CARDS ── */
.how-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; padding: 1.6rem 1.4rem; text-align: center;
}
.how-num   { font-size: 2rem; font-weight: 700; color: rgba(79,142,247,0.25); line-height: 1; margin-bottom: 0.4rem; }
.how-title { font-size: 1rem; font-weight: 600; color: #e2e8f0; margin-bottom: 0.4rem; }
.how-desc  { font-size: 0.83rem; color: #64748b; line-height: 1.6; }

/* ── AUTH FORM ── */
.auth-wrap { max-width: 420px; margin: 0 auto; padding-top: 1rem; }
.auth-title { font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: 0.2rem; }
.auth-sub   { font-size: 0.85rem; color: #64748b; margin-bottom: 2rem; }
div.stTextInput > label { color: #94a3b8 !important; font-size: 0.8rem !important; }
div.stTextInput > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 8px !important; color: #e2e8f0 !important;
}
div.stTextInput > div > input:focus {
    border-color: rgba(79,142,247,0.4) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.1) !important;
}

/* ── PAGE HEADER ── */
.page-hdr { border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 1.2rem; margin-bottom: 1.5rem; }
.page-hdr h2 { font-size: 1.4rem; font-weight: 700; color: #fff; margin: 0 0 0.2rem 0; }
.page-hdr p  { font-size: 0.83rem; color: #64748b; margin: 0; }

hr { border-color: rgba(255,255,255,0.06) !important; }

.empty-state { text-align: center; padding: 4rem 2rem; color: #374151; }
.empty-state .e-icon { font-size: 3rem; margin-bottom: 0.8rem; }
.empty-state h3 { font-size: 1.1rem; font-weight: 600; color: #4b5563; margin-bottom: 0.4rem; }
.empty-state p  { font-size: 0.85rem; color: #374151; max-width: 300px; margin: 0 auto; }

.faq-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px; padding: 0.9rem 1.2rem;
    margin-bottom: 0.5rem; color: #94a3b8; font-size: 0.87rem; line-height: 1.6;
}
.faq-item strong { color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  NAVBAR
# ─────────────────────────────────────────────
usuario_nombre = st.session_state["usuario"]
usuario_email  = st.session_state["usuario_email"]

if usuario_nombre:
    inicial = usuario_nombre[0].upper()
    nav_right = f'<div class="navbar-user"><div class="user-avatar">{inicial}</div><span style="color:#e2e8f0;font-weight:500">{usuario_nombre}</span></div>'
else:
    nav_right = '<div></div>'

st.markdown(f"""
<div class="navbar">
    <div class="navbar-logo">✈ Legion<span class="logo-accent">.</span>Flight</div>
    <div class="navbar-nav" id="navbar-nav"></div>
    {nav_right}
</div>
""", unsafe_allow_html=True)

# Botones de navegación en columnas
ncols = st.columns([1,1,1,1,1,2] if not usuario_nombre else [1,1,1,1,1,1,1])
with ncols[0]:
    if st.button("🔍 Buscar", key="nav_buscar"):
        st.session_state["vista"] = "inicio"
        st.session_state["modal_vuelo"] = None
        st.rerun()
with ncols[1]:
    if st.button("⚙️ Cómo funciona", key="nav_como"):
        st.session_state["vista"] = "inicio"
        st.session_state["modal_vuelo"] = None
        st.rerun()
with ncols[2]:
    if st.button("📩 Contacto", key="nav_contacto"):
        st.session_state["vista"] = "inicio"
        st.session_state["modal_vuelo"] = None
        st.rerun()
if usuario_nombre:
    with ncols[3]:
        if st.button("⭐ Favoritos", key="nav_favs"):
            st.session_state["vista"] = "favoritos"
            st.session_state["modal_vuelo"] = None
            st.rerun()
    with ncols[4]:
        if st.button("🚪 Salir", key="nav_logout"):
            st.session_state["usuario"] = None
            st.session_state["usuario_email"] = None
            st.session_state["favoritos"] = []
            st.session_state["vista"] = "inicio"
            st.session_state["modal_vuelo"] = None
            st.rerun()
else:
    with ncols[3]:
        if st.button("🔑 Acceder", key="nav_login"):
            st.session_state["vista"] = "login"
            st.session_state["modal_vuelo"] = None
            st.rerun()

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════
#  VISTA: LOGIN / REGISTRO
# ═══════════════════════════════════════════
if st.session_state["vista"] == "login":
    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)

    if "auth_tab" not in st.session_state:
        st.session_state["auth_tab"] = "login"

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 Iniciar sesión", key="tab_login", use_container_width=True):
            st.session_state["auth_tab"] = "login"
    with c2:
        if st.button("✨ Crear cuenta", key="tab_reg", use_container_width=True):
            st.session_state["auth_tab"] = "registro"

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    if st.session_state["auth_tab"] == "login":
        st.markdown('<div class="auth-title">Bienvenido de nuevo</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Inicia sesión para acceder a tus favoritos</div>', unsafe_allow_html=True)
        with st.form("form_login"):
            email_l = st.text_input("Correo electrónico", placeholder="tu@email.com")
            pass_l  = st.text_input("Contraseña", type="password", placeholder="••••••••")
            ok_l    = st.form_submit_button("Entrar →")
        if ok_l:
            if not email_l or not pass_l:
                st.error("Rellena todos los campos.")
            else:
                exito, res = do_login(email_l, pass_l)
                if exito:
                    st.session_state["usuario"]       = res["nombre"]
                    st.session_state["usuario_email"] = email_l
                    st.session_state["favoritos"]     = res.get("favoritos", [])
                    st.session_state["vista"]         = "inicio"
                    st.success(f"✅ ¡Bienvenido, {res['nombre']}!")
                    st.rerun()
                else:
                    st.error(res)
    else:
        st.markdown('<div class="auth-title">Crear cuenta</div>', unsafe_allow_html=True)
        st.markdown('<div class="auth-sub">Regístrate gratis para guardar tus vuelos favoritos</div>', unsafe_allow_html=True)
        with st.form("form_registro"):
            nombre_r = st.text_input("Nombre", placeholder="Tu nombre")
            email_r  = st.text_input("Correo electrónico", placeholder="tu@email.com")
            pass_r   = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            conf_r   = st.text_input("Confirmar contraseña", type="password")
            ok_r     = st.form_submit_button("Crear cuenta →")
        if ok_r:
            if not nombre_r or not email_r or not pass_r or not conf_r:
                st.error("Rellena todos los campos.")
            elif len(pass_r) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
            elif pass_r != conf_r:
                st.error("Las contraseñas no coinciden.")
            elif "@" not in email_r:
                st.error("Introduce un email válido.")
            else:
                exito, res = do_register(nombre_r, email_r, pass_r)
                if exito:
                    st.success("✅ Cuenta creada. Ahora inicia sesión.")
                    st.session_state["auth_tab"] = "login"
                    st.rerun()
                else:
                    st.error(res)

    st.markdown("---")
    if st.button("← Volver al inicio", use_container_width=True):
        st.session_state["vista"] = "inicio"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═══════════════════════════════════════════
#  VISTA: FAVORITOS
# ═══════════════════════════════════════════
if st.session_state["vista"] == "favoritos":
    if not st.session_state["usuario"]:
        st.warning("Debes iniciar sesión para ver tus favoritos.")
        if st.button("🔑 Iniciar sesión"):
            st.session_state["vista"] = "login"
            st.rerun()
        st.stop()

    favoritos = st.session_state.get("favoritos", [])

    st.markdown(f"""
    <div class="page-hdr">
        <h2>⭐ Mis favoritos</h2>
        <p>Hola, <strong style="color:#e2e8f0">{st.session_state["usuario"]}</strong> · {len(favoritos)} vuelo{"s" if len(favoritos) != 1 else ""} guardado{"s" if len(favoritos) != 1 else ""}</p>
    </div>
    """, unsafe_allow_html=True)

    if not favoritos:
        st.markdown("""
        <div class="empty-state">
            <div class="e-icon">🔍</div>
            <h3>Sin favoritos todavía</h3>
            <p>Busca vuelos y pulsa "☆ Favorito" para guardarlos aquí.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔍 Buscar vuelos", use_container_width=True):
            st.session_state["vista"] = "inicio"
            st.rerun()
    else:
        ch, cc = st.columns([4, 1])
        with cc:
            if st.button("🗑️ Limpiar todo", use_container_width=True):
                limpiar_favoritos_db(usuario_email)
                st.session_state["favoritos"] = []
                st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        for i, fav in enumerate(favoritos):
            v = fav["vuelo"]
            st.markdown(
                f'<div class="fav-card">'
                f'<div class="fav-accent"></div>'
                f'<div class="fav-body">'
                f'<div><div class="fav-route">{fav["iata_origen"]}<span class="fav-arrow">✈</span>{fav["iata_destino"]}</div>'
                f'<div class="fav-meta"><strong>{fav["origen"]}</strong> → <strong>{fav["destino"]}</strong> &nbsp;·&nbsp; {fav["fecha"]} &nbsp;·&nbsp; {v["hora_salida"]} &nbsp;·&nbsp; {v["linea"]}</div></div>'
                f'<div class="fav-score" style="background:{fav["color_nota"]}">{fav["nota_final"]:.1f}<div class="fav-score-lbl">{fav["etiqueta"]}</div></div>'
                f'<div><div class="fav-price">{fav["precio_vuelo"]}<span>€</span></div><div class="fav-price-tag">Estimado</div></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
            cf1, cf2 = st.columns([3, 1])
            with cf1:
                if st.button("Ver detalle →", key=f"fav_ver_{i}"):
                    st.session_state["modal_vuelo"] = fav
                    st.session_state["vista"] = "inicio"
                    st.rerun()
            with cf2:
                if st.button("🗑️ Eliminar", key=f"fav_del_{i}"):
                    eliminar_favorito_db(usuario_email, i)
                    st.session_state["favoritos"].pop(i)
                    st.rerun()
            st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("← Volver al inicio", use_container_width=True):
        st.session_state["vista"] = "inicio"
        st.rerun()
    st.stop()


# ═══════════════════════════════════════════
#  VISTA: INICIO (hero + buscador + resultados)
# ═══════════════════════════════════════════

# ─── HERO ───
st.markdown(f"""
<div class="hero">
    <img src="data:image/jpeg;base64,{imagen_fondo_64}" alt="Avión en vuelo">
    <div class="hero-content">
        <h1>Descubre cómo será<br>tu vuelo <em>antes</em> de despegar</h1>
        <p>Conoce las condiciones meteorológicas en origen y destino antes de embarcar.</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ─── BUSCADOR ───
st.markdown('<div class="search-section">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
with col1:
    origen = st.selectbox("🛫 Origen", options=list(CIUDADES_IATA.keys()), index=0, key="origen_select")
with col2:
    destino = st.selectbox("🛬 Destino", options=list(CIUDADES_IATA.keys()), index=1, key="destino_select")
with col3:
    fecha = st.date_input("📅 Fecha", value=available_dates[0], min_value=available_dates[0], max_value=available_dates[-1], key="fecha_salida")
with col4:
    buscar = st.button("🔍 Buscar vuelos", key="btn_buscar")
st.markdown('</div>', unsafe_allow_html=True)


# ─── RESULTADOS ───
if buscar:
    if origen == destino:
        st.error("Origen y destino no pueden ser iguales.")
    else:
        vuelos_reales = buscar_programacion_comercial(origen, destino)
        if not vuelos_reales:
            st.warning("No se encontraron vuelos programados.")
        else:
            precio_ruta  = obtener_precio_estimado(origen, destino)
            iata_origen  = CIUDADES_IATA[origen]
            iata_destino = CIUDADES_IATA[destino]

            for v in vuelos_reales:
                partes = v["hora_salida"].split(":")
                v["h_sort"] = int(partes[0]); v["m_sort"] = int(partes[1])
            vuelos_reales = sorted(vuelos_reales, key=lambda x: (x["h_sort"], x["m_sort"]))

            st.markdown(
                f'<div class="results-header"><span>{len(vuelos_reales)}</span> vuelos · {iata_origen} → {iata_destino} · {fecha}</div>',
                unsafe_allow_html=True
            )

            for idx, vuelo in enumerate(vuelos_reales):
                w_orig = get_weather_at(df_weather, origen, fecha, vuelo["hora_int"])
                w_dest = get_weather_at(df_weather, destino, fecha, (vuelo["hora_int"] + 1) % 24)

                if w_orig and w_dest:
                    datos_o = {
                        "temperature":   w_orig.get("temperature", 20),
                        "wind_speed":    w_orig.get("windspeed", w_orig.get("wind_speed", 0)),
                        "precipitation": w_orig.get("precipitation", 0),
                    }
                    datos_d = {
                        "temperature":   w_dest.get("temperature", 20),
                        "wind_speed":    w_dest.get("windspeed", w_dest.get("wind_speed", 0)),
                        "precipitation": w_dest.get("precipitation", 0),
                    }
                    result       = score_flight(datos_o, datos_d)
                    nota_final   = result.get("rating", 0.0)
                    etiqueta     = result.get("label", "Malo")
                    color_nota   = result.get("color", "#dc3545")
                    precio_vuelo = precio_ruta + random.randint(-10, 15)

                    temp_o = datos_o["temperature"]; temp_d = datos_d["temperature"]
                    nota_str = f"{nota_final:.1f}"
                    html_card = (
                        '<div class="flight-card">'
                            '<div class="flight-main-content">'
                                '<div>'
                                    '<div class="flight-time">' + vuelo["hora_salida"] + '</div>'
                                    '<div class="flight-airline">' + vuelo["linea"] + '</div>'
                                    '<div class="flight-number">' + vuelo["vuelo"] + '</div>'
                                '</div>'
                                '<div class="flight-route">'
                                    '<div class="route-inner">'
                                        '<span class="iata">' + iata_origen + '</span>'
                                        '<div class="route-line"><span class="plane-icon">✈</span></div>'
                                        '<span class="iata">' + iata_destino + '</span>'
                                    '</div>'
                                    '<div class="route-temps">🌡️ ' + str(temp_o) + '°C → ' + str(temp_d) + '°C</div>'
                                '</div>'
                                '<div class="rating-wrap">'
                                    '<div class="rating-box" style="background:' + color_nota + '">'
                                        + nota_str +
                                        '<div class="rating-label">' + etiqueta + '</div>'
                                    '</div>'
                                '</div>'
                            '</div>'
                            '<div class="flight-price-section">'
                                '<div class="price-value">' + str(precio_vuelo) + '<span class="price-currency">€</span></div>'
                                '<div class="price-tag">Estimado</div>'
                            '</div>'
                        '</div>'
                    )
                    st.markdown(html_card, unsafe_allow_html=True)

                    # Botones debajo de cada card
                    cd, cf = st.columns([3, 1])
                    vuelo_data = {
                        "vuelo": vuelo, "origen": origen, "destino": destino,
                        "iata_origen": iata_origen, "iata_destino": iata_destino,
                        "fecha": str(fecha), "datos_o": datos_o, "datos_d": datos_d,
                        "nota_final": nota_final, "etiqueta": etiqueta,
                        "color_nota": color_nota, "precio_vuelo": precio_vuelo,
                        "score_detail": result,
                    }
                    with cd:
                        if st.button("Ver detalle →", key=f"det_{idx}"):
                            st.session_state["modal_vuelo"] = vuelo_data
                            st.rerun()
                    with cf:
                        ya_fav = any(
                            f.get("vuelo", {}).get("vuelo") == vuelo["vuelo"]
                            for f in st.session_state.get("favoritos", [])
                        )
                        lbl = "⭐ Guardado" if ya_fav else "☆ Favorito"
                        if st.button(lbl, key=f"fav_{idx}"):
                            if not st.session_state["usuario"]:
                                st.warning("Inicia sesión para guardar favoritos.")
                            elif not ya_fav:
                                guardar_favorito_db(usuario_email, vuelo_data)
                                st.session_state["favoritos"].append(vuelo_data)
                                st.success(f"✅ Vuelo {vuelo['vuelo']} guardado")
                    st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)


# ─── COMO FUNCIONA ───
st.markdown("---")
st.markdown("## ⚙️ Cómo funciona")
st.markdown("<br>", unsafe_allow_html=True)
ca, cb, cc_col = st.columns(3)
for col, n, t, d in [
    (ca, "01", "Busca tu vuelo", "Selecciona origen, destino y fecha para ver los vuelos disponibles."),
    (cb, "02", "Analiza condiciones", "Temperatura, viento y precipitación en origen y destino."),
    (cc_col, "03", "Decide con datos", "Elige el horario con mejores condiciones y guarda tus favoritos."),
]:
    with col:
        st.markdown(f'<div class="how-card"><div class="how-num">{n}</div><div class="how-title">{t}</div><div class="how-desc">{d}</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("## 📩 Contacto")
st.markdown('<p style="color:#64748b">¿Tienes dudas? Escríbenos a <strong style="color:#4f8ef7">contacto@legionflight.com</strong></p>', unsafe_allow_html=True)
st.markdown("---")
st.markdown("## ❓ FAQ")
for p, r in [
    ("¿De dónde salen los datos?", "Del servicio meteorológico Open-Meteo, actualizado cada hora."),
    ("¿Qué variables se analizan?", "Temperatura, velocidad del viento y precipitación en origen y destino."),
    ("¿Puedo ver previsión a más de 7 días?", "De momento cubrimos los próximos 7 días naturales."),
    ("¿Los precios son exactos?", "Los precios mostrados son estimaciones orientativas, no vinculantes."),
]:
    st.markdown(f'<div class="faq-item"><strong>{p}</strong><br>{r}</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#374151;font-size:0.78rem">© 2025 Legion Flight</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════
#  MODAL DE DETALLE — se renderiza ENCIMA de todo
# ═══════════════════════════════════════════
if st.session_state.get("modal_vuelo"):
    d = st.session_state["modal_vuelo"]
    vuelo        = d["vuelo"]
    origen       = d["origen"]
    destino      = d["destino"]
    iata_origen  = d["iata_origen"]
    iata_destino = d["iata_destino"]
    fecha        = d["fecha"]
    datos_o      = d["datos_o"]
    datos_d      = d["datos_d"]
    nota_final   = d["nota_final"]
    etiqueta     = d["etiqueta"]
    color_nota   = d["color_nota"]
    precio_vuelo = d["precio_vuelo"]

    # Backdrop oscuro con blur via CSS
    st.markdown("""
    <style>
    /* Bloquear scroll del fondo y mostrar backdrop */
    body { overflow: hidden !important; }
    [data-testid="stAppViewContainer"] > .main > .block-container {
        filter: blur(3px) brightness(0.4);
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="modal-backdrop">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="modal-box">
        <div class="modal-route">
            {iata_origen}
            <span class="modal-arrow">✈</span>
            {iata_destino}
            <div class="modal-score-badge" style="background:{color_nota};margin-left:auto">
                {nota_final:.1f}
                <div class="modal-score-label">{etiqueta}</div>
            </div>
        </div>
        <div class="modal-sub">
            <strong>{origen}</strong> → <strong>{destino}</strong>
            &nbsp;·&nbsp; {fecha}
            &nbsp;·&nbsp; Salida <strong>{vuelo['hora_salida']}</strong>
            &nbsp;·&nbsp; {vuelo['linea']} · {vuelo['vuelo']}
        </div>

        <div class="modal-grid">
            <div class="modal-card">
                <div class="modal-card-title">🛫 Clima en origen · {origen}</div>
                <div class="w-grid">
                    <div class="w-item"><div class="w-icon">🌡️</div><div class="w-val">{datos_o['temperature']}°C</div><div class="w-lbl">Temperatura</div></div>
                    <div class="w-item"><div class="w-icon">💨</div><div class="w-val">{datos_o['wind_speed']} km/h</div><div class="w-lbl">Viento</div></div>
                    <div class="w-item"><div class="w-icon">🌧️</div><div class="w-val">{datos_o['precipitation']} mm</div><div class="w-lbl">Precipitación</div></div>
                </div>
            </div>
            <div class="modal-card">
                <div class="modal-card-title">🛬 Clima en destino · {destino}</div>
                <div class="w-grid">
                    <div class="w-item"><div class="w-icon">🌡️</div><div class="w-val">{datos_d['temperature']}°C</div><div class="w-lbl">Temperatura</div></div>
                    <div class="w-item"><div class="w-icon">💨</div><div class="w-val">{datos_d['wind_speed']} km/h</div><div class="w-lbl">Viento</div></div>
                    <div class="w-item"><div class="w-icon">🌧️</div><div class="w-val">{datos_d['precipitation']} mm</div><div class="w-lbl">Precipitación</div></div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Desglose de puntuación + info vuelo dentro del modal
    criterios = {
        "Temperatura origen":    min(max(datos_o["temperature"], 0) / 40, 1.0),
        "Viento origen":         max(0, 1 - datos_o["wind_speed"] / 100),
        "Precipitación origen":  max(0, 1 - datos_o["precipitation"] / 20),
        "Temperatura destino":   min(max(datos_d["temperature"], 0) / 40, 1.0),
        "Viento destino":        max(0, 1 - datos_d["wind_speed"] / 100),
        "Precipitación destino": max(0, 1 - datos_d["precipitation"] / 20),
    }
    barras = ""
    for nombre, valor in criterios.items():
        pct = int(valor * 100)
        col = "#22c55e" if pct >= 70 else ("#f59e0b" if pct >= 40 else "#ef4444")
        barras += (
            f'<div class="score-row">'
            f'<span class="score-name">{nombre}</span>'
            f'<div class="score-bar"><div class="score-fill" style="width:{pct}%;background:{col}"></div></div>'
            f'<span class="score-num">{pct}</span>'
            f'</div>'
        )

    st.markdown(f"""
        <div class="modal-grid">
            <div class="modal-card">
                <div class="modal-card-title">📊 Desglose de puntuación</div>
                {barras}
            </div>
            <div class="modal-card">
                <div class="modal-card-title">✈️ Información del vuelo</div>
                <div class="fi-row"><span class="fi-label">Aerolínea</span><span class="fi-value">{vuelo['linea']}</span></div>
                <div class="fi-row"><span class="fi-label">Número</span><span class="fi-value">{vuelo['vuelo']}</span></div>
                <div class="fi-row"><span class="fi-label">Hora salida</span><span class="fi-value">{vuelo['hora_salida']}</span></div>
                <div class="fi-row"><span class="fi-label">Origen</span><span class="fi-value">{origen}</span></div>
                <div class="fi-row"><span class="fi-label">Destino</span><span class="fi-value">{destino}</span></div>
                <div class="fi-row"><span class="fi-label">Fecha</span><span class="fi-value">{fecha}</span></div>
            </div>
        </div>

        <div class="modal-card" style="display:flex;align-items:center;justify-content:space-between;margin-top:0">
            <div>
                <div class="modal-card-title">💶 Precio estimado</div>
                <div class="modal-price">{precio_vuelo}<span>€</span></div>
                <div class="modal-price-tag">Precio orientativo · No vinculante</div>
            </div>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    # Botones del modal con Streamlit (para que funcionen los callbacks)
    mc1, mc2, mc3 = st.columns([2, 2, 1])
    with mc1:
        if st.button("✕ Cerrar detalle", key="modal_close", use_container_width=True):
            st.session_state["modal_vuelo"] = None
            st.rerun()
    with mc2:
        ya_fav = any(
            f.get("vuelo", {}).get("vuelo") == vuelo["vuelo"]
            for f in st.session_state.get("favoritos", [])
        )
        if ya_fav:
            st.button("⭐ Ya en favoritos", disabled=True, use_container_width=True)
        else:
            if st.button("☆ Guardar en favoritos", key="modal_fav", use_container_width=True):
                if not st.session_state["usuario"]:
                    st.warning("Inicia sesión para guardar favoritos.")
                else:
                    guardar_favorito_db(usuario_email, d)
                    st.session_state["favoritos"].append(d)
                    st.success("✅ Guardado en favoritos")
                    st.rerun()
    with mc3:
        st.button("🎫 Reservar", key="modal_reservar", use_container_width=True)
