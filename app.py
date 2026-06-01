import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la página institucional
st.set_page_config(
    page_title="Dinagua - Panel de gestión de trámites",
    page_icon="💧",
    layout="wide"
)

# Título principal de la aplicación pública
st.markdown("<h1 style='text-align: center;'>💧 Solicitud de derechos de uso de agua subterránea - Tiempos de demora de trámite</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Sistema de Información Hídrica (SIH) – Dinagua</h3>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; font-size: 1.1em;'>Esta aplicación interactiva permite explorar el comportamiento histórico de los tiempos de resolución de expedientes de solicitudes de uso de agua subterránea, filtrando por rangos temporales y analizando el impacto de variables clave.</p>", unsafe_allow_html=True)


# CARGA DE DATOS PROCESADOS (se utilizará el dataset limpio que guardamos en el Paso 7)
@st.cache_data
def load_data():
    # Cargar el archivo unificado exportado con pathlib
    df = pd.read_csv("data/processed/water_processed.csv")
    return df


try:
    df_modelo = (load_data())
except FileNotFoundError:
    st.error(
        "⚠️ No se encontró el archivo 'tramites_procesados.csv' en 'data/processed/'. Asegúrate de haber ejecutado las celdas de guardado en tu notebook.")
    st.stop()

# ==============================================================================
# SIDEBAR DE CONTROL (st.sidebar)
# ==============================================================================
st.sidebar.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6A6R4Q7ZpY6kGvYk8rX8Fqf3m9u_JzCg2XQ&s",
                 width=100)  # Opcional: Logo genérico o estético
st.sidebar.markdown("## 🎛️ Panel de control")
st.sidebar.markdown("Utilice los controles de abajo para segmentar los expedientes bajo análisis.")

# Filtro 1: Rango de días de demora (st.slider) basado en los mínimos y máximos reales
min_dias = int(df_modelo['Dias_Demora'].min())
max_dias = int(df_modelo['Dias_Demora'].max())

rango_seleccionado = st.sidebar.slider(
    "Seleccione el rango de días de demora:",
    min_value=min_dias,
    max_value=max_dias,
    value=(min_dias, int(df_modelo['Dias_Demora'].quantile(0.95))),
    # Por defecto acotado al percentil 95 para evitar distorsión inicial de outliers
    step=1
)

# Filtro 2: Selector de departamentos clave (identificados por SelectKBest)
departamentos_clave = ["DURAZNO", "PAYSANDÚ", "SALTO", "SAN JOSÉ"]

depto_seleccionado = st.sidebar.selectbox(
    "Filtrar por foco de departamento:",
    ["TODOS"] + departamentos_clave
)

# Nota metodológica para el usuario/profesor en el menú lateral
st.sidebar.caption(
    "💡 *Nota: Se muestran únicamente los departamentos seleccionados por el algoritmo "
    "SelectKBest por su alto impacto estadístico en los tiempos de demora.*"
)


# =======================================================================
# APLICACIÓN DE LOS FILTROS AL DATAFRAME ORIGINAL
# =======================================================================

# 1. Filtro por el rango de días de demora (Slider)
df_filtrado = df_modelo[
    (df_modelo['Dias_Demora'] >= rango_seleccionado[0]) &
    (df_modelo['Dias_Demora'] <= rango_seleccionado[1])
]

# 2. Filtro por Departamento (Selectbox)
if depto_seleccionado != "TODOS":
    columna_depto = f"Departamento_{depto_seleccionado}"
    if columna_depto in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado[columna_depto] == 1]


# ==============================================================================
# RESUMEN DESCRIPTIVO (Métricas dinámicas)
# ==============================================================================
st.subheader("📋 Resumen estadístico descriptivo (datos filtrados)")

# Calculamos las métricas clave del dataset resultante
if not df_filtrado.empty:
    media_demora = df_filtrado['Dias_Demora'].mean()
    mediana_demora = df_filtrado['Dias_Demora'].median()
    desviacion_demora = df_filtrado['Dias_Demora'].std()
    min_actual = df_filtrado['Dias_Demora'].min()
    max_actual = df_filtrado['Dias_Demora'].max()
    rango_actual = max_actual - min_actual

    # Mostramos métricas destacadas en tarjetas visuales (st.columns)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Registros", f"{len(df_filtrado):,}")
    col2.metric("Media de Demora", f"{media_demora:.1f} días")
    col3.metric("Mediana de Demora", f"{mediana_demora:.1f} días")
    col4.metric("Rango Operativo", f"{rango_actual:.0f} días")

    # Tabla detallada con los percentiles solicitados por la letra del proyecto
    st.markdown("**Cuadro estadístico detallado (Pandas describe)**")
    st.dataframe(df_filtrado[['Demora en día', 'Es riego']].describe().T)
else:
    st.warning("❌ No hay registros que coincidan con el rango seleccionado en el slider.")

st.markdown("---")

# ==============================================================================
# VISUALIZACIÓN DINÁMICA
# ==============================================================================
st.subheader("📊 Análisis gráfico interactivo")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("### 📈 Distribución del Target (`demora en día`)")
    if not df_filtrado.empty:
        fig_hist, ax_hist = plt.subplots(figsize=(6, 4))
        sns.histplot(df_filtrado['Dias_Demora'], kde=True, color="#2c3e50", ax=ax_hist, bins=25)
        ax_hist.set_title("Histograma de frecuencias de femora")
        ax_hist.set_xlabel("Días transcurridos")
        ax_hist.set_ylabel("Cantidad de expedientes")
        st.pyplot(fig_hist)
    else:
        st.info("Sin datos para graficar histograma.")

with col_graf2:
    st.markdown("### 🔍 Relación: impacto del uso de riego")
    if not df_filtrado.empty:
        fig_scatter, ax_scatter = plt.subplots(figsize=(6, 4))
        # Generamos un scatter plot o boxplot que asocie el comportamiento continuo frente a Riego
        sns.stripplot(data=df_filtrado, x='Es_Riego', y='Dias_Demora', palette="Blues", alpha=0.6, ax=ax_scatter,
                      jitter=0.2)
        ax_scatter.set_title("Dispersión de Tiempos por Tipo de Uso")
        ax_scatter.set_xlabel("¿Es de Riego? (0 = No, 1 = Sí)")
        ax_scatter.set_ylabel("Días de Demora")
        st.pyplot(fig_scatter)
    else:
        st.info("Sin datos para graficar dispersión.")

st.markdown("---")
st.caption("Estructura técnica desarrollada para el proyecto final de ciencia de datos aplicado a Dinagua — 2026.")