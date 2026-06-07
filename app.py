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
    st.header("📋 Resumen descriptivo")

    st.markdown(
        """
        Estadísticas descriptivas calculadas sobre el conjunto de datos resultante
        luego de aplicar los filtros seleccionados.
        """
    )

    columnas_numericas = [
        "Demora_Tecnica",
        "Demora_Registral",
        "Demora_Total"
    ]

    resumen = df_filtrado[columnas_numericas].agg(
        [
            "mean",
            "median",
            "std",
            "min",
            lambda x: x.quantile(0.25),
            lambda x: x.quantile(0.75),
            "max"
        ]
    ).T

    resumen.columns = [
        "Media",
        "Mediana",
        "Desv. Std",
        "Mínimo",
        "Q1 (25%)",
        "Q3 (75%)",
        "Máximo"
    ]

    resumen["Rango"] = (
            resumen["Máximo"] -
            resumen["Mínimo"]
    )

    resumen = resumen[
        [
            "Mediana",
            "Media",
            "Desv. Std",
            "Mínimo",
            "Q1 (25%)",
            "Q3 (75%)",
            "Máximo",
            "Rango"
        ]
    ]

    st.dataframe(
        resumen.style.format("{:.2f}"),
        use_container_width=True
    )

    st.caption(
        """
        La tabla resume las principales medidas de tendencia central y dispersión
        para las variables de demora analizadas. Estas estadísticas permiten
        caracterizar el comportamiento general de los tiempos de tramitación y
        evaluar la presencia de variabilidad entre los expedientes.
        """
    )

    st.markdown("---")


    # ==========================================================
    # HISTOGRAMA DEL TARGET
    # ==========================================================

    st.header("📈 Análisis de la demora total de los trámites")

    st.markdown(
        """
        El siguiente gráfico permite observar cómo se distribuyen los tiempos
        totales de tramitación registrados en los expedientes analizados.
        """
    )

    fig1, ax1 = plt.subplots(figsize=(10, 5))

    sns.histplot(
        data=df_filtrado,
        x="Demora_Total",
        bins=40,
        color="#2E8B57",
        alpha=0.85,
        edgecolor="black",
        linewidth=0.3,
        kde=True,
        ax=ax1
    )

    media = df_filtrado["Demora_Total"].mean()
    mediana = df_filtrado["Demora_Total"].median()

    ax1.axvline(
        media,
        color="#1F3A5F",
        linestyle="-.",
        linewidth=2,
        label=f"Media: {media:.0f} días"
    )

    ax1.axvline(
        mediana,
        color="#E76F51",
        linestyle="--",
        linewidth=2,
        label=f"Mediana: {mediana:.0f} días"
    )

    ax1.set_title(
        "Distribución de los tiempos de tramitación",
        fontsize=15,
        fontweight="semibold"
    )

    ax1.set_xlabel("Demora total (días)")
    ax1.set_ylabel("Cantidad de trámites")

    ax1.grid(
        which="major",
        linestyle="--",
        linewidth=0.7,
        alpha=0.4
    )

    plt.tight_layout()

    st.pyplot(fig1)

    st.caption(
        """
        La mayor concentración de trámites se encuentra en determinados rangos de días,
        mientras que algunos casos presentan demoras considerablemente superiores al resto.
        La comparación entre la media y la mediana ayuda a identificar posibles valores
        extremos y el grado de asimetría de la distribución.
        """
    )

    st.markdown("---")

    # ==========================================================
    # SCATTER PLOT
    # ==========================================================

    st.header("🔍 Influencia de la demora técnica sobre la demora total")

    st.markdown(
        """
        El siguiente gráfico permite analizar la relación entre la demora técnica
        y la duración total de los trámites registrados.
        """
    )

    fig2, ax2 = plt.subplots(figsize=(10, 5))

    sns.regplot(
        data=df_filtrado,
        x="Demora_Tecnica",
        y="Demora_Total",
        scatter_kws={
            "alpha": 0.5,
            "s": 45,
            "color": "#2E8B57"
        },
        line_kws={
            "color": "#085041",
            "linewidth": 2
        },
        ax=ax2
    )

    ax2.set_title(
        "Relación entre demora técnica y demora total",
        fontsize=15,
        fontweight="semibold"
    )

    ax2.set_xlabel(
        "Demora técnica (días)",
        fontsize=11
    )

    ax2.set_ylabel(
        "Demora total (días)",
        fontsize=11
    )

    ax2.grid(
        which="major",
        linestyle="--",
        linewidth=0.7,
        alpha=0.4
    )

    sns.despine()

    plt.tight_layout()

    st.pyplot(fig2)

    st.caption(
        """
        Cada punto representa un trámite. La línea de tendencia resume el comportamiento
        general observado en los datos. Una pendiente positiva sugiere que los expedientes
        con mayores demoras técnicas tienden a presentar también mayores tiempos totales
        de tramitación.
        """
    )

    st.markdown("---")

    # ==========================================================
    # COMPARACIÓN DE DEMORAS
    # ==========================================================

    st.header("📦 Comparación de las distribuciones de demora")

    st.markdown(
        """
        El siguiente gráfico permite comparar la distribución de las demoras
        técnicas, registrales y totales observadas en los expedientes seleccionados.
        """
    )

    if not df_filtrado.empty:

        fig_box, ax_box = plt.subplots(figsize=(11, 5))

        palette = ["#2E8B57", "#5FA777", "#A8D5BA"]

        sns.boxplot(
            data=df_filtrado[
                [
                    "Demora_Tecnica",
                    "Demora_Registral",
                    "Demora_Total"
                ]
            ],
            palette=palette,
            width=0.55,
            ax=ax_box
        )

        ax_box.set_title(
            "Distribución de los distintos tipos de demora",
            fontsize=15,
            fontweight="semibold"
        )

        ax_box.set_xlabel(
            "Tipo de demora",
            fontsize=11
        )

        ax_box.set_ylabel(
            "Cantidad de días",
            fontsize=11
        )

        ax_box.grid(
            which="major",
            linestyle="--",
            linewidth=0.7,
            alpha=0.4
        )

        sns.despine()

        plt.tight_layout()

        st.pyplot(fig_box)

    else:
        st.warning(
            "No existen registros para los filtros seleccionados."
        )

    st.caption(
        """
        Los diagramas de caja permiten visualizar la variabilidad de cada tipo de demora.
        La línea central representa la mediana, mientras que la caja contiene el 50% de
        los expedientes. Los puntos ubicados fuera de los límites habituales corresponden
        a casos con tiempos de demora considerablemente superiores al resto.
        """
    )

    st.markdown("---")

    # ------------------------------------------------------
    # USOS DEL AGUA
    # ------------------------------------------------------

    st.subheader("💧 Cantidad de perforaciones según uso")

    st.markdown(
        """
        Durante el análisis exploratorio se identificó que las variables vinculadas al
        uso declarado del agua presentan una fuerte relación con los tiempos de demora
        del trámite. Por este motivo, resulta relevante analizar cómo se distribuyen
        las perforaciones entre los distintos tipos de uso registrados.
        """
    )

    usos = (
        df_filtrado["Uso"]
        .value_counts()
        .reset_index()
    )

    usos.columns = ["Uso", "Cantidad"]
    st.dataframe(
        usos,
        column_config={
            "Uso": st.column_config.TextColumn(
                "Tipo de uso"
            ),
            "Cantidad": st.column_config.NumberColumn(
                "Cantidad",
                format="%d"
            )
        },
        use_container_width=True,
        hide_index=True
    )
    st.caption(
        """
        La tabla muestra la cantidad de expedientes asociados a cada categoría de uso.
        Esta distribución permite identificar cuáles son los usos más frecuentes dentro
        de los registros analizados y aporta contexto para interpretar las diferencias
        observadas en las demoras de tramitación.
        """
    )

    st.markdown("---")


    # ------------------------------------------------------
    # GRÁFICO DE BARRAS SEGÚN USO
    # ------------------------------------------------------

    st.header("🚰 Distribución de las perforaciones según su uso")

    st.markdown(
        """
        El siguiente gráfico presenta una vista cuantitativa de las perforaciones 
        registradas, clasificadas según el tipo de uso principal asignado.
        """
    )

    if not usos.empty:

        fig_uso, ax_uso = plt.subplots(figsize=(11, 5))

        colores_uso = {
            "Riego": "#4C72B0",
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
            "Cantidad de perforaciones según uso - vista gráfica",
            fontsize=15,
            fontweight="semibold"
        )

        ax_uso.set_xlabel(
            "Uso",
            fontsize=11
        )

        ax_uso.set_ylabel(
            "Cantidad",
            fontsize=11
        )

        plt.xticks(rotation=45, fontsize=9)

        ax_uso.grid(
            which="major",
            linestyle="--",
            linewidth=0.7,
            alpha=0.4
        )

        sns.despine()

        plt.tight_layout()

        st.pyplot(fig_uso)

    else:
        st.warning(
            "No existen registros para los filtros seleccionados."
        )

    st.caption(
        """
        El gráfico de barras permite identificar rápidamente la prevalencia de cada tipo 
        de uso en el volumen total de perforaciones. Esto facilita el análisis visual de 
        la demanda de recursos hídricos subterráneos.
        """
    )

    st.markdown("---")

# ==========================================================
# DEMORA TÉCNICA SEGÚN USO DEL AGUA
# ==========================================================

st.header("💧 Demora técnica según el uso del agua")

st.markdown(
    """
    El siguiente gráfico permite comparar la distribución de las demoras 
    técnicas observadas en los expedientes según el uso del agua asignado.
    """
)

if not df_filtrado.empty:

    fig_uso_demora, ax_uso_demora = plt.subplots(figsize=(11, 5))

    colores_uso = {
        "Riego": "#4C72B0",
        "Otros usos agropecuarios": "green",
        "Industrial": "gray",
        "Otros usos": "gold",
        "Consumo humano": "skyblue",
        "Usos no consuntivos": "purple"
    }

    sns.boxplot(
        data=df_filtrado,
        x="Uso",
        y="Demora_Tecnica",
        hue="Uso",
        palette=colores_uso,
        legend=False,
        width=0.55,
        ax=ax_uso_demora
    )

    ax_uso_demora.set_title(
        "Demora técnica según el uso del agua",
        fontsize=15,
        fontweight="semibold"
    )

    ax_uso_demora.set_xlabel(
        "Uso",
        fontsize=11
    )

    ax_uso_demora.set_ylabel(
        "Cantidad de días",
        fontsize=11
    )

    plt.xticks(rotation=45, fontsize=9)

    ax_uso_demora.grid(
        which="major",
        linestyle="--",
        linewidth=0.7,
        alpha=0.4
    )

    sns.despine()

    plt.tight_layout()

    st.pyplot(fig_uso_demora)

else:
    st.warning(
        "No existen registros para los filtros seleccionados."
    )

st.caption(
    """
    Cada caja representa el 50% central de los datos, donde la línea interna marca la mediana 
    de días de trámite. Los numerosos puntos superiores representan casos atípicos o 'outliers' 
    que superaron el comportamiento habitual, evidenciando expedientes con demoras críticas 
    (algunas cercanas a los 900 días) independientemente del tipo de uso del agua.
    """
)

st.markdown("---")

# ==========================================================
# MAPA
# ==========================================================

st.header("🗺️ Distribución geográfica de las obras de aprovechamiento de agua subterránea con derecho de uso otorgado por Dinagua")

# Diccionario de colores idéntico al de los gráficos anteriores
colores_uso = {
    "Riego": "#4C72B0",
    "Otros usos agropecuarios": "#008000",  # Hex para "green"
    "Industrial": "#808080",               # Hex para "gray"
    "Otros usos": "#FFD700",               # Hex para "gold"
    "Consumo humano": "#87CEEB",           # Hex para "skyblue"
    "Usos no consuntivos": "#800080"       # Hex para "purple"
}

# Filtramos coordenadas válidas e incluimos la columna 'Uso' para el mapeo
mapa = df_filtrado[
    (df_filtrado["Latitud"].between(-35.5, -30.0)) &
    (df_filtrado["Longitud"].between(-59.0, -53.0))
][["Latitud", "Longitud", "Uso"]].dropna()

mapa = mapa.rename(
    columns={
        "Latitud": "lat",
        "Longitud": "lon"
    }
)

if not mapa.empty:
    # Creamos la columna de color mapeando el Uso con nuestro diccionario (usamos negro como respaldo si falta alguno)
    mapa["color"] = mapa["Uso"].map(colores_uso).fillna("#000000")

    # Graficamos el mapa aplicando la columna de color creada
    st.map(
        data=mapa,
        latitude="lat",
        longitude="lon",
        color="color",
        size=20
    )
else:
    st.warning(
        "No existen registros con coordenadas válidas para los filtros seleccionados."
    )

st.caption(
    """
    El mapa muestra la localización georreferenciada de cada perforación dentro del 
    territorio nacional. Cada punto está codificado con el color correspondiente a su 
    tipo de aprovechamiento principal (manteniendo la misma paleta de los gráficos anteriores), 
    lo que permite identificar visualmente zonas de alta concentración de demanda y la 
    distribución espacial de los diferentes usos del agua subterránea.
    """
)

st.markdown("---")


st.caption(
    """
    Trabajo final de Python utilizando la base de datos del Sistema de Información Hídrica de Dinagua.

    Datos válidos al 7 de abril de 2026.
    
    """
)