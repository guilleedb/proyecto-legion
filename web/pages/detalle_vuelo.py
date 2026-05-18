import streamlit as st
import os
import sys

# ─── PATH SETUP ────────────────────────────────────────────────────────────────
current_dir  = os.path.dirname(os.path.abspath(__file__))
web_dir      = os.path.abspath(os.path.join(current_dir, ".."))
project_root = os.path.abspath(os.path.join(web_dir, ".."))
src_path     = os.path.join(project_root, "src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

from flight_scoring import score_wind, score_precipitation, score_temperature
from ayuda_weather import degrees_to_compass

st.set_page_config(page_title="Detalle de vuelo · Legion Flight", layout="wide")

# ─── CSS + NAVBAR ──────────────────────────────────────────────────────────────
# st.markdown (string estático, sin f-string) → el procesador Markdown no interfiere
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Syne', sans-serif; }

    #MainMenu {visibility: hidden;}
    footer     {visibility: hidden;}
    header     {visibility: hidden;}
    [data-testid="stSidebar"]        { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stAppViewContainer"] { background-color: #06080f; }
    .block-container { padding-top: 4.5rem !important; }

    .navbar {
        position: fixed; top: 0; left: 0; width: 100%; z-index: 9999;
        background-color: #0e1117; border-bottom: 1px solid #2e2e2e;
        display: flex; align-items: center; padding: 0.6rem 2rem; box-sizing: border-box;
    }
    .navbar-logo { font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 700; color: #fff; }

    div.stButton > button {
        background-color: #2563eb !important; color: white !important;
        font-weight: 700 !important; border-radius: 8px !important;
        border: none !important; transition: all 0.2s ease;
        padding: 0.5rem 1.2rem !important;
    }
    div.stButton > button:hover {
        background-color: #1d4ed8 !important;
        box-shadow: 0 4px 12px rgba(37,99,235,0.3);
    }
</style>
<div class="navbar">
    <div class="navbar-logo">✈️ Legion Flight</div>
</div>
""", unsafe_allow_html=True)

# ─── SESSION STATE ──────────────────────────────────────────────────────────────
v = st.session_state.get("vuelo_seleccionado")

if not v:
    st.error("No hay ningún vuelo seleccionado. Vuelve a la búsqueda y pulsa 'Ver detalle'.")
    if st.button("Volver a resultados", key="volver_error"):
        st.switch_page("app.py")
    st.stop()

# ─── CÁLCULO DE SCORES ─────────────────────────────────────────────────────────
sv_o = score_wind(v["viento_orig"])
sp_o = score_precipitation(v["precip_orig"])
st_o = score_temperature(v["temp_orig"])

sv_d = score_wind(v["viento_dest"])
sp_d = score_precipitation(v["precip_dest"])
st_d = score_temperature(v["temp_dest"])

score_orig  = sv_o * 0.45 + sp_o * 0.40 + st_o * 0.15
score_dest  = sv_d * 0.45 + sp_d * 0.40 + st_d * 0.15
score_final = min(score_orig, score_dest)

sv_avg = (sv_o + sv_d) / 2
sp_avg = (sp_o + sp_d) / 2
st_avg = (st_o + st_d) / 2

# ─── HELPERS ───────────────────────────────────────────────────────────────────
def bar_color(s):
    if s >= 80: return "#28a745"
    if s >= 55: return "#ffc107"
    return "#dc3545"

def precip_label(mm):
    if mm == 0:    return "Sin lluvia"
    if mm <= 1:    return "Ligera"
    if mm <= 5:    return "Moderada"
    return "Intensa"

def estado_color(estado):
    tabla = {
        "scheduled": ("background:#2563eb;color:#dbeafe;",),
        "active":    ("background:#15803d;color:#dcfce7;",),
        "landed":    ("background:#374151;color:#f3f4f6;",),
        "cancelled": ("background:#dc2626;color:#fee2e2;",),
        "incident":  ("background:#92400e;color:#fef3c7;",),
        "diverted":  ("background:#2563eb;color:#ede9fe;",),
    }
    entry = tabla.get(str(estado).lower())
    return entry[0] if entry else "background:#374151;color:#f3f4f6;"

def recomendacion(nota):
    if nota >= 9.0:
        return "#14532d", "rgba(20,83,45,0.25)", "Condiciones excepcionales", \
               "Mínimas turbulencias esperadas, buena visibilidad y temperaturas confortables en ambos aeropuertos. Es un momento ideal para volar."
    if nota >= 7.5:
        return "#1e3a5f", "rgba(30,58,95,0.25)", "Buenas condiciones", \
               "El trayecto debería transcurrir con normalidad. Las condiciones meteorológicas son favorables en origen y destino."
    if nota >= 5.5:
        return "#78350f", "rgba(120,53,15,0.25)", "Condiciones moderadas", \
               "Es posible que haya algo de turbulencia o lluvia ligera. Llega con tiempo y consulta el estado del vuelo antes de salir."
    return "#7f1d1d", "rgba(127,29,29,0.25)", "Condiciones adversas", \
           "Se detectan condiciones desfavorables en alguno de los aeropuertos. Consulta el estado actualizado y contacta con la aerolínea si tienes dudas."

# ─── VARIABLES DERIVADAS ────────────────────────────────────────────────────────
precio_str   = f"~{v['precio']} euro" if isinstance(v.get("precio"), int) else "-"
compass_o    = degrees_to_compass(v["dir_orig"])
compass_d    = degrees_to_compass(v["dir_dest"])
pl_o         = precip_label(v["precip_orig"])
pl_d         = precip_label(v["precip_dest"])
estado_css   = estado_color(v["estado"])
rc_b, rc_bg, rc_title, rc_text = recomendacion(v["nota"])

# ─── BOTÓN VOLVER ──────────────────────────────────────────────────────────────
if st.button("Volver a resultados", key="volver_top"):
    st.switch_page("app.py")

# ─── SECCIÓN 1: CABECERA ───────────────────────────────────────────────────────
# Usamos st.html() para evitar que el procesador Markdown interfiera con el HTML dinámico
st.html(f"""
<div style="
    background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 4px solid #2563eb;
    border-radius: 16px;
    padding: 28px 32px;
    color: #e8eaf0;
    margin-bottom: 16px;
    margin-top: 12px;
">
    <div style="display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:24px;">

        <div>
            <div style="font-size:0.75rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:6px;">Vuelo</div>
            <div style="font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:800; color:white; line-height:1.1;">
                {v["iata_orig"]} &#8594; {v["iata_dest"]}
            </div>
            <div style="font-size:1rem; color:#9ca3af; margin-top:4px;">
                {v["origen"]} &#8594; {v["destino"]}
            </div>
        </div>

        <div style="text-align:center;">
            <div style="font-size:0.75rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:4px;">Hora salida</div>
            <div style="font-family:'Syne',sans-serif; font-size:2rem; font-weight:800; color:white;">{v["hora_salida"]}</div>
            <div style="font-size:0.8rem; color:#6b7280;">{v["fecha"]}</div>
        </div>

        <div style="text-align:center;">
            <div style="font-size:0.75rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:4px;">Aerolinea</div>
            <div style="font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700; color:white; line-height:1.1;">{v["linea"]}</div>
            <div style="font-size:0.85rem; color:#9ca3af; margin-top:4px;">{v["vuelo"]}</div>
        </div>

        <div style="text-align:center;">
            <div style="font-size:0.75rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px;">Estado</div>
            <span style="display:inline-block; padding:4px 14px; border-radius:20px; font-size:0.78rem; font-weight:600; {estado_css}">{v["estado"]}</span>
        </div>

        <div style="text-align:center;">
            <div style="font-size:0.75rem; color:#6b7280; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:4px;">Precio estimado</div>
            <div style="font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:700; color:white; line-height:1.1;">{precio_str}</div>
            <div style="font-size:0.7rem; color:#6b7280;">estimacion sin garantia</div>
        </div>

    </div>
</div>
""")

# ─── SECCIÓN 2: RATING + CLIMA ─────────────────────────────────────────────────
col_rating, col_orig, col_dest = st.columns([1, 1, 1])

CARD = "background:linear-gradient(135deg,#0d1117 0%,#111827 100%);border:1px solid rgba(255,255,255,0.07);border-left:4px solid #2563eb;border-radius:16px;padding:24px 28px;color:#e8eaf0;height:100%;"
BAR_BG = "background:rgba(255,255,255,0.07);border-radius:6px;height:8px;margin:6px 0 14px 0;overflow:hidden;"

def bar(pct, color):
    return f'<div style="{BAR_BG}"><div style="height:100%;border-radius:6px;width:{pct:.0f}%;background:{color};"></div></div>'

def stat_row(label, value):
    return f'''<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.05);">
        <span style="color:#6b7280;font-size:0.85rem;">{label}</span>
        <span style="color:#e8eaf0;font-weight:600;font-size:0.95rem;">{value}</span>
    </div>'''

def score_row(label, val):
    return f'''<div style="display:flex;justify-content:space-between;font-size:0.8rem;margin-bottom:4px;">
        <span style="color:#9ca3af;">{label}</span>
        <span style="color:#e8eaf0;">{val:.0f}/100</span>
    </div>{bar(val, bar_color(val))}'''

with col_rating:
    st.html(f"""
    <div style="{CARD}">
        <div style="font-size:0.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:16px;">Rating meteorologico</div>

        <div style="text-align:center;margin-bottom:24px;">
            <div style="font-family:'Syne',sans-serif;font-size:3.5rem;font-weight:800;color:{v["color"]};line-height:1;">{v["nota"]:.1f}</div>
            <div style="font-size:1rem;font-weight:600;color:#e8eaf0;margin-top:4px;">{v["etiqueta"]}</div>
            <div style="font-size:0.75rem;color:#6b7280;margin-top:2px;">sobre 10 · peor de los dos aeropuertos</div>
        </div>

        <div style="font-size:0.75rem;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:10px;">Desglose de factores</div>

        <div style="display:flex;justify-content:space-between;font-size:0.82rem;">
            <span style="color:#9ca3af;">Viento <span style="color:#6b7280;font-size:0.7rem;">(45%)</span></span>
            <span style="color:#e8eaf0;font-weight:600;">{sv_avg:.0f}/100</span>
        </div>
        {bar(sv_avg, bar_color(sv_avg))}

        <div style="display:flex;justify-content:space-between;font-size:0.82rem;">
            <span style="color:#9ca3af;">Precipitacion <span style="color:#6b7280;font-size:0.7rem;">(40%)</span></span>
            <span style="color:#e8eaf0;font-weight:600;">{sp_avg:.0f}/100</span>
        </div>
        {bar(sp_avg, bar_color(sp_avg))}

        <div style="display:flex;justify-content:space-between;font-size:0.82rem;">
            <span style="color:#9ca3af;">Temperatura <span style="color:#6b7280;font-size:0.7rem;">(15%)</span></span>
            <span style="color:#e8eaf0;font-weight:600;">{st_avg:.0f}/100</span>
        </div>
        {bar(st_avg, bar_color(st_avg))}

        <div style="margin-top:16px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.06);display:flex;justify-content:space-between;font-size:0.8rem;">
            <div style="text-align:center;">
                <div style="color:#6b7280;">Score {v["iata_orig"]}</div>
                <div style="color:#e8eaf0;font-weight:700;font-size:1rem;">{score_orig:.0f}</div>
            </div>
            <div style="text-align:center;">
                <div style="color:#6b7280;">Score {v["iata_dest"]}</div>
                <div style="color:#e8eaf0;font-weight:700;font-size:1rem;">{score_dest:.0f}</div>
            </div>
            <div style="text-align:center;">
                <div style="color:#6b7280;">Score final</div>
                <div style="color:{v["color"]};font-weight:700;font-size:1rem;">{score_final:.0f}</div>
            </div>
        </div>
    </div>
    """)

with col_orig:
    st.html(f"""
    <div style="{CARD}">
        <div style="font-size:0.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">Clima en origen</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:white;margin-bottom:20px;">
            {v["origen"]} ({v["iata_orig"]})
        </div>

        {stat_row("Temperatura", f'{v["temp_orig"]} C')}
        {stat_row("Viento", f'{v["viento_orig"]} km/h')}
        {stat_row("Direccion del viento", f'{compass_o} ({int(v["dir_orig"])})')}
        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;">
            <span style="color:#6b7280;font-size:0.85rem;">Precipitacion</span>
            <span style="color:#e8eaf0;font-weight:600;font-size:0.95rem;">{v["precip_orig"]} mm — {pl_o}</span>
        </div>

        <div style="margin-top:20px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.06);">
            <div style="font-size:0.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:10px;">Puntuacion por factor</div>
            {score_row("Viento", sv_o)}
            {score_row("Precipitacion", sp_o)}
            {score_row("Temperatura", st_o)}
        </div>
    </div>
    """)

with col_dest:
    st.html(f"""
    <div style="{CARD}">
        <div style="font-size:0.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px;">Clima en destino</div>
        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:white;margin-bottom:20px;">
            {v["destino"]} ({v["iata_dest"]})
        </div>

        {stat_row("Temperatura", f'{v["temp_dest"]} C')}
        {stat_row("Viento", f'{v["viento_dest"]} km/h')}
        {stat_row("Direccion del viento", f'{compass_d} ({int(v["dir_dest"])})')}
        <div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;">
            <span style="color:#6b7280;font-size:0.85rem;">Precipitacion</span>
            <span style="color:#e8eaf0;font-weight:600;font-size:0.95rem;">{v["precip_dest"]} mm — {pl_d}</span>
        </div>

        <div style="margin-top:20px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.06);">
            <div style="font-size:0.75rem;color:#6b7280;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:10px;">Puntuacion por factor</div>
            {score_row("Viento", sv_d)}
            {score_row("Precipitacion", sp_d)}
            {score_row("Temperatura", st_d)}
        </div>
    </div>
    """)

# ─── SECCIÓN 3: RECOMENDACIÓN ──────────────────────────────────────────────────
st.html(f"""
<div style="border-radius:14px;padding:24px 28px;border:1px solid {rc_b};background:{rc_bg};margin-top:8px;">
    <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:white;margin-bottom:8px;">
        Recomendacion — {rc_title}
    </div>
    <div style="color:#d1d5db;font-size:0.92rem;line-height:1.7;">{rc_text}</div>
    <div style="margin-top:12px;font-size:0.75rem;color:#6b7280;">
        Score final: peor valor entre origen y destino (criterio conservador).
        Factores: viento (45%), precipitacion (40%), temperatura (15%).
        El precio es una estimacion basada en ruta, hora y aerolinea.
    </div>
</div>
""")

st.markdown("")
if st.button("Volver a resultados", key="volver_bottom"):
    st.switch_page("app.py")
