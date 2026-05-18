import streamlit as st
import os
import sys

current_dir  = os.path.dirname(os.path.abspath(__file__))
web_dir      = os.path.abspath(os.path.join(current_dir, ".."))
project_root = os.path.abspath(os.path.join(web_dir, ".."))
src_path     = os.path.join(project_root, "src")

if src_path not in sys.path:
    sys.path.insert(0, src_path)

from flight_scoring import score_wind, score_precipitation, score_temperature
from ayuda_weather import degrees_to_compass, load_weather_csv, get_weather_at
import matplotlib.pyplot as plt
import matplotlib
import datetime

st.set_page_config(page_title="Detalle de vuelo · Legion Flight", layout="wide")

# CSS mínimo: ocultar chrome de Streamlit y barra de navegación fija
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
    .navbar-logo { font-family: 'Syne', sans-serif; font-size: 1.3rem; font-weight: 800; color: #fff; }

    div.stButton > button {
        background-color: #2563eb !important; color: white !important;
        font-weight: 700 !important; border-radius: 8px !important;
        border: none !important; padding: 0.5rem 1.2rem !important;
    }
    div.stButton > button:hover { background-color: #1d4ed8 !important; }
</style>
<div class="navbar">
    <div class="navbar-logo">Legion<span style="color:#3b82f6;">.</span>Flight</div>
</div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
v = st.session_state.get("vuelo_seleccionado")

if not v:
    st.error("No hay ningún vuelo seleccionado. Vuelve a la búsqueda y pulsa 'Ver detalle'.")
    if st.button("Volver a resultados", key="volver_error"):
        st.switch_page("app.py")
    st.stop()

# --- CÁLCULO DE SCORES ---
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

# --- HELPERS ---
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

# --- VARIABLES DERIVADAS ---
precio_str = f"~{v['precio']} €" if isinstance(v.get("precio"), int) else "—"
compass_o  = degrees_to_compass(v["dir_orig"])
compass_d  = degrees_to_compass(v["dir_dest"])
pl_o       = precip_label(v["precip_orig"])
pl_d       = precip_label(v["precip_dest"])
estado_css = estado_color(v["estado"])

# --- BOTÓN VOLVER ---
if st.button("← Volver a resultados", key="volver_top"):
    st.switch_page("app.py")

# --- SECCIÓN 1: CABECERA ---
with st.container(border=True):
    c1, c2, c3, c4, c5 = st.columns([2, 1, 2, 1, 1])
    with c1:
        st.caption("Ruta")
        st.markdown(f"### {v['iata_orig']} → {v['iata_dest']}")
        st.caption(f"{v['origen']} → {v['destino']}")
    with c2:
        st.metric("Hora salida", v["hora_salida"])
        st.caption(v["fecha"])
    with c3:
        st.metric("Aerolínea", v["linea"])
        st.caption(v["vuelo"])
    with c4:
        st.caption("Estado")
        st.markdown(
            f'<span style="display:inline-block;padding:4px 14px;border-radius:20px;font-size:0.78rem;font-weight:600;{estado_css}">{v["estado"]}</span>',
            unsafe_allow_html=True
        )
    with c5:
        st.metric("Precio estimado", precio_str)
        st.caption("estimación sin garantía")

# --- SECCIÓN 2: RATING + CLIMA ---
col_rating, col_orig, col_dest = st.columns([1, 1, 1])

with col_rating:
    with st.container(border=True):
        st.caption("Rating meteorológico")
        st.metric(v["etiqueta"], f"{v['nota']:.1f} / 10", help="sobre 10 · peor de los dos aeropuertos")

        st.caption("Desglose de factores")

        st.write(f"Viento (45%) — {sv_avg:.0f}/100")
        st.progress(int(sv_avg))

        st.write(f"Precipitación (40%) — {sp_avg:.0f}/100")
        st.progress(int(sp_avg))

        st.write(f"Temperatura (15%) — {st_avg:.0f}/100")
        st.progress(int(st_avg))

        st.divider()
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric(f"Score {v['iata_orig']}", f"{score_orig:.0f}")
        sc2.metric(f"Score {v['iata_dest']}", f"{score_dest:.0f}")
        sc3.metric("Score final", f"{score_final:.0f}")

with col_orig:
    with st.container(border=True):
        st.caption("Clima en origen")
        st.subheader(f"{v['origen']} ({v['iata_orig']})")

        st.metric("Temperatura", f"{v['temp_orig']} °C")
        st.metric("Viento", f"{v['viento_orig']} km/h")
        st.metric("Dirección del viento", f"{compass_o} ({int(v['dir_orig'])}°)")
        st.metric("Precipitación", f"{v['precip_orig']} mm — {pl_o}")

        st.caption("Puntuación por factor")
        st.write(f"Viento — {sv_o:.0f}/100")
        st.progress(int(sv_o))
        st.write(f"Precipitación — {sp_o:.0f}/100")
        st.progress(int(sp_o))
        st.write(f"Temperatura — {st_o:.0f}/100")
        st.progress(int(st_o))

with col_dest:
    with st.container(border=True):
        st.caption("Clima en destino")
        st.subheader(f"{v['destino']} ({v['iata_dest']})")

        st.metric("Temperatura", f"{v['temp_dest']} °C")
        st.metric("Viento", f"{v['viento_dest']} km/h")
        st.metric("Dirección del viento", f"{compass_d} ({int(v['dir_dest'])}°)")
        st.metric("Precipitación", f"{v['precip_dest']} mm — {pl_d}")

        st.caption("Puntuación por factor")
        st.write(f"Viento — {sv_d:.0f}/100")
        st.progress(int(sv_d))
        st.write(f"Precipitación — {sp_d:.0f}/100")
        st.progress(int(sp_d))
        st.write(f"Temperatura — {st_d:.0f}/100")
        st.progress(int(st_d))

# --- SECCIÓN 3: GRÁFICO COMPARATIVO POR HORA ---
st.divider()
st.subheader("Comparativa de condiciones por horario")
st.caption(f"Puntuación estimada para cada hora del día en la ruta {v['iata_orig']} → {v['iata_dest']} · {v['fecha']}")

@st.cache_data(ttl=3600)
def load_df():
    return load_weather_csv()

df_w = load_df()
fecha_dt = datetime.date.fromisoformat(v["fecha"])

horas, scores_o, scores_d, scores_final = [], [], [], []
for h in range(24):
    wo = get_weather_at(df_w, v["origen"], fecha_dt, h)
    wd = get_weather_at(df_w, v["destino"], fecha_dt, (h + 1) % 24)
    if wo and wd:
        so = score_wind(wo["wind_speed"]) * 0.45 + score_precipitation(wo["precipitation"]) * 0.40 + score_temperature(wo["temperature"]) * 0.15
        sd = score_wind(wd["wind_speed"]) * 0.45 + score_precipitation(wd["precipitation"]) * 0.40 + score_temperature(wd["temperature"]) * 0.15
        horas.append(h)
        scores_o.append(round(so / 10, 1))
        scores_d.append(round(sd / 10, 1))
        scores_final.append(round(min(so, sd) / 10, 1))

if horas:
    hora_actual = v["hora_int"]

    matplotlib.rcParams.update({"text.color": "#e8eaf0", "axes.labelcolor": "#9ca3af",
                                  "xtick.color": "#9ca3af", "ytick.color": "#9ca3af"})

    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor("#0d1117")
    ax.set_facecolor("#0d1117")

    ax.plot(horas, scores_o,    color="#3b82f6", linewidth=2, label=f"Origen ({v['iata_orig']})", marker="o", markersize=3)
    ax.plot(horas, scores_d,    color="#8b5cf6", linewidth=2, label=f"Destino ({v['iata_dest']})", marker="o", markersize=3)
    ax.plot(horas, scores_final, color="#22c55e", linewidth=2.5, label="Score final", marker="o", markersize=3, linestyle="--")

    # Línea vertical en la hora del vuelo seleccionado
    if hora_actual in horas:
        idx = horas.index(hora_actual)
        ax.axvline(x=hora_actual, color="#f59e0b", linewidth=1.5, linestyle=":", alpha=0.9)
        ax.scatter([hora_actual], [scores_final[idx]], color="#f59e0b", s=80, zorder=5)
        ax.annotate(f"  {v['hora_salida']}\n  {scores_final[idx]}", xy=(hora_actual, scores_final[idx]),
                    color="#f59e0b", fontsize=8.5, va="bottom")

    ax.set_xlim(0, 23)
    ax.set_ylim(0, 10)
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f"{h:02d}h" for h in range(0, 24, 2)], fontsize=8)
    ax.set_yticks(range(0, 11, 2))
    ax.set_ylabel("Puntuación (0–10)", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#2e2e2e")
    ax.grid(axis="y", color="#1e293b", linewidth=0.8)
    ax.legend(fontsize=8.5, facecolor="#0d1117", edgecolor="#2e2e2e", labelcolor="#e8eaf0")

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# --- SECCIÓN 4: RECOMENDACIÓN ---
nota = v["nota"]
if nota >= 9.0:
    st.success("**Condiciones excepcionales** — Mínimas turbulencias esperadas, buena visibilidad y temperaturas confortables en ambos aeropuertos. Es un momento ideal para volar.")
elif nota >= 7.5:
    st.info("**Buenas condiciones** — El trayecto debería transcurrir con normalidad. Las condiciones meteorológicas son favorables en origen y destino.")
elif nota >= 5.5:
    st.warning("**Condiciones moderadas** — Es posible que haya algo de turbulencia o lluvia ligera. Llega con tiempo y consulta el estado del vuelo antes de salir.")
else:
    st.error("**Condiciones adversas** — Se detectan condiciones desfavorables en alguno de los aeropuertos. Consulta el estado actualizado y contacta con la aerolínea si tienes dudas.")

st.caption("Score final: peor valor entre origen y destino (criterio conservador). Factores: viento (45%), precipitación (40%), temperatura (15%). El precio es una estimación basada en ruta, hora y aerolínea.")

st.write("")
if st.button("← Volver a resultados", key="volver_bottom"):
    st.switch_page("app.py")
