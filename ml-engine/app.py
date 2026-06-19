"""
=============================================================================
 Plataforma Cloud para Analisis de Microemprendimientos
 y Prediccion de Sostenibilidad Economica
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import json
import requests

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACION DE PAGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Analisis de Microemprendimientos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS — Diseño premium oscuro, sin emojis decorativos
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    box-sizing: border-box;
}

/* ── Fondo principal ── */
.stApp {
    background: #0d0d1a;
    color: #e2e2f0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #111120;
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: #c8c8e0; }

/* ── Botón principal ── */
.stButton > button {
    background: linear-gradient(135deg, #5b52f5, #9333ea);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 11px 28px;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.3px;
    width: 100%;
    transition: opacity 0.2s ease, transform 0.2s ease;
    box-shadow: 0 4px 20px rgba(91,82,245,0.35);
}
.stButton > button:hover {
    opacity: 0.88;
    transform: translateY(-1px);
}

/* ── Inputs ── */
.stNumberInput input, .stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #e2e2f0 !important;
    font-size: 14px !important;
}

/* ── Métricas ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 16px 18px;
    transition: transform 0.2s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
}

/* ── Encabezados de sección ── */
.section-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: rgba(180,170,240,0.55);
    margin-bottom: 4px;
}
.section-title {
    font-size: 20px;
    font-weight: 700;
    color: #c4b5fd;
    margin-bottom: 16px;
    letter-spacing: -0.2px;
}

/* ── Badge de riesgo ── */
.badge {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 50px;
    font-weight: 700;
    font-size: 12px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.badge-alto  { background: rgba(239,68,68,0.15);  border: 1px solid #ef4444; color:#f87171; }
.badge-medio { background: rgba(245,158,11,0.15); border: 1px solid #f59e0b; color:#fbbf24; }
.badge-bajo  { background: rgba(34,197,94,0.15);  border: 1px solid #22c55e; color:#4ade80; }

/* ── Card de recomendaciones ── */
.rec-card {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid #5b52f5;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin-bottom: 8px;
    font-size: 13.5px;
    line-height: 1.65;
    color: #cccce8;
}

/* ── Divisor ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(91,82,245,0.4), transparent);
    margin: 24px 0;
}

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, rgba(91,82,245,0.18), rgba(147,51,234,0.10));
    border: 1px solid rgba(91,82,245,0.25);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.hero-title {
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
    line-height: 1.2;
}
.hero-sub {
    font-size: 14px;
    color: rgba(200,200,230,0.55);
    font-weight: 400;
    max-width: 680px;
}

/* ── Card métricas IA (sidebar) ── */
.ai-metric-card {
    background: rgba(91,82,245,0.12);
    border: 1px solid rgba(91,82,245,0.3);
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
}
.ai-metric-value {
    font-size: 22px;
    font-weight: 800;
    color: #a78bfa;
    line-height: 1.1;
}
.ai-metric-label {
    font-size: 10px;
    color: rgba(200,200,230,0.45);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 2px;
}
.ai-metric-desc {
    font-size: 10px;
    color: rgba(200,200,230,0.3);
    margin-top: 3px;
}

/* ── Tag usuario autenticado ── */
.user-tag {
    background: rgba(34,197,94,0.1);
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    color: #4ade80;
    text-align: center;
    margin-bottom: 8px;
}

/* ── Sidebar títulos ── */
.sidebar-section-title {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: rgba(180,170,240,0.45);
    margin-bottom: 10px;
    margin-top: 4px;
}

/* ── Tabla ── */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
}

/* ── Riesgo row ── */
.risk-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 18px 0 6px;
}
.risk-label {
    font-size: 13px;
    color: rgba(200,200,230,0.5);
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────────────────────
DATASET_FILE = "04-01-Financial Sample Data.xlsx"
METRICS_FILE = "model_metrics.json"
BACKEND_URL  = "http://backend:4000"


# ─────────────────────────────────────────────────────────────────────────────
# CARGA DE DATOS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def cargar_dataset(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()
    cols_num = ["Gross Sales", "Sales", "COGS", "Profit",
                "Discounts", "Units Sold", "Sale Price", "Manufacturing Price"]
    for col in cols_num:
        if col in df.columns and df[col].dtype == object:
            df[col] = (
                df[col].astype(str)
                .str.replace(r"[\$,\(\)\s]", "", regex=True)
                .str.replace(r"^-$", "0", regex=True)
                .pipe(pd.to_numeric, errors="coerce")
            )
    df.dropna(subset=["Sales", "COGS", "Profit"], inplace=True)
    return df


@st.cache_data(show_spinner=False)
def cargar_metricas(path: str) -> dict | None:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


if not os.path.exists(DATASET_FILE):
    st.error(f"No se encontró el archivo '{DATASET_FILE}'. Colócalo en la misma carpeta que app.py.")
    st.stop()

with st.spinner("Cargando dataset..."):
    df = cargar_dataset(DATASET_FILE)

metricas_modelo = cargar_metricas(METRICS_FILE)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "jwt_token" not in st.session_state:
    st.session_state["jwt_token"] = None
if "usuario_nombre" not in st.session_state:
    st.session_state["usuario_nombre"] = None


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE AUTENTICACIÓN
# ─────────────────────────────────────────────────────────────────────────────
def api_registro(nombre, email, password):
    try:
        r = requests.post(f"{BACKEND_URL}/api/auth/registro",
                          json={"nombre": nombre, "email": email, "password": password}, timeout=5)
        data = r.json()
        return r.status_code == 201, data.get("mensaje" if r.status_code == 201 else "error", "Error")
    except Exception:
        return False, "No se pudo conectar con el servidor"


def api_login(email, password):
    try:
        r = requests.post(f"{BACKEND_URL}/api/auth/login",
                          json={"email": email, "password": password}, timeout=5)
        data = r.json()
        if r.status_code == 200:
            return True, data.get("mensaje", "OK"), data.get("token", "")
        return False, data.get("error", "Error"), ""
    except Exception:
        return False, "No se pudo conectar con el servidor", ""


def api_guardar_registro(ingresos, costos_fijos, costos_variables, riesgo, token):
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/registros",
            json={"ingresos": ingresos, "costos_fijos": costos_fijos,
                  "costos_variables": costos_variables, "riesgo": riesgo},
            headers={"Authorization": f"Bearer {token}"},
            timeout=5
        )
        return r.status_code == 201, r.json().get("mensaje" if r.status_code == 201 else "error", "")
    except Exception:
        return False, "No se pudo conectar con el servidor"


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:

    # ── Métricas del modelo ──────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section-title">Rendimiento del Modelo</div>', unsafe_allow_html=True)

    if metricas_modelo:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="ai-metric-card">
                <div class="ai-metric-value">{metricas_modelo['accuracy']:.1f}%</div>
                <div class="ai-metric-label">Accuracy</div>
                <div class="ai-metric-desc">Exactitud global</div>
            </div>""", unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div class="ai-metric-card">
                <div class="ai-metric-value">{metricas_modelo['f1_score']:.1f}%</div>
                <div class="ai-metric-label">F1-Score</div>
                <div class="ai-metric-desc">Ponderado</div>
            </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='font-size:10px;color:rgba(200,200,230,0.3);margin-top:6px;line-height:1.5;'>
            Random Forest &middot; {metricas_modelo['n_estimators']} árboles<br>
            {metricas_modelo['train_samples']:,} entrenamiento &middot; {metricas_modelo['test_samples']:,} prueba
        </div>""", unsafe_allow_html=True)
    else:
        st.caption("Sin métricas disponibles. Ejecuta entrenar_modelo.py.")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.divider()

    # ── Autenticación ────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section-title">Mi Cuenta</div>', unsafe_allow_html=True)

    if st.session_state["jwt_token"]:
        nombre_usr = st.session_state["usuario_nombre"] or "Usuario"
        st.markdown(f'<div class="user-tag">Sesión activa &mdash; <b>{nombre_usr}</b></div>', unsafe_allow_html=True)
        st.caption("Los análisis se guardarán automáticamente en la base de datos.")
        if st.button("Cerrar sesión", key="btn_logout"):
            st.session_state["jwt_token"]      = None
            st.session_state["usuario_nombre"] = None
            st.rerun()
    else:
        tab_l, tab_r = st.tabs(["Iniciar sesión", "Crear cuenta"])

        with tab_l:
            with st.form("form_login"):
                login_email = st.text_input("Email", placeholder="demo@empresa.com", key="login_email")
                login_pass  = st.text_input("Contraseña", type="password", placeholder="••••••••", key="login_pass")
                if st.form_submit_button("Entrar", use_container_width=True):
                    if login_email and login_pass:
                        ok, msg, token = api_login(login_email, login_pass)
                        if ok:
                            st.session_state["jwt_token"]      = token
                            st.session_state["usuario_nombre"] = login_email.split("@")[0].capitalize()
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Completa todos los campos.")

        with tab_r:
            with st.form("form_registro"):
                reg_nombre = st.text_input("Nombre", placeholder="Tu nombre", key="reg_nombre")
                reg_email  = st.text_input("Email",  placeholder="tu@correo.com", key="reg_email")
                reg_pass   = st.text_input("Contraseña", type="password",
                                           placeholder="Mínimo 6 caracteres", key="reg_pass")
                if st.form_submit_button("Crear cuenta", use_container_width=True):
                    if reg_nombre and reg_email and reg_pass:
                        if len(reg_pass) < 6:
                            st.warning("La contraseña debe tener al menos 6 caracteres.")
                        else:
                            ok, msg = api_registro(reg_nombre, reg_email, reg_pass)
                            if ok:
                                st.success(f"{msg} — Ahora inicia sesión.")
                            else:
                                st.error(msg)
                    else:
                        st.warning("Completa todos los campos.")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown(
        "<div style='font-size:10px;color:rgba(200,200,230,0.25);line-height:1.6;'>"
        "Plataforma universitaria &mdash; Proyecto académico<br>"
        "Random Forest · PostgreSQL · Node.js · Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────────────────
# BANNER HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <div class="hero-title">Análisis de Sostenibilidad para Microemprendimientos</div>
  <div class="hero-sub">
    Evalúa la viabilidad financiera de tu negocio comparando tus datos con registros históricos reales.
    El nivel de riesgo es calculado mediante un modelo de Machine Learning entrenado con datos de mercado.
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FORMULARIO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Datos financieros del emprendimiento</div>', unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    ingresos = st.number_input(
        "Ingresos mensuales (USD)",
        min_value=0.0, value=15000.0, step=500.0,
        help="Total de ventas o ingresos del mes",
        key="input_ingresos"
    )
with col_f2:
    costos_fijos = st.number_input(
        "Costos fijos (USD)",
        min_value=0.0, value=5000.0, step=500.0,
        help="Alquiler, salarios fijos, servicios, etc.",
        key="input_costos_fijos"
    )
with col_f3:
    costos_variables = st.number_input(
        "Costos variables (USD)",
        min_value=0.0, value=4000.0, step=500.0,
        help="Materias primas, comisiones, empaque, etc.",
        key="input_costos_variables"
    )

_, col_btn, _ = st.columns([2, 1, 2])
with col_btn:
    analizar = st.button("Analizar emprendimiento", key="btn_analizar")


# ─────────────────────────────────────────────────────────────────────────────
# ANÁLISIS
# ─────────────────────────────────────────────────────────────────────────────
if analizar:
    total_costos     = costos_fijos + costos_variables
    saldo_neto       = ingresos - total_costos
    margen_utilidad  = (saldo_neto / ingresos * 100) if ingresos > 0 else 0.0
    punto_equilibrio = total_costos

    # ── Predicción de riesgo con ML ─────────────────────────────────────────
    import joblib

    try:
        modelo_ia     = joblib.load('modelo_riesgo_definitivo.pkl')
        datos_entrada = pd.DataFrame([[ingresos, total_costos]], columns=['Sales', 'COGS'])
        prediccion    = modelo_ia.predict(datos_entrada)[0]

        if prediccion == 2:
            nivel_riesgo = "ALTO"
            badge_class  = "badge-alto"
            color_riesgo = "#ef4444"
        elif prediccion == 1:
            nivel_riesgo = "MEDIO"
            badge_class  = "badge-medio"
            color_riesgo = "#f59e0b"
        else:
            nivel_riesgo = "BAJO"
            badge_class  = "badge-bajo"
            color_riesgo = "#22c55e"

    except Exception as e:
        st.warning(f"Error cargando el modelo: {e}")
        nivel_riesgo = "DESCONOCIDO"
        badge_class  = "badge-medio"
        color_riesgo = "#6c63ff"

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Métricas principales ─────────────────────────────────────────────────
    st.markdown('<div class="section-title">Resultados financieros</div>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Ingresos",          f"${ingresos:,.0f}")
    m2.metric("Total costos",      f"${total_costos:,.0f}", delta=f"-${total_costos:,.0f}", delta_color="inverse")
    m3.metric("Saldo neto",        f"${saldo_neto:,.0f}",  delta="Ganancia" if saldo_neto >= 0 else "Pérdida")
    m4.metric("Margen neto",       f"{margen_utilidad:.1f}%")
    m5.metric("Punto de equilibrio", f"${punto_equilibrio:,.0f}")

    st.markdown(f"""
    <div class="risk-row">
        <span class="risk-label">Nivel de riesgo financiero</span>
        <span class="badge {badge_class}">{nivel_riesgo}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Filtros de comparativa ───────────────────────────────────────────────
    with st.expander("Filtros de datos históricos de referencia", expanded=False):
        fc1, fc2 = st.columns(2)
        with fc1:
            segmentos    = (["Todos"] + sorted(df["Segment"].dropna().unique().tolist())) if "Segment" in df.columns else ["Todos"]
            segmento_sel = st.selectbox("Segmento", segmentos, key="seg_sel")
        with fc2:
            paises    = (["Todos"] + sorted(df["Country"].dropna().unique().tolist())) if "Country" in df.columns else ["Todos"]
            pais_sel  = st.selectbox("País", paises, key="pais_sel")
    
    df_ref = df.copy()
    if segmento_sel != "Todos" and "Segment" in df.columns:
        df_ref = df_ref[df_ref["Segment"] == segmento_sel]
    if pais_sel != "Todos" and "Country" in df.columns:
        df_ref = df_ref[df_ref["Country"] == pais_sel]

    # ── Comparativa con dataset ──────────────────────────────────────────────
    st.markdown('<div class="section-title">Comparativa con datos históricos</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:13px;color:rgba(200,200,230,0.45);margin-bottom:16px;">'
        'Empresas con ingresos similares al tuyo (rango ±40%)</div>',
        unsafe_allow_html=True
    )

    rango_inf  = ingresos * 0.60
    rango_sup  = ingresos * 1.40
    df_similar = df_ref[(df_ref["Sales"] >= rango_inf) & (df_ref["Sales"] <= rango_sup)].copy()

    if len(df_similar) == 0:
        st.info("No se encontraron registros en el rango exacto. Mostrando promedios del dataset completo.")
        df_similar    = df_ref.copy()
        modo_promedio = True
    else:
        modo_promedio = False

    prom_sales  = df_similar["Sales"].mean()
    prom_cogs   = df_similar["COGS"].mean()
    prom_profit = df_similar["Profit"].mean()
    prom_margen = (prom_profit / prom_sales * 100) if prom_sales > 0 else 0

    col_tab, col_chart = st.columns([1.4, 1])

    with col_tab:
        cols_mostrar = [c for c in ["Segment", "Country", "Product", "Sales", "COGS", "Profit"] if c in df_similar.columns]
        st.dataframe(
            df_similar[cols_mostrar]
            .rename(columns={"Sales": "Ingresos", "COGS": "Costos", "Profit": "Ganancia"})
            .head(12)
            .style.format({"Ingresos": "${:,.0f}", "Costos": "${:,.0f}", "Ganancia": "${:,.0f}"}),
            use_container_width=True,
            hide_index=True
        )
        st.caption(
            f"Dataset completo ({len(df_ref):,} registros)" if modo_promedio
            else f"{len(df_similar):,} empresas en rango de ingresos similar"
        )

    with col_chart:
        categorias     = ["Ingresos", "Costos totales", "Saldo neto"]
        usuario_vals   = [ingresos, total_costos, saldo_neto]
        historico_vals = [prom_sales, prom_cogs, prom_profit]

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name="Tu emprendimiento",
            x=categorias, y=usuario_vals,
            marker_color=["#5b52f5", "#9333ea", "#22c55e" if saldo_neto >= 0 else "#ef4444"],
            text=[f"${v:,.0f}" for v in usuario_vals],
            textposition="outside",
            textfont=dict(color="white", size=11)
        ))
        fig_comp.add_trace(go.Bar(
            name="Promedio histórico",
            x=categorias, y=historico_vals,
            marker_color=["rgba(91,82,245,0.3)", "rgba(147,51,234,0.3)", "rgba(34,197,94,0.3)"],
            text=[f"${v:,.0f}" for v in historico_vals],
            textposition="outside",
            textfont=dict(color="rgba(200,200,230,0.6)", size=11)
        ))
        fig_comp.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#d1d0e8", family="Inter"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", tickprefix="$"),
            title=dict(text="Tu empresa vs. Promedio histórico", font=dict(size=13, color="#c4b5fd")),
            margin=dict(t=44, b=16, l=8, r=8),
            height=300,
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Panel analítico ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Panel analítico</div>', unsafe_allow_html=True)

    col_g1, col_g2, col_g3 = st.columns(3)

    with col_g1:
        fig_donut = go.Figure(go.Pie(
            labels=["Costos fijos", "Costos variables", "Saldo neto" if saldo_neto > 0 else "Pérdida"],
            values=[costos_fijos, costos_variables, abs(saldo_neto)],
            hole=0.58,
            marker_colors=["#5b52f5", "#9333ea", "#22c55e" if saldo_neto > 0 else "#ef4444"],
            textfont=dict(color="white", size=11),
        ))
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#d1d0e8", family="Inter"),
            title=dict(text="Estructura de costos", font=dict(size=12, color="#c4b5fd")),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
            margin=dict(t=44, b=8, l=8, r=8),
            height=260,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_g2:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=margen_utilidad,
            delta={"reference": prom_margen, "valueformat": ".1f", "suffix": "%"},
            number={"suffix": "%", "font": {"size": 26, "color": "#e8e8f0"}},
            gauge={
                "axis": {"range": [-50, 60], "tickcolor": "#a78bfa"},
                "bar":  {"color": color_riesgo},
                "steps": [
                    {"range": [-50, 0],  "color": "rgba(239,68,68,0.12)"},
                    {"range": [0, 10],   "color": "rgba(245,158,11,0.12)"},
                    {"range": [10, 20],  "color": "rgba(245,158,11,0.08)"},
                    {"range": [20, 60],  "color": "rgba(34,197,94,0.10)"},
                ],
                "threshold": {
                    "line": {"color": "#a78bfa", "width": 2},
                    "thickness": 0.75,
                    "value": prom_margen
                },
                "bgcolor": "rgba(0,0,0,0)",
            },
            title={"text": "Margen de utilidad neto<br><span style='font-size:10px;color:#a78bfa'>vs. promedio histórico</span>",
                   "font": {"size": 12, "color": "#c4b5fd"}}
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#d1d0e8", family="Inter"),
            margin=dict(t=36, b=8, l=16, r=16),
            height=260,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_g3:
        fig_hist = px.histogram(
            df_similar, x="Profit", nbins=25,
            color_discrete_sequence=["#5b52f5"],
            labels={"Profit": "Ganancia histórica (USD)"},
            title="Distribución de ganancias en el dataset",
        )
        fig_hist.add_vline(
            x=saldo_neto, line_dash="dash", line_color="#c084fc",
            annotation_text="Tu empresa", annotation_font_color="#c084fc",
            annotation_font_size=11
        )
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#d1d0e8", family="Inter"),
            title=dict(font=dict(size=12, color="#c4b5fd")),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            margin=dict(t=44, b=16, l=8, r=8),
            height=260,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Recomendaciones ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Recomendaciones</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:13px;color:rgba(200,200,230,0.45);margin-bottom:14px;">'
        f'Basadas en nivel de riesgo: <b style="color:#e2e2f0">{nivel_riesgo}</b></div>',
        unsafe_allow_html=True
    )

    if nivel_riesgo == "ALTO":
        recomendaciones = [
            f"<b>Situación crítica.</b> Los costos superan los ingresos en <b>${abs(saldo_neto):,.0f}</b>. "
            "Se requiere acción inmediata para evitar insolvencia.",
            "<b>Reducción de costos.</b> Identifica gastos no esenciales. Renegocia contratos con proveedores "
            "y busca alternativas de menor costo para insumos clave.",
            "<b>Incremento de ingresos.</b> Evalúa ajustes de precio o diversificación hacia productos "
            "con mayor margen.",
            f"<b>Punto de equilibrio.</b> Necesitas al menos <b>${punto_equilibrio:,.0f}</b> en ingresos mensuales "
            "para cubrir costos totales.",
            "<b>Financiamiento.</b> Evalúa líneas de crédito, inversores o programas de apoyo gubernamental "
            "para microempresas.",
            f"<b>Referencia histórica.</b> Empresas similares en el dataset generan en promedio "
            f"<b>${prom_profit:,.0f}</b> de ganancia. Analiza sus modelos de negocio.",
        ]
    elif nivel_riesgo == "MEDIO":
        recomendaciones = [
            f"<b>Zona de atención.</b> Margen de utilidad del <b>{margen_utilidad:.1f}%</b>, por debajo del "
            "umbral saludable del 20%. El negocio opera, pero es vulnerable ante imprevistos.",
            f"<b>Costos variables.</b> Representan <b>${costos_variables:,.0f}</b> "
            f"({costos_variables/total_costos*100:.0f}% del total). Revisa eficiencias en procesos.",
            f"<b>Meta de margen.</b> Para alcanzar el 20%, necesitas incrementar ingresos en al menos "
            f"<b>${(total_costos / 0.80) - ingresos:,.0f}</b> sin aumentar costos.",
            "<b>Diversificación.</b> Considera líneas de productos o servicios complementarios que "
            "aprovechen la infraestructura actual.",
            f"<b>Referencia sectorial.</b> El margen promedio del dataset es <b>{prom_margen:.1f}%</b>. "
            f"{'Estás por encima del promedio.' if margen_utilidad > prom_margen else 'Estás por debajo del promedio; hay oportunidad de mejora.'}",
            f"<b>Liquidez.</b> Mantén un fondo de reserva equivalente a 3 meses de costos fijos "
            f"(<b>${costos_fijos * 3:,.0f}</b>).",
        ]
    else:
        recomendaciones = [
            f"<b>Desempeño saludable.</b> Margen de utilidad del <b>{margen_utilidad:.1f}%</b>. "
            "La operación es financieramente sostenible.",
            f"<b>Reinversión.</b> Con un saldo neto de <b>${saldo_neto:,.0f}</b>, considera destinar "
            "al menos el 30% a expansión: marketing, tecnología o capacidad productiva.",
            "<b>Escalabilidad.</b> Analiza qué tan replicables son tus procesos para crecer "
            "en nuevos canales o mercados sin comprometer el margen.",
            "<b>Distribución del excedente.</b> Una estructura sugerida: 20% reserva de emergencia, "
            "50% reinversión, 30% retiro del emprendedor.",
            f"<b>Posición competitiva.</b> Superas el promedio histórico en <b>${saldo_neto - prom_profit:,.0f}</b>. "
            "Documenta tus prácticas como ventaja competitiva.",
            "<b>Control de costos.</b> Fija un límite máximo de costos fijos del 35% de ingresos "
            "para proteger el margen ante futuras expansiones.",
        ]

    for rec in recomendaciones:
        st.markdown(f'<div class="rec-card">{rec}</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Guardar en BD ────────────────────────────────────────────────────────
    token = st.session_state.get("jwt_token")

    if token:
        ok, msg_api = api_guardar_registro(ingresos, costos_fijos, costos_variables, nivel_riesgo, token)
        if ok:
            st.toast(f"Análisis guardado correctamente.", icon="✓")
        else:
            st.toast(f"Error al guardar: {msg_api}", icon="✗")
    else:
        st.info(
            "**Inicia sesión** desde la barra lateral para guardar este análisis "
            "en la base de datos y llevar un historial de tu evolución.",
        )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Resumen ejecutivo ────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Resumen ejecutivo</div>', unsafe_allow_html=True)

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.markdown(f"""
| Indicador | Tu empresa | Promedio histórico |
|-----------|-----------|-------------------|
| Ingresos | ${ingresos:,.0f} | ${prom_sales:,.0f} |
| Costos totales | ${total_costos:,.0f} | ${prom_cogs:,.0f} |
| Saldo neto | ${saldo_neto:,.0f} | ${prom_profit:,.0f} |
| Margen neto | {margen_utilidad:.1f}% | {prom_margen:.1f}% |
| Nivel de riesgo | **{nivel_riesgo}** | — |
        """)
    with col_res2:
        ratio_ci  = (total_costos / ingresos * 100) if ingresos > 0 else 0
        efic_hist = ((saldo_neto - prom_profit) / abs(prom_profit) * 100) if prom_profit != 0 else 0
        st.markdown(f"""
| Métrica derivada | Valor |
|-----------------|-------|
| Ratio costo/ingreso | {ratio_ci:.1f}% |
| Costos fijos (% total) | {costos_fijos/total_costos*100:.1f}% |
| Costos variables (% total) | {costos_variables/total_costos*100:.1f}% |
| Eficiencia vs. histórico | {efic_hist:+.1f}% |
| Empresas similares en dataset | {len(df_similar):,} |
        """)


# ─────────────────────────────────────────────────────────────────────────────
# ESTADO INICIAL
# ─────────────────────────────────────────────────────────────────────────────
else:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.info(
        "Ingresa los datos de tu emprendimiento en el formulario y presiona **Analizar emprendimiento** "
        "para obtener el análisis completo."
    )

    st.markdown('<div class="section-title">Vista previa del dataset histórico</div>', unsafe_allow_html=True)
    cols_prev = [c for c in ["Segment", "Country", "Product", "Sales", "COGS", "Profit", "Year"] if c in df.columns]
    st.dataframe(
        df[cols_prev]
        .rename(columns={"Sales": "Ingresos", "COGS": "Costos", "Profit": "Ganancia"})
        .head(10)
        .style.format({"Ingresos": "${:,.0f}", "Costos": "${:,.0f}", "Ganancia": "${:,.0f}"}),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Estadísticas descriptivas del dataset</div>', unsafe_allow_html=True)

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric("Venta promedio",    f"${df['Sales'].mean():,.0f}")
    col_s2.metric("Costo promedio",    f"${df['COGS'].mean():,.0f}")
    col_s3.metric("Ganancia promedio", f"${df['Profit'].mean():,.0f}")
    col_s4.metric("Margen promedio",   f"{(df['Profit'].mean() / df['Sales'].mean() * 100):.1f}%")


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:40px 0 20px;color:rgba(200,200,230,0.2);font-size:11px;letter-spacing:0.5px;">
    Plataforma de Análisis de Microemprendimientos &mdash; Proyecto Universitario
</div>
""", unsafe_allow_html=True)
