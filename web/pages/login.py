import streamlit as st
import hashlib
import json
import os

st.set_page_config(page_title="Acceso · Legion Flight", layout="centered")

# ─────────────────────────────────────────────
#  ALMACENAMIENTO DE USUARIOS (JSON local)
# ─────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "usuarios.json")

def cargar_usuarios():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return {}

def guardar_usuarios(usuarios):
    with open(DB_PATH, "w") as f:
        json.dump(usuarios, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def registrar(username, password):
    usuarios = cargar_usuarios()
    if username in usuarios:
        return False, "Este nombre de usuario ya está en uso."
    usuarios[username] = {"password": hash_password(password), "favoritos": []}
    guardar_usuarios(usuarios)
    return True, "Cuenta creada correctamente."

def login(username, password):
    usuarios = cargar_usuarios()
    if username not in usuarios:
        return False, "Nombre de usuario no encontrado."
    if usuarios[username]["password"] != hash_password(password):
        return False, "Contraseña incorrecta."
    return True, username


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

    [data-testid="stSidebar"]       { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    .block-container { padding-top: 3rem !important; max-width: 480px !important; }

    .auth-logo {
        text-align: center;
        font-family: 'Syne', sans-serif;
        font-size: 2rem; font-weight: 800;
        color: white; margin-bottom: 0.25rem;
    }
    .auth-logo .dot { color: #3b82f6; }
    .auth-subtitle {
        text-align: center; color: #6b7280;
        font-size: 0.9rem; margin-bottom: 2.5rem;
    }

    div.stTextInput > label { color: #9ca3af !important; font-size: 0.82rem !important; }
    div.stTextInput > div > input {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important; color: white !important;
        padding: 0.75rem 1rem !important;
    }
    div.stTextInput > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }

    div.stButton > button {
        width: 100% !important; height: 3.2em !important;
        background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
        color: white !important; font-weight: 700 !important;
        border-radius: 10px !important; border: none !important;
        font-family: 'Syne', sans-serif !important;
        font-size: 1rem !important; letter-spacing: 0.02em !important;
        box-shadow: 0 4px 20px rgba(37,99,235,0.35) !important;
        transition: all 0.25s ease !important;
        margin-top: 0.5rem !important;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(37,99,235,0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  REDIRECT SI YA ESTÁ LOGUEADO
# ─────────────────────────────────────────────
if st.session_state.get("usuario"):
    st.success(f"Ya has iniciado sesión como **{st.session_state['usuario']}**")
    if st.button("← Volver al inicio"):
        st.switch_page("app.py")
    st.stop()

# ─────────────────────────────────────────────
#  LOGO
# ─────────────────────────────────────────────
st.markdown('<div class="auth-logo">Legion<span class="dot">.</span>Flight</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-subtitle">Tu compañero meteorológico para volar</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS LOGIN / REGISTRO
# ─────────────────────────────────────────────
if "auth_tab" not in st.session_state:
    st.session_state["auth_tab"] = "login"

col_log, col_reg = st.columns(2)
with col_log:
    if st.button("Iniciar sesión", key="tab_login", use_container_width=True):
        st.session_state["auth_tab"] = "login"
with col_reg:
    if st.button("Crear cuenta", key="tab_reg", use_container_width=True):
        st.session_state["auth_tab"] = "registro"

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FORMULARIO LOGIN
# ─────────────────────────────────────────────
if st.session_state["auth_tab"] == "login":
    st.markdown("### Iniciar sesión")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    with st.form("form_login"):
        username_l = st.text_input("Nombre de usuario", placeholder="tu_usuario")
        password_l = st.text_input("Contraseña", type="password", placeholder="••••••••")
        submit_l   = st.form_submit_button("Entrar →")

    if submit_l:
        if not username_l or not password_l:
            st.error("Rellena todos los campos.")
        else:
            ok, resultado = login(username_l, password_l)
            if ok:
                st.session_state["usuario"] = resultado
                usuarios_data = cargar_usuarios()
                st.session_state["favoritos"] = usuarios_data.get(resultado, {}).get("favoritos", [])
                st.success(f"Bienvenido, {resultado}!")
                st.balloons()
                st.switch_page("app.py")
            else:
                st.error(resultado)

# ─────────────────────────────────────────────
#  FORMULARIO REGISTRO
# ─────────────────────────────────────────────
else:
    st.markdown("### Crear cuenta nueva")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    with st.form("form_registro"):
        username_r = st.text_input("Nombre de usuario", placeholder="tu_usuario")
        password_r = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
        confirm_r  = st.text_input("Confirmar contraseña", type="password", placeholder="Repite la contraseña")
        submit_r   = st.form_submit_button("Crear cuenta →")

    if submit_r:
        if not username_r or not password_r or not confirm_r:
            st.error("Rellena todos los campos.")
        elif len(username_r) < 3:
            st.error("El nombre de usuario debe tener al menos 3 caracteres.")
        elif len(password_r) < 6:
            st.error("La contraseña debe tener al menos 6 caracteres.")
        elif password_r != confirm_r:
            st.error("Las contraseñas no coinciden.")
        else:
            ok, mensaje = registrar(username_r, password_r)
            if ok:
                st.success(f"{mensaje} Ahora inicia sesión.")
                st.session_state["auth_tab"] = "login"
                st.rerun()
            else:
                st.error(mensaje)

st.markdown("---")
if st.button("← Volver al inicio sin iniciar sesión", use_container_width=True):
    st.switch_page("app.py")
