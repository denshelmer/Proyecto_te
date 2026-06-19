"""
=============================================================================
 Plataforma Cloud para Análisis de Microemprendimientos
 y Predicción de Sostenibilidad Económica
=============================================================================
 Ejecución local : streamlit run app.py
 Deploy gratuito : Streamlit Community Cloud  (share.streamlit.io)
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Plataforma de Sostenibilidad · MicroEmprendimientos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS PERSONALIZADO — UI Premium
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Fondo general */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #1a1a3e, #24243e);
    color: #e8e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04);
    border-right: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
}

/* Cards métricas */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 18px 20px;
    backdrop-filter: blur(8px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(130,80,255,0.25);
}

/* Botón principal */
.stButton > button {
    background: linear-gradient(135deg, #6c63ff, #a855f7);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 32px;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 0.4px;
    width: 100%;
    transition: all 0.3s ease;
    box-shadow: 0 6px 24px rgba(108,99,255,0.35);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(108,99,255,0.55);
}

/* Inputs */
.stNumberInput input, .stSelectbox select {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    font-size: 15px !important;
}

/* Encabezados de sección */
.section-title {
    font-size: 22px;
    font-weight: 700;
    color: #c4b5fd;
    margin-bottom: 6px;
    letter-spacing: -0.3px;
}
.section-sub {
    font-size: 13px;
    color: rgba(200,200,230,0.55);
    margin-bottom: 20px;
}

/* Badge de riesgo */
.badge {
    display: inline-block;
    padding: 6px 18px;
    border-radius: 50px;
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-alto  { background: rgba(239,68,68,0.2);  border: 1.5px solid #ef4444; color:#f87171; }
.badge-medio { background: rgba(245,158,11,0.2); border: 1.5px solid #f59e0b; color:#fbbf24; }
.badge-bajo  { background: rgba(34,197,94,0.2);  border: 1.5px solid #22c55e; color:#4ade80; }

/* Recomendaciones */
.rec-card {
    background: rgba(255,255,255,0.05);
    border-left: 4px solid #6c63ff;
    border-radius: 0 12px 12px 0;
    padding: 16px 20px;
    margin-bottom: 10px;
    font-size: 14px;
    line-height: 1.6;
    color: #d1d0e8;
}

/* Divider */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(108,99,255,0.5), transparent);
    margin: 28px 0;
}

/* Tabla comparativa */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Header banner */
.hero-banner {
    background: linear-gradient(135deg, rgba(108,99,255,0.25), rgba(168,85,247,0.15));
    border: 1px solid rgba(108,99,255,0.3);
    border-radius: 20px;
    padding: 32px 36px;
    margin-bottom: 28px;
    backdrop-filter: blur(10px);
}
.hero-title {
    font-size: 32px;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #c084fc, #e879f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
}
.hero-sub {
    font-size: 15px;
    color: rgba(200,200,230,0.65);
    font-weight: 400;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 1. CARGA DEL DATASET
# ─────────────────────────────────────────────────────────────────────────────
DATASET_FILE = "04-01-Financial Sample Data.xlsx"

@st.cache_data(show_spinner=False)
def cargar_dataset(path: str) -> pd.DataFrame:
    """Lee el archivo Excel y limpia las columnas numéricas."""
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip()

    # Limpiar valores numéricos que vienen como string con $ , ( )
    cols_numericas = ["Gross Sales", "Sales", "COGS", "Profit",
                      "Discounts", "Units Sold", "Sale Price",
                      "Manufacturing Price"]
    for col in cols_numericas:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = (
                    df[col].astype(str)
                    .str.replace(r"[\$,\(\)\s]", "", regex=True)
                    .str.replace(r"^-$", "0", regex=True)
                    .pipe(pd.to_numeric, errors="coerce")
                )
    df.dropna(subset=["Sales", "COGS", "Profit"], inplace=True)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Verificación de existencia del archivo
# ─────────────────────────────────────────────────────────────────────────────
if not os.path.exists(DATASET_FILE):
    st.error(
        f"⚠️ No se encontró el archivo **'{DATASET_FILE}'** en la carpeta del proyecto.\n\n"
        "Asegúrate de colocar el dataset en la misma carpeta que `app.py` y volver a ejecutar."
    )
    st.stop()

with st.spinner("⏳ Cargando dataset histórico…"):
    df = cargar_dataset(DATASET_FILE)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — Información del dataset
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📂 Dataset Histórico")
    st.markdown(f"**Registros cargados:** `{len(df):,}`")
    st.markdown(f"**Variables disponibles:** `{len(df.columns)}`")
    st.markdown("---")

    segmentos = ["Todos"] + sorted(df["Segment"].dropna().unique().tolist()) if "Segment" in df.columns else ["Todos"]
    segmento_sel = st.selectbox("🏷️ Filtrar por segmento", segmentos)

    paises = ["Todos"] + sorted(df["Country"].dropna().unique().tolist()) if "Country" in df.columns else ["Todos"]
    pais_sel = st.selectbox("🌍 Filtrar por país", paises)

    st.markdown("---")
    st.markdown(
        "<small style='color:rgba(200,200,230,0.4);'>Plataforma universitaria · Sin IA · "
        "Análisis 100% basado en datos históricos</small>",
        unsafe_allow_html=True
    )

# Aplicar filtros de sidebar al df de referencia
df_ref = df.copy()
if segmento_sel != "Todos" and "Segment" in df.columns:
    df_ref = df_ref[df_ref["Segment"] == segmento_sel]
if pais_sel != "Todos" and "Country" in df.columns:
    df_ref = df_ref[df_ref["Country"] == pais_sel]


# ─────────────────────────────────────────────────────────────────────────────
# BANNER HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <div class="hero-title">📊 Plataforma de Análisis de Microemprendimientos</div>
  <div class="hero-sub">
    Herramienta de sostenibilidad económica · Comparación con datos históricos reales ·
    Recomendaciones automáticas basadas en lógica financiera
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 2. FORMULARIO DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">💼 Ingresa los Datos de tu Emprendimiento</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Introduce las variables financieras de tu negocio del último mes</div>', unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    ingresos = st.number_input(
        "💰 Ingresos Mensuales (USD)",
        min_value=0.0, value=15000.0, step=500.0,
        help="Total de ventas o ingresos del mes",
        key="input_ingresos"
    )
with col_f2:
    costos_fijos = st.number_input(
        "🏢 Costos Fijos (USD)",
        min_value=0.0, value=5000.0, step=500.0,
        help="Alquiler, salarios fijos, servicios, etc.",
        key="input_costos_fijos"
    )
with col_f3:
    costos_variables = st.number_input(
        "⚙️ Costos Variables (USD)",
        min_value=0.0, value=4000.0, step=500.0,
        help="Materias primas, comisiones, empaque, etc.",
        key="input_costos_variables"
    )

_, col_btn, _ = st.columns([2, 1, 2])
with col_btn:
    analizar = st.button("🔍 Analizar mi Emprendimiento", key="btn_analizar")


# ─────────────────────────────────────────────────────────────────────────────
# 3. PROCESAMIENTO ARITMÉTICO + ANÁLISIS
# ─────────────────────────────────────────────────────────────────────────────
if analizar:
    total_costos   = costos_fijos + costos_variables
    saldo_neto     = ingresos - total_costos
    margen_utilidad = (saldo_neto / ingresos * 100) if ingresos > 0 else 0.0
    punto_equilibrio = total_costos  # Ingresos mínimos para no perder

   # ── Nivel de riesgo financiero con MACHINE LEARNING ─────────────────────
    # ── Nivel de riesgo financiero con MACHINE LEARNING ─────────────────────
    import joblib
    import os
    import pandas as pd

    try:
        # 1. Cargar el modelo definitivo que aprendió del Excel
        modelo_ia = joblib.load('modelo_riesgo_definitivo.pkl')
        
        # 2. Empaquetar los datos EXACTAMENTE como los leyó la IA al entrenar
        datos_entrada = pd.DataFrame([[ingresos, total_costos]], columns=['Sales', 'COGS'])
        
        # 3. Hacer la predicción matemática
        prediccion = modelo_ia.predict(datos_entrada)[0]
        
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
        st.warning(f"⚠️ Error cargando la IA: {e}")
        nivel_riesgo = "DESCONOCIDO"
        badge_class  = "badge-medio"
        color_riesgo = "#6c63ff"
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # 5A. MÉTRICAS PRINCIPALES
    # ─────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📈 Resultados Financieros</div>', unsafe_allow_html=True)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("💰 Ingresos",       f"${ingresos:,.0f}")
    m2.metric("💸 Total Costos",   f"${total_costos:,.0f}", delta=f"-${total_costos:,.0f}", delta_color="inverse")
    m3.metric("🏦 Saldo Neto",     f"${saldo_neto:,.0f}",  delta=f"{'Ganancia' if saldo_neto >= 0 else 'Pérdida'}")
    m4.metric("📊 Margen Neto",    f"{margen_utilidad:.1f}%")
    m5.metric("⚖️ Punto Equilibrio", f"${punto_equilibrio:,.0f}")

    # Nivel de riesgo visual
    st.markdown(f"""
    <div style="margin:22px 0 6px;">
        <span style="font-size:15px;color:rgba(200,200,230,0.6);font-weight:500;">
            🚦 Nivel de Riesgo Financiero:
        </span>&nbsp;&nbsp;
        <span class="badge {badge_class}">{nivel_riesgo}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # 4. COMPARACIÓN CON EL DATASET
    # ─────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🔍 Comparativa con Empresas Históricas del Dataset</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Empresas similares basadas en rango de ingresos (±40%)</div>', unsafe_allow_html=True)

    # Filtrar empresas con ingresos similares (±40 %)
    rango_inf = ingresos * 0.60
    rango_sup = ingresos * 1.40
    df_similar = df_ref[(df_ref["Sales"] >= rango_inf) & (df_ref["Sales"] <= rango_sup)].copy()

    if len(df_similar) == 0:
        st.info("ℹ️ No se encontraron registros exactos en el rango. Se muestran las métricas promedio del dataset completo.")
        df_similar = df_ref.copy()
        modo_promedio = True
    else:
        modo_promedio = False

    # Estadísticas del grupo comparable
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
        if modo_promedio:
            st.caption(f"📌 Se muestran métricas del dataset completo ({len(df_ref):,} registros)")
        else:
            st.caption(f"📌 Se encontraron {len(df_similar):,} empresas en rango similar de ingresos")

    with col_chart:
        # Gráfico comparativo: usuario vs. promedio histórico
        categorias  = ["Ingresos", "Costos Totales", "Saldo Neto"]
        usuario_vals = [ingresos, total_costos, saldo_neto]
        historico_vals = [prom_sales, prom_cogs, prom_profit]

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(
            name="Tu Emprendimiento",
            x=categorias,
            y=usuario_vals,
            marker_color=["#6c63ff", "#a855f7", "#22c55e" if saldo_neto >= 0 else "#ef4444"],
            text=[f"${v:,.0f}" for v in usuario_vals],
            textposition="outside",
            textfont=dict(color="white", size=11)
        ))
        fig_comp.add_trace(go.Bar(
            name="Promedio Histórico",
            x=categorias,
            y=historico_vals,
            marker_color=["rgba(108,99,255,0.35)", "rgba(168,85,247,0.35)", "rgba(34,197,94,0.35)"],
            text=[f"${v:,.0f}" for v in historico_vals],
            textposition="outside",
            textfont=dict(color="rgba(200,200,230,0.7)", size=11)
        ))
        fig_comp.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#d1d0e8", family="Inter"),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickprefix="$"),
            title=dict(text="Tu empresa vs. Histórico", font=dict(size=14, color="#c4b5fd")),
            margin=dict(t=50, b=20, l=10, r=10),
            height=320,
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # GRÁFICOS ADICIONALES
    # ─────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📉 Panel Analítico Extendido</div>', unsafe_allow_html=True)

    col_g1, col_g2, col_g3 = st.columns(3)

    # Donut: estructura de costos del usuario
    with col_g1:
        fig_donut = go.Figure(go.Pie(
            labels=["Costos Fijos", "Costos Variables", "Saldo Neto" if saldo_neto > 0 else "Pérdida"],
            values=[costos_fijos, costos_variables, abs(saldo_neto)],
            hole=0.55,
            marker_colors=["#6c63ff", "#a855f7", "#22c55e" if saldo_neto > 0 else "#ef4444"],
            textfont=dict(color="white"),
        ))
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#d1d0e8", family="Inter"),
            title=dict(text="Estructura de Costos", font=dict(size=13, color="#c4b5fd")),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
            margin=dict(t=50, b=10, l=10, r=10),
            height=280,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # Medidor de margen de utilidad
    with col_g2:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=margen_utilidad,
            delta={"reference": prom_margen, "valueformat": ".1f", "suffix": "%"},
            number={"suffix": "%", "font": {"size": 28, "color": "#e8e8f0"}},
            gauge={
                "axis": {"range": [-50, 60], "tickcolor": "#a78bfa"},
                "bar": {"color": color_riesgo},
                "steps": [
                    {"range": [-50, 0],  "color": "rgba(239,68,68,0.15)"},
                    {"range": [0, 10],   "color": "rgba(245,158,11,0.15)"},
                    {"range": [10, 20],  "color": "rgba(245,158,11,0.1)"},
                    {"range": [20, 60],  "color": "rgba(34,197,94,0.12)"},
                ],
                "threshold": {
                    "line": {"color": "#a78bfa", "width": 2},
                    "thickness": 0.75,
                    "value": prom_margen
                },
                "bgcolor": "rgba(0,0,0,0)",
            },
            title={"text": "Margen de Utilidad Neto<br><span style='font-size:11px;color:#a78bfa'>△ vs promedio histórico</span>",
                   "font": {"size": 13, "color": "#c4b5fd"}}
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#d1d0e8", family="Inter"),
            margin=dict(t=40, b=10, l=20, r=20),
            height=280,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Distribución de Profit en el dataset comparable
    with col_g3:
        fig_hist = px.histogram(
            df_similar, x="Profit", nbins=25,
            color_discrete_sequence=["#6c63ff"],
            labels={"Profit": "Ganancia Histórica (USD)"},
            title="Distribución de Ganancias (Dataset)",
        )
        fig_hist.add_vline(
            x=saldo_neto, line_dash="dash", line_color="#e879f9",
            annotation_text="Tu empresa", annotation_font_color="#e879f9"
        )
        fig_hist.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#d1d0e8", family="Inter"),
            title=dict(font=dict(size=13, color="#c4b5fd")),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            margin=dict(t=50, b=20, l=10, r=10),
            height=280,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────
    # 5B. RECOMENDACIONES AUTOMÁTICAS (IF/ELSE puro)
    # ─────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">💡 Recomendaciones Automáticas</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">Basadas en análisis del riesgo: <b>{nivel_riesgo}</b></div>', unsafe_allow_html=True)

    if nivel_riesgo == "ALTO":
        recomendaciones = [
            "🔴 **Situación crítica:** Tu emprendimiento opera con pérdidas. El saldo neto negativo indica que los costos "
            f"superan los ingresos en **${abs(saldo_neto):,.0f}**. Requiere acción inmediata.",
            "📉 **Reducción de costos:** Identifica y elimina todos los costos no esenciales. Renegocia contratos de "
            "proveedores y busca alternativas más económicas para insumos.",
            "📈 **Incremento de ingresos:** Evalúa aumentar precios si la elasticidad del mercado lo permite, o "
            "diversifica hacia productos/servicios de mayor margen.",
            f"⚖️ **Punto de equilibrio:** Necesitas generar al menos **${punto_equilibrio:,.0f}** en ingresos para "
            "cubrir costos. Establece este valor como meta mínima mensual.",
            "🆘 **Busca financiamiento de emergencia:** Evalúa líneas de crédito, inversores ángeles o programas "
            "gubernamentales para microempresas en crisis.",
            f"📊 **Comparativa histórica:** Las empresas similares del dataset generan un promedio de "
            f"**${prom_profit:,.0f}** de ganancia. Analiza sus modelos de negocio como referencia.",
        ]
    elif nivel_riesgo == "MEDIO":
        recomendaciones = [
            f"🟡 **Zona de atención:** Tu margen de utilidad es del **{margen_utilidad:.1f}%**, que está por debajo "
            "del umbral saludable del 20%. El negocio sobrevive, pero es vulnerable a imprevistos.",
            "📊 **Optimización de costos variables:** Tus costos variables representan "
            f"**${costos_variables:,.0f}** ({costos_variables/total_costos*100:.0f}% del total). "
            "Busca eficiencias en procesos productivos.",
            "🎯 **Meta de margen:** Apunta a un margen mínimo del 20% aumentando ingresos en al menos "
            f"**${(total_costos / 0.80) - ingresos:,.0f}** sin incrementar costos.",
            "🔄 **Diversificación:** Considera añadir líneas de productos/servicios complementarios que "
            "aprovechen tu infraestructura actual sin aumentar costos fijos.",
            f"💡 **Benchmark:** El promedio histórico del dataset muestra un margen del **{prom_margen:.1f}%**. "
            f"{'Estás por encima del promedio sector.' if margen_utilidad > prom_margen else 'Estás por debajo del promedio sector, hay oportunidad de mejora.'}",
            "📅 **Planificación de liquidez:** Con márgenes ajustados, mantén al menos 3 meses de costos fijos "
            f"(**${costos_fijos * 3:,.0f}**) como fondo de emergencia.",
        ]
    else:  # BAJO
        recomendaciones = [
            f"🟢 **¡Excelente desempeño!** Tu margen de utilidad del **{margen_utilidad:.1f}%** indica una operación "
            "financieramente saludable y sostenible.",
            "📈 **Reinversión estratégica:** Con un saldo neto positivo de **${:,.0f}**, considera reinvertir al menos "
            "el 30% en expansión: marketing, tecnología o capacidad productiva.".format(saldo_neto),
            "🚀 **Escalabilidad:** Evalúa si el modelo actual puede escalar. Analiza qué tan replicables son tus "
            "procesos para abrir nuevos canales o mercados.",
            f"💰 **Gestión del excedente:** Distribuye el saldo neto entre: reserva de emergencia (20%), "
            "reinversión (50%) y retiro del empresario (30%).",
            f"📊 **Posición competitiva:** Superas el promedio histórico del dataset en **${saldo_neto - prom_profit:,.0f}**. "
            "Documenta tus prácticas exitosas como ventaja competitiva.",
            "🔒 **Protege tu margen:** Establece controles de costos para que la expansión no erosione el margen. "
            "Fija un límite máximo de costos fijos del 35% de ingresos.",
        ]

    for rec in recomendaciones:
        st.markdown(f'<div class="rec-card">{rec}</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)




# ─────────────────────────────────────────────────────────────────────
    # REEMPLAZO DE LA API POR EL CSV LOCAL (CONTINGENCIA)
    # ─────────────────────────────────────────────────────────────────────
    import csv
    import os
    from datetime import datetime

    try:
        archivo_db = 'base_auditoria.csv'
        
        if not os.path.exists(archivo_db):
            with open(archivo_db, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(['Fecha', 'Ingresos', 'Costos Fijos', 'Costos Variables', 'Riesgo Predicho', 'Estado Real'])

        nuevo_registro = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ingresos, costos_fijos, costos_variables, nivel_riesgo, "Pendiente"]
        with open(archivo_db, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(nuevo_registro)
            
        st.toast('✅ Registro guardado en el sistema de auditoría local', icon='💾')
    except Exception as e:
        st.toast(f'⚠️ Error al guardar: {e}', icon='🔌')

    # ─────────────────────────────────────────────────────────────────────
    # RESUMEN EJECUTIVO
    # ─────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Resumen Ejecutivo</div>', unsafe_allow_html=True)

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.markdown(f"""
        | Indicador | Tu empresa | Promedio histórico |
        |-----------|-----------|-------------------|
        | Ingresos | ${ingresos:,.0f} | ${prom_sales:,.0f} |
        | Costos Totales | ${total_costos:,.0f} | ${prom_cogs:,.0f} |
        | Saldo Neto | ${saldo_neto:,.0f} | ${prom_profit:,.0f} |
        | Margen Neto | {margen_utilidad:.1f}% | {prom_margen:.1f}% |
        | Nivel de Riesgo | **{nivel_riesgo}** | — |
        """)
    with col_res2:
        ratio_costo_ingreso = (total_costos / ingresos * 100) if ingresos > 0 else 0
        eficiencia_vs_hist  = ((saldo_neto - prom_profit) / abs(prom_profit) * 100) if prom_profit != 0 else 0

        st.markdown(f"""
        | Métrica Derivada | Valor |
        |-----------------|-------|
        | Ratio Costo/Ingreso | {ratio_costo_ingreso:.1f}% |
        | Costos fijos (% del total) | {costos_fijos/total_costos*100:.1f}% |
        | Costos variables (% del total) | {costos_variables/total_costos*100:.1f}% |
        | Eficiencia vs. histórico | {eficiencia_vs_hist:+.1f}% |
        | Empresas similares en dataset | {len(df_similar):,} |
        """)
# ─────────────────────────────────────────────────────────────────────────────
# ESTADO INICIAL (antes de pulsar Analizar)
# ─────────────────────────────────────────────────────────────────────────────
else:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.info(
        "👆 Ingresa los valores de tu emprendimiento en el formulario de arriba y pulsa "
        "**'Analizar mi Emprendimiento'** para obtener tu análisis completo.",
        icon="📊"
    )

    # Vista previa del dataset
    st.markdown('<div class="section-title">🗂️ Vista Previa del Dataset Histórico</div>', unsafe_allow_html=True)
    cols_prev = [c for c in ["Segment", "Country", "Product", "Sales", "COGS", "Profit", "Year"] if c in df.columns]
    st.dataframe(
        df[cols_prev]
        .rename(columns={"Sales": "Ingresos", "COGS": "Costos", "Profit": "Ganancia"})
        .head(10)
        .style.format({"Ingresos": "${:,.0f}", "Costos": "${:,.0f}", "Ganancia": "${:,.0f}"}),
        use_container_width=True,
        hide_index=True
    )

    # Estadísticas rápidas del dataset
    st.markdown("### 📊 Estadísticas Descriptivas del Dataset")
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric("📈 Venta Promedio",   f"${df['Sales'].mean():,.0f}")
    col_s2.metric("💸 Costo Promedio",   f"${df['COGS'].mean():,.0f}")
    col_s3.metric("🏦 Ganancia Promedio", f"${df['Profit'].mean():,.0f}")
    col_s4.metric("📊 Margen Promedio",
                  f"{(df['Profit'].mean() / df['Sales'].mean() * 100):.1f}%")

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:40px 0 20px;color:rgba(200,200,230,0.3);font-size:12px;">
    Plataforma Cloud de Análisis de Microemprendimientos · Proyecto Universitario ·
    Desarrollado con Streamlit + Pandas · Sin IA · 100% Open Source
</div>
""", unsafe_allow_html=True)
