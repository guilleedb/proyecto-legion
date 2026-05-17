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

def registrar(nombre, email, password):
    usuarios = cargar_usuarios()
    if email in usuarios:
        return False, "Este email ya está registrado."
    usuarios[email] = {"nombre": nombre, "password": hash_password(password)}
    guardar_usuarios(usuarios)
    return True, "Cuenta creada correctamente."

def login(email, password):
    usuarios = cargar_usuarios()
    if email not in usuarios:
        return False, "Email no encontrado."
    if usuarios[email]["password"] != hash_password(password):
        return False, "Contraseña incorrecta."
    return True, usuarios[email]["nombre"]


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

    .auth-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px; padding: 2.5rem 2rem;
    }

    .tab-selector {
        display: flex; background: rgba(255,255,255,0.04);
        border-radius: 12px; padding: 4px; margin-bottom: 2rem; gap: 4px;
    }
    .tab-btn {
        flex: 1; text-align: center; padding: 0.6rem;
        border-radius: 10px; cursor: pointer;
        font-size: 0.9rem; font-weight: 600; transition: 0.2s;
        font-family: 'Syne', sans-serif;
    }
    .tab-btn.active { background: #2563eb; color: white; }
    .tab-btn.inactive { color: #6b7280; }

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

    .divider {
        display: flex; align-items: center; gap: 1rem;
        margin: 1.5rem 0; color: #374151;
        font-size: 0.8rem;
    }
    .divider::before, .divider::after {
        content: ''; flex: 1;
        height: 1px; background: rgba(255,255,255,0.07);
    }

    .back-link {
        text-align: center; margin-top: 1.5rem;
        font-size: 0.85rem; color: #6b7280;
    }
    .back-link a { color: #3b82f6; text-decoration: none; }
    .back-link a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  REDIRECT SI YA ESTÁ LOGUEADO
# ─────────────────────────────────────────────
if st.session_state.get("usuario"):
    st.success(f"✅ Ya has iniciado sesión como **{st.session_state['usuario']}**")
    if st.button("← Volver al inicio"):
        st.switch_page("app.py")
    st.stop()

# ─────────────────────────────────────────────
#  LOGO
# ─────────────────────────────────────────────
st.markdown('<div class="auth-logo">✈️ Legion<span class="dot">.</span>Flight</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-subtitle">Tu compañero meteorológico para volar</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  TABS LOGIN / REGISTRO
# ─────────────────────────────────────────────
if "auth_tab" not in st.session_state:
    st.session_state["auth_tab"] = "login"

col_log, col_reg = st.columns(2)
with col_log:
    if st.button("🔑 Iniciar sesión", key="tab_login", use_container_width=True):
        st.session_state["auth_tab"] = "login"
with col_reg:
    if st.button("✨ Crear cuenta", key="tab_reg", use_container_width=True):
        st.session_state["auth_tab"] = "registro"

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FORMULARIO LOGIN
# ─────────────────────────────────────────────
if st.session_state["auth_tab"] == "login":
    st.markdown("### 🔑 Iniciar sesión")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    with st.form("form_login"):
        email_l    = st.text_input("Correo electrónico", placeholder="tu@email.com")
        password_l = st.text_input("Contraseña", type="password", placeholder="••••••••")
        submit_l   = st.form_submit_button("Entrar →")

    if submit_l:
        if not email_l or not password_l:
            st.error("Rellena todos los campos.")
        else:
            ok, resultado = login(email_l, password_l)
            if ok:
                st.session_state["usuario"] = resultado
                if "favoritos" not in st.session_state:
                    st.session_state["favoritos"] = []
                st.success(f"✅ ¡Bienvenido, {resultado}!")
                st.balloons()
                st.switch_page("app.py")
            else:
                st.error(resultado)

# ─────────────────────────────────────────────
#  FORMULARIO REGISTRO
# ─────────────────────────────────────────────
else:
    st.markdown("### ✨ Crear cuenta nueva")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    with st.form("form_registro"):
        nombre_r   = st.text_input("Nombre", placeholder="Tu nombre")
        email_r    = st.text_input("Correo electrónico", placeholder="tu@email.com")
        password_r = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
        confirm_r  = st.text_input("Confirmar contraseña", type="password", placeholder="Repite la contraseña")
        submit_r   = st.form_submit_button("Crear cuenta →")

    if submit_r:
        if not nombre_r or not email_r or not password_r or not confirm_r:
            st.error("Rellena todos los campos.")
        elif len(password_r) < 6:
            st.error("La contraseña debe tener al menos 6 caracteres.")
        elif password_r != confirm_r:
            st.error("Las contraseñas no coinciden.")
        elif "@" not in email_r:
            st.error("Introduce un email válido.")
        else:
            ok, mensaje = registrar(nombre_r, email_r, password_r)
            if ok:
                st.success(f"✅ {mensaje} Ahora inicia sesión.")
                st.session_state["auth_tab"] = "login"
                st.rerun()
            else:
                st.error(mensaje)

st.markdown("---")
if st.button("← Volver al inicio sin iniciar sesión", use_container_width=True):
    st.switch_page("app.py")
