import streamlit as st

st.set_page_config(page_title="Mis favoritos · Legion Flight", layout="wide")

# ─────────────────────────────────────────────
#  GUARD
# ─────────────────────────────────────────────
if not st.session_state.get("usuario"):
    st.warning("Debes iniciar sesión para ver tus vuelos favoritos.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Iniciar sesión"):
            st.switch_page("pages/login.py")
    with col2:
        if st.button("← Volver al inicio"):
            st.switch_page("app.py")
    st.stop()

usuario_nombre = st.session_state["usuario"]
favoritos      = st.session_state.get("favoritos", [])

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500;600&display=swap');

    *, *::before, *::after { box-sizing: border-box; }
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #06080f !important;
        color: #e8eaf0;
    }
    #MainMenu {visibility: hidden;}
    footer     {visibility: hidden;}
    header     {visibility: hidden;}

    .navbar {
        position: fixed; top: 0; left: 0; width: 100%; z-index: 9999;
        background: rgba(6,8,15,0.85);
        backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(255,255,255,0.07);
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.7rem 2.5rem;
    }
    .navbar-logo {
        font-family: 'Syne', sans-serif; font-size: 1.4rem;
        font-weight: 800; color: #ffffff; display: flex;
        align-items: center; gap: 0.6rem;
    }
    .logo-dot { color: #3b82f6; }
    .block-container { padding-top: 5rem !important; }

    /* ── PAGE HEADER ── */
    .page-header {
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 2rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }
    .page-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.2rem; font-weight: 800;
        color: #ffffff; letter-spacing: -1px;
    }
    .page-subtitle { color: #6b7280; font-size: 0.9rem; margin-top: 0.25rem; }

    /* ── FAV CARD ── */
    .fav-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px; overflow: hidden;
        display: flex; align-items: stretch;
        margin-bottom: 12px; transition: all 0.3s ease;
    }
    .fav-card:hover {
        border-color: rgba(234,179,8,0.35);
        background: rgba(255,255,255,0.05);
        box-shadow: 0 8px 28px rgba(0,0,0,0.35);
        transform: translateY(-2px);
    }
    .fav-card-accent {
        width: 5px; min-height: 100%;
        background: linear-gradient(180deg, #fbbf24, #f59e0b);
        flex-shrink: 0;
    }
    .fav-card-body {
        padding: 20px 24px; flex-grow: 1;
        display: flex; align-items: center; justify-content: space-between;
        flex-wrap: wrap; gap: 1rem;
    }
    .fav-route {
        font-family: 'Syne', sans-serif;
        font-size: 1.6rem; font-weight: 800;
        color: #ffffff; letter-spacing: -0.5px;
        display: flex; align-items: center; gap: 0.6rem;
    }
    .fav-route-arrow { color: #fbbf24; font-size: 1.2rem; }
    .fav-meta { font-size: 0.82rem; color: #6b7280; margin-top: 4px; }
    .fav-meta strong { color: #9ca3af; }

    .fav-score {
        padding: 8px 16px; border-radius: 10px;
        font-family: 'Syne', sans-serif; font-weight: 800;
        font-size: 1.2rem; color: white; text-align: center;
        min-width: 80px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .fav-score-label { font-size: 0.5rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 3px; opacity: 0.85; }

    .fav-price {
        font-family: 'Syne', sans-serif;
        font-size: 1.8rem; font-weight: 800;
        color: #ffffff; letter-spacing: -1px;
    }
    .fav-price span { font-size: 0.9rem; color: #9ca3af; }
    .fav-price-tag { font-size: 0.65rem; color: #22c55e; font-weight: 700; text-transform: uppercase; }

    /* ── BOTONES ── */
    div.stButton > button {
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        color: white !important; font-weight: 700 !important;
        border-radius: 10px !important; border: none !important;
        height: 3em !important; font-family: 'Syne', sans-serif !important;
        box-shadow: 0 4px 16px rgba(37,99,235,0.3) !important;
        transition: all 0.25s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(37,99,235,0.5) !important;
    }

    /* ── EMPTY STATE ── */
    .empty-state {
        text-align: center; padding: 5rem 2rem;
        color: #374151;
    }
    .empty-state .emoji { font-size: 4rem; margin-bottom: 1rem; }
    .empty-state h3 {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem; font-weight: 700;
        color: #4b5563; margin-bottom: 0.5rem;
    }
    .empty-state p { color: #374151; font-size: 0.9rem; max-width: 340px; margin: 0 auto; }

    hr { border-color: rgba(255,255,255,0.07) !important; }
</style>

<div class="navbar">
    <div class="navbar-logo">✈️ Legion<span class="logo-dot">.</span>Flight</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  NAVEGACIÓN
# ─────────────────────────────────────────────
if st.button("← Volver al inicio"):
    st.switch_page("app.py")

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CABECERA
# ─────────────────────────────────────────────
inicial = usuario_nombre[0].upper()
st.markdown(f"""
<div class="page-header">
    <div>
        <div class="page-title">⭐ Mis vuelos favoritos</div>
        <div class="page-subtitle">Hola, <strong style="color:#e8eaf0">{usuario_nombre}</strong> · {len(favoritos)} vuelo{'s' if len(favoritos) != 1 else ''} guardado{'s' if len(favoritos) != 1 else ''}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  LISTADO DE FAVORITOS
# ─────────────────────────────────────────────
if not favoritos:
    st.markdown("""
    <div class="empty-state">
        <div class="emoji">🔍</div>
        <h3>Todavía no tienes favoritos</h3>
        <p>Busca vuelos en la página principal y guarda los que más te interesen.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍 Buscar vuelos", use_container_width=True):
        st.switch_page("app.py")
else:
    # Botón limpiar todo
    col_header, col_clear = st.columns([4, 1])
    with col_clear:
        if st.button("🗑️ Eliminar todos", use_container_width=True):
            st.session_state["favoritos"] = []
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    for i, fav in enumerate(favoritos):
        vuelo        = fav["vuelo"]
        iata_origen  = fav["iata_origen"]
        iata_destino = fav["iata_destino"]
        origen       = fav["origen"]
        destino      = fav["destino"]
        fecha        = fav["fecha"]
        nota_final   = fav["nota_final"]
        etiqueta     = fav["etiqueta"]
        color_nota   = fav["color_nota"]
        precio_vuelo = fav["precio_vuelo"]

        st.markdown(
            '<div class="fav-card">'
                '<div class="fav-card-accent"></div>'
                '<div class="fav-card-body">'
                    '<div>'
                        '<div class="fav-route">'
                            + iata_origen +
                            '<span class="fav-route-arrow">✈</span>'
                            + iata_destino +
                        '</div>'
                        '<div class="fav-meta">'
                            '<strong>' + origen + '</strong> → <strong>' + destino + '</strong>'
                            ' &nbsp;·&nbsp; ' + fecha +
                            ' &nbsp;·&nbsp; ' + vuelo['hora_salida'] +
                            ' &nbsp;·&nbsp; ' + vuelo['linea'] +
                        '</div>'
                    '</div>'
                    '<div class="fav-score" style="background:' + color_nota + '">'
                        + f"{nota_final:.1f}" +
                        '<div class="fav-score-label">' + etiqueta + '</div>'
                    '</div>'
                    '<div>'
                        '<div class="fav-price">' + str(precio_vuelo) + '<span>€</span></div>'
                        '<div class="fav-price-tag">Estimado</div>'
                    '</div>'
                '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        col_ver, col_elim = st.columns([3, 1])
        with col_ver:
            if st.button(f"Ver detalle →", key=f"ver_fav_{i}"):
                st.session_state["vuelo_seleccionado"] = fav
                st.switch_page("pages/vuelo.py")
        with col_elim:
            if st.button("🗑️ Eliminar", key=f"elim_fav_{i}"):
                st.session_state["favoritos"].pop(i)
                st.rerun()

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown('<p style="text-align:center;color:#374151;font-size:0.8rem">© 2025 Legion Flight</p>', unsafe_allow_html=True)
