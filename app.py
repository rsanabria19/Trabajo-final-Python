import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

st.set_page_config(
    page_title="DINAGUA - Análisis de demora de trámite de solicitud de derechos de uso de agua subterránea",
    page_icon="💧",
    layout="wide"
)

# ==========================================================
# TÍTULO
# ==========================================================

# Título principal de la aplicación pública
st.markdown("<h1 style='text-align: center;'>💧 Solicitud de derechos de uso de agua subterránea - Tiempos de demora de trámite</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #7f8c8d;'>Sistema de Información Hídrica (SIH) – Dinagua</h3>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; font-size: 1.1em;'>Esta aplicación interactiva permite explorar el comportamiento histórico de los tiempos de resolución de expedientes de solicitudes de uso de agua subterránea, filtrando por rangos temporales y analizando el impacto de variables clave.</p>", unsafe_allow_html=True)

# ==========================================================
# CARGA DE DATOS
# ==========================================================

@st.cache_data
def cargar_datos():
    return pd.read_csv("data/processed/water_processed.csv")

df = cargar_datos()

# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.markdown("# 🎛️ Filtros")
st.sidebar.markdown(
    """
    Utilice el siguiente control para explorar
    distintos rangos de demora total del trámite 
    de solicitud de derechos de uso de agua subterránea.
    """
)

# ----------------------------------------------------------
# FILTRO 1 - DEMORA TOTAL
# ----------------------------------------------------------

min_demora = int(df["Demora_Total"].min())
max_demora = int(df["Demora_Total"].max())

rango_demora = st.sidebar.slider(
    "Rango de demora total (días)",
    min_value=min_demora,
    max_value=max_demora,
    value=(min_demora, max_demora)
)

# ----------------------------------------------------------
# FILTRO 2 - DEPARTAMENTO
# ----------------------------------------------------------

departamentos = st.sidebar.multiselect(
    "Departamento",
    options=sorted(df["Departamento"].dropna().unique())
)

# ----------------------------------------------------------
# FILTRO 3 - REGIONAL
# ----------------------------------------------------------

regionales = st.sidebar.multiselect(
    "Oficina Regional",
    options=sorted(df["Regional"].dropna().unique())
)

# ==========================================================
# APLICACIÓN DE FILTROS
# ==========================================================

df_filtrado = df.copy()

# Filtro por demora total
df_filtrado = df_filtrado[
    (df_filtrado["Demora_Total"] >= rango_demora[0]) &
    (df_filtrado["Demora_Total"] <= rango_demora[1])
]

# Filtro por departamento
if departamentos:
    df_filtrado = df_filtrado[
        df_filtrado["Departamento"].isin(departamentos)
    ]

# Filtro por regional
if regionales:
    df_filtrado = df_filtrado[
        df_filtrado["Regional"].isin(regionales)
    ]
# Filtro por registros seleccionados
st.metric(
    "Registros seleccionados",
    f"{len(df_filtrado):,}"
)

# ==========================================================
# INDICADORES PRINCIPALES
# ==========================================================

st.header("📋 Indicadores principales")

if not df_filtrado.empty:

    total_perforaciones = len(df_filtrado)

    mediana_caudal = df_filtrado["Caudal"].median()

    mediana_volumen = df_filtrado["Volumen"].median()

    volumen_total = df_filtrado["Volumen"].sum()

    mediana_demora_tecnica = df_filtrado["Demora_Tecnica"].median()

    mediana_demora_registral = df_filtrado["Demora_Registral"].median()

    mediana_demora_total = df_filtrado["Demora_Total"].median()

    pendientes = (
        df_filtrado["Estado"]
        .astype(str)
        .str.upper()
        .str.contains("ESTUDIO|PENDIENTE", na=False)
        .sum()
    )

    # ------------------------------------------------------
    # FILA 1
    # ------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Perforaciones registradas",
        f"{total_perforaciones:,}"
    )

    col2.metric(
        "Mediana de caudal (m3)",
        f"{mediana_caudal:.2f}"
    )

    col3.metric(
        "Mediana de volumen (m3/año)",
        f"{mediana_volumen:,.0f}"
    )

    col4.metric(
        "Volumen total extraído (m3/año)",
        f"{volumen_total:,.0f}"
    )

    # ------------------------------------------------------
    # FILA 2
    # ------------------------------------------------------

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Mediana demora técnica",
        f"{mediana_demora_tecnica:.0f} días"
    )

    col6.metric(
        "Mediana demora registral",
        f"{mediana_demora_registral:.0f} días"
    )

    col7.metric(
        "Mediana demora total",
        f"{mediana_demora_total:.0f} días"
    )



    # ------------------------------------------------------
    # USOS DEL AGUA
    # ------------------------------------------------------

    st.subheader("💧 Perforaciones según uso")

    usos = (
        df_filtrado["Uso"]
        .value_counts()
        .reset_index()
    )

    usos.columns = ["Uso", "Cantidad"]

    # Tabla

    st.dataframe(
        usos,
        use_container_width=True,
        hide_index=True
    )
    # ------------------------------------------------------
    # GRÁFICO DE BARRAS SEGÚN USO
    # ------------------------------------------------------

    fig_uso, ax_uso = plt.subplots(figsize=(8, 4))

    colores_uso = {
        "Riego": "#4C72B0",  # azul (similar al actual)
        "Otros usos agropecuarios": "green",
        "Industrial": "gray",
        "Otros usos": "gold",
        "Consumo humano": "skyblue",
        "Usos no consuntivos": "purple"
    }

    sns.barplot(
        data=usos,
        x="Uso",
        y="Cantidad",
        hue="Uso",
        palette=colores_uso,
        legend=False,
        ax=ax_uso
    )

    ax_uso.set_title(
        "Cantidad de perforaciones según uso"
    )

    ax_uso.set_xlabel("Uso")

    ax_uso.set_ylabel("Cantidad")

    plt.xticks(rotation=45)

    st.pyplot(fig_uso)



# ==========================================================
# HISTOGRAMA DEL TARGET
# ==========================================================

st.header("📊 Distribución de la demora total")

fig1, ax1 = plt.subplots(figsize=(8, 4))

sns.histplot(
    df_filtrado["Demora_Total"],
    bins=30,
    kde=True,
    ax=ax1
)

ax1.set_title("Distribución de demora total")
ax1.set_xlabel("Días")
ax1.set_ylabel("Frecuencia")

st.pyplot(fig1)

# ==========================================================
# SCATTER PLOT
# ==========================================================

st.header("🔍 Influencia de la demora técnica sobre demora total")

fig2, ax2 = plt.subplots(figsize=(8, 5))

sns.scatterplot(
    data=df_filtrado,
    x="Demora_Tecnica",
    y="Demora_Total",
    alpha=0.7,
    ax=ax2
)

ax2.set_title(
    "Demora técnica vs demora total"
)

ax2.set_xlabel("Demora técnica (días)")
ax2.set_ylabel("Demora total (días)")

st.pyplot(fig2)

# ==========================================================
# COMPARACIÓN DE DEMORAS
# ==========================================================

st.header("📦 Comparación de las distribuciones de demora de trámite")

if not df_filtrado.empty:

    fig_box, ax_box = plt.subplots(figsize=(10, 6))

    sns.boxplot(
        data=df_filtrado[
            [
                "Demora_Tecnica",
                "Demora_Registral",
                "Demora_Total"
            ]
        ],
        ax=ax_box
    )

    ax_box.set_title(
        "Comparación de las distribuciones de demora"
    )

    ax_box.set_ylabel(
        "Cantidad de días"
    )

    ax_box.set_xlabel(
        "Tipo de demora"
    )

    st.pyplot(fig_box)

else:
    st.warning(
        "No existen registros para los filtros seleccionados."
    )

# ==========================================================
# MAPA
# ==========================================================

st.header("🗺️ Distribución geográfica de las obras de aprovechamiento de agua subterránea con derecho de uso otorgado por Dinagua")

mapa = df_filtrado[
    (df_filtrado["Latitud"].between(-35.5, -30.0)) &
    (df_filtrado["Longitud"].between(-59.0, -53.0))
][["Latitud", "Longitud"]]

mapa = mapa.rename(
    columns={
        "Latitud": "lat",
        "Longitud": "lon"
    }
)

st.map(mapa)

# ==========================================================
# DATOS FILTRADOS
# ==========================================================

st.header("📄 DataFrame resultante luego de realizar el EDA")

st.dataframe(
    df_filtrado,
    use_container_width=True
)

st.caption(
    """
    Trabajo final de Python utilizando la base de datos del Sistema de Información Hídrica de Dinagua.

    Realizado por Romina Sanabria Maciera - junio 2026.

    Datos válidos al 7 de abril de 2026.
    """
)