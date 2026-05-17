import streamlit as st

# ─────────────────────────────────────────────
#  NOTA: El detalle del vuelo ahora se muestra como
#  modal/overlay directamente en app.py al pulsar
#  "Ver detalle →". Esta página sirve de respaldo
#  por si se navega directamente a ella.
# ─────────────────────────────────────────────

st.set_page_config(page_title="Detalle del vuelo · Legion Flight", layout="wide")

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
.block-container { padding-top: 4rem !important; }

.navbar {
    position: fixed; top: 0; left: 0; width: 100%; z-index: 9000;
    background: rgba(10,10,15,0.92); backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.8rem 2.5rem;
}
.navbar-logo { font-size: 1.1rem; font-weight: 700; color: #fff; }
.logo-accent { color: #4f8ef7; }

.detail-hero {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px; padding: 2rem 2.4rem;
    margin-bottom: 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
}
.detail-route { font-size: 2.4rem; font-weight: 700; color: #fff; letter-spacing: -1px; display: flex; align-items: center; gap: 0.8rem; }
.detail-arrow { color: #4f8ef7; font-size: 1.4rem; }
.detail-sub   { font-size: 0.85rem; color: #64748b; margin-top: 0.4rem; }
.detail-sub strong { color: #94a3b8; }
.detail-badge {
    padding: 0.8rem 1.5rem; border-radius: 12px;
    font-size: 2rem; font-weight: 700; color: white; text-align: center; min-width: 110px;
}
.detail-badge-lbl { font-size: 0.55rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px; opacity: 0.8; }

.info-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; padding: 1.3rem 1.5rem; margin-bottom: 1rem;
}
.info-card h3 { margin: 0 0 1rem 0; font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; }

.w-grid { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.w-item { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 0.7rem 0.9rem; flex: 1; min-width: 80px; text-align: center; }
.w-icon  { font-size: 1.1rem; margin-bottom: 0.2rem; }
.w-val   { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }
.w-lbl   { font-size: 0.6rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }

.score-row { display: flex; justify-content: space-between; align-items: center; padding: 0.45rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.82rem; }
.score-row:last-child { border-bottom: none; }
.score-name { color: #94a3b8; }
.score-bar  { flex-grow: 1; height: 4px; background: rgba(255,255,255,0.06); border-radius: 99px; margin: 0 0.8rem; }
.score-fill { height: 4px; border-radius: 99px; }
.score-num  { font-weight: 700; color: #e2e8f0; min-width: 28px; text-align: right; }

.fi-row { display: flex; justify-content: space-between; padding: 0.45rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); font-size: 0.83rem; }
.fi-row:last-child { border-bottom: none; }
.fi-label { color: #64748b; }
.fi-value { color: #e2e8f0; font-weight: 500; }

.price-big { font-size: 2.8rem; font-weight: 700; color: #fff; letter-spacing: -1.5px; line-height: 1; }
.price-big span { font-size: 1.2rem; color: #64748b; }
.price-tag { font-size: 0.65rem; color: #22c55e; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 0.3rem; }

.fav-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25);
    border-radius: 6px; padding: 0.35rem 0.8rem;
    color: #f59e0b; font-size: 0.78rem; font-weight: 600; margin-bottom: 0.8rem;
}

div.stButton > button {
    width: 100% !important; height: 3em !important;
    background: #1e3a5f !important; color: #93c5fd !important; font-weight: 600 !important;
    border-radius: 8px !important; border: 1px solid rgba(79,142,247,0.25) !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.88rem !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover { background: #1e4080 !important; border-color: rgba(79,142,247,0.5) !important; }
hr { border-color: rgba(255,255,255,0.06) !important; }
</style>

<div class="navbar">
    <div class="navbar-logo">✈ Legion<span class="logo-accent">.</span>Flight</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  GUARD
# ─────────────────────────────────────────────
if "modal_vuelo" not in st.session_state or not st.session_state["modal_vuelo"]:
    st.warning("No hay ningún vuelo seleccionado.")
    if st.button("← Volver al inicio"):
        st.switch_page("app.py")
    st.stop()

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
usuario_nombre = st.session_state.get("usuario", None)

# ─── BOTÓN VOLVER ───
if st.button("← Volver a resultados"):
    st.switch_page("app.py")

# ─── HERO ───
st.markdown(
    f'<div class="detail-hero">'
        f'<div>'
            f'<div class="detail-route">{iata_origen}<span class="detail-arrow">✈</span>{iata_destino}</div>'
            f'<div class="detail-sub"><strong>{origen}</strong> → <strong>{destino}</strong> &nbsp;·&nbsp; {fecha} &nbsp;·&nbsp; Salida <strong>{vuelo["hora_salida"]}</strong></div>'
            f'<div style="font-size:0.88rem;color:#94a3b8;margin-top:0.3rem">{vuelo["linea"]} &nbsp;·&nbsp; {vuelo["vuelo"]}</div>'
        f'</div>'
        f'<div class="detail-badge" style="background:{color_nota}">{nota_final:.1f}<div class="detail-badge-lbl">{etiqueta}</div></div>'
    f'</div>',
    unsafe_allow_html=True
)

# ─── CONTENIDO ───
col_left, col_right = st.columns([3, 2])

with col_left:
    for loc, dat, icono in [(origen, datos_o, "🛫"), (destino, datos_d, "🛬")]:
        st.markdown(
            f'<div class="info-card"><h3>{icono} Clima en {loc}</h3>'
            f'<div class="w-grid">'
            f'<div class="w-item"><div class="w-icon">🌡️</div><div class="w-val">{dat["temperature"]}°C</div><div class="w-lbl">Temperatura</div></div>'
            f'<div class="w-item"><div class="w-icon">💨</div><div class="w-val">{dat["wind_speed"]} km/h</div><div class="w-lbl">Viento</div></div>'
            f'<div class="w-item"><div class="w-icon">🌧️</div><div class="w-val">{dat["precipitation"]} mm</div><div class="w-lbl">Precipitación</div></div>'
            f'</div></div>',
            unsafe_allow_html=True
        )
    st.markdown(
        f'<div class="info-card"><h3>✈️ Información del vuelo</h3>'
        f'<div class="fi-row"><span class="fi-label">Aerolínea</span><span class="fi-value">{vuelo["linea"]}</span></div>'
        f'<div class="fi-row"><span class="fi-label">Número</span><span class="fi-value">{vuelo["vuelo"]}</span></div>'
        f'<div class="fi-row"><span class="fi-label">Hora salida</span><span class="fi-value">{vuelo["hora_salida"]}</span></div>'
        f'<div class="fi-row"><span class="fi-label">Origen</span><span class="fi-value">{origen}</span></div>'
        f'<div class="fi-row"><span class="fi-label">Destino</span><span class="fi-value">{destino}</span></div>'
        f'<div class="fi-row"><span class="fi-label">Fecha</span><span class="fi-value">{fecha}</span></div>'
        f'</div>',
        unsafe_allow_html=True
    )

with col_right:
    criterios = {
        "Temperatura origen":    min(max(datos_o["temperature"], 0) / 40, 1.0),
        "Viento origen":         max(0, 1 - datos_o["wind_speed"] / 100),
        "Precipitación origen":  max(0, 1 - datos_o["precipitation"] / 20),
        "Temperatura destino":   min(max(datos_d["temperature"], 0) / 40, 1.0),
        "Viento destino":        max(0, 1 - datos_d["wind_speed"] / 100),
        "Precipitación destino": max(0, 1 - datos_d["precipitation"] / 20),
    }
    barras = '<div class="info-card"><h3>📊 Desglose de puntuación</h3>'
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
    barras += '</div>'
    st.markdown(barras, unsafe_allow_html=True)

    st.markdown(
        f'<div class="info-card"><h3>💶 Precio estimado</h3>'
        f'<div class="price-big">{precio_vuelo}<span>€</span></div>'
        f'<div class="price-tag">Precio orientativo · No vinculante</div></div>',
        unsafe_allow_html=True
    )

    st.button("🎫 Reservar este vuelo", use_container_width=True)
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    ya_fav = any(
        f.get("vuelo", {}).get("vuelo") == vuelo["vuelo"]
        for f in st.session_state.get("favoritos", [])
    )
    if ya_fav:
        st.markdown('<div class="fav-badge">⭐ Guardado en favoritos</div>', unsafe_allow_html=True)
    else:
        if st.button("☆ Guardar en favoritos", use_container_width=True):
            if not st.session_state.get("usuario"):
                st.warning("Inicia sesión para guardar favoritos.")
            else:
                import json, hashlib, os
                DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "usuarios.json")
                email = st.session_state.get("usuario_email")
                if email and os.path.exists(DB_PATH):
                    with open(DB_PATH, "r") as f:
                        u = json.load(f)
                    if email in u:
                        if "favoritos" not in u[email]:
                            u[email]["favoritos"] = []
                        u[email]["favoritos"].append(d)
                        with open(DB_PATH, "w") as f:
                            json.dump(u, f)
                if "favoritos" not in st.session_state:
                    st.session_state["favoritos"] = []
                st.session_state["favoritos"].append(d)
                st.success("✅ Guardado en favoritos")
                st.rerun()
