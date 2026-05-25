import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Deserción Escolar RD",
    page_icon="🏫",
    layout="wide",
)

PROCESSED_DIR = Path("data/processed")
COLOR_RIESGO = {"alto": "#D32F2F", "medio": "#FF9800", "bajo": "#FFC107", "muy_bajo": "#4CAF50"}
ORDEN_RIESGO = ["muy_bajo", "bajo", "medio", "alto"]


@st.cache_data
def cargar_datos():
    df = pd.read_csv(PROCESSED_DIR / "dataset_con_predicciones.csv")
    df_ind = pd.read_csv(PROCESSED_DIR / "indicadores_educativos_ancho.csv")
    return df, df_ind


df, df_ind = cargar_datos()

# ── Sidebar: Filtros ────────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Coat_of_arms_of_the_Dominican_Republic.svg/120px-Coat_of_arms_of_the_Dominican_Republic.svg.png",
    width=80,
)
st.sidebar.title("Filtros")

regionales = ["Todas"] + sorted(df["regional"].unique().tolist())
sel_regional = st.sidebar.selectbox("Regional", regionales)

if sel_regional != "Todas":
    distritos_disp = sorted(df[df["regional"] == sel_regional]["distrito"].unique().tolist())
else:
    distritos_disp = sorted(df["distrito"].unique().tolist())
sel_distrito = st.sidebar.selectbox("Distrito", ["Todos"] + distritos_disp)

sel_sector = st.sidebar.multiselect("Sector", df["sector"].unique().tolist(), default=df["sector"].unique().tolist())

sel_riesgo = st.sidebar.multiselect("Nivel de Riesgo", ORDEN_RIESGO, default=ORDEN_RIESGO)

# Aplicar filtros
mask = df["sector"].isin(sel_sector) & df["riesgo"].isin(sel_riesgo)
if sel_regional != "Todas":
    mask &= df["regional"] == sel_regional
if sel_distrito != "Todos":
    mask &= df["distrito"] == sel_distrito
df_filtrado = df[mask]

# ── Header ──────────────────────────────────────────────────────────
st.title("🏫 Predictor de Deserción Escolar en RD")
st.markdown("Análisis de riesgo de deserción en centros educativos dominicanos basado en datos del **MINERD** (2021-2025).")

# ── KPIs ────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Centros", f"{len(df_filtrado):,}")
col2.metric("Matrícula Total", f"{df_filtrado['matricula'].sum():,}")

n_alto = (df_filtrado["riesgo"] == "alto").sum()
col3.metric("Riesgo Alto", f"{n_alto:,}", delta=f"{n_alto/len(df_filtrado)*100:.1f}%" if len(df_filtrado) > 0 else "0%")

abandono_med = df_filtrado["abandono_max"].median()
col4.metric("Abandono Mediana", f"{abandono_med:.1f}%")

tend_med = df_filtrado["tendencia_abandono_sec"].median()
col5.metric("Tendencia Mediana", f"{tend_med:+.1f}pp", delta_color="inverse")

st.divider()

# ── Tabs ────────────────────────────────────────────────────────────
tab_mapa, tab_regional, tab_detalle, tab_tendencia = st.tabs(
    ["🗺️ Mapa", "📊 Por Regional", "🔍 Detalle Centros", "📈 Tendencias"]
)

# ── TAB 1: Mapa ────────────────────────────────────────────────────
with tab_mapa:
    st.subheader("Mapa de Centros Educativos por Nivel de Riesgo")

    df_mapa = df_filtrado.dropna(subset=["coordenadas latitud", "coordenadas longitud"])

    if len(df_mapa) > 0:
        df_mapa["riesgo_cat"] = pd.Categorical(df_mapa["riesgo"], categories=ORDEN_RIESGO, ordered=True)
        fig_map = px.scatter_map(
            df_mapa.sort_values("riesgo_cat", ascending=False),
            lat="coordenadas latitud",
            lon="coordenadas longitud",
            color="riesgo",
            color_discrete_map=COLOR_RIESGO,
            category_orders={"riesgo": ORDEN_RIESGO},
            hover_name="centros",
            hover_data={"regional": True, "distrito": True, "matricula": True, "abandono_max": True, "coordenadas latitud": False, "coordenadas longitud": False},
            size="matricula",
            size_max=12,
            zoom=7.5,
            center={"lat": 18.9, "lon": -70.0},
            map_style="carto-positron",
            height=550,
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend_title_text="Riesgo")
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption(f"Mostrando {len(df_mapa):,} centros con coordenadas de {len(df_filtrado):,} total.")
    else:
        st.info("No hay centros con coordenadas para los filtros seleccionados.")

# ── TAB 2: Por Regional ────────────────────────────────────────────
with tab_regional:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Distribución de Riesgo por Regional")
        riesgo_regional = (
            df_filtrado.groupby(["regional", "riesgo"])
            .size()
            .reset_index(name="count")
        )
        riesgo_regional["riesgo"] = pd.Categorical(riesgo_regional["riesgo"], categories=ORDEN_RIESGO, ordered=True)
        fig_bar = px.bar(
            riesgo_regional.sort_values(["regional", "riesgo"]),
            x="count",
            y="regional",
            color="riesgo",
            color_discrete_map=COLOR_RIESGO,
            orientation="h",
            height=550,
            category_orders={"riesgo": ORDEN_RIESGO},
        )
        fig_bar.update_layout(yaxis=dict(categoryorder="category ascending"), legend_title_text="Riesgo")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
        st.subheader("Tasa de Abandono Secundario por Regional")
        año_col = [c for c in df_ind.columns if "lectivo" in c][0]
        ind_reg = df_ind[
            (df_ind["tipo"] == "regional") & (df_ind[año_col] == "2024-2025")
        ].sort_values("abandono_secundario", ascending=True)

        fig_aband = px.bar(
            ind_reg,
            x="abandono_secundario",
            y="regional_distrito",
            orientation="h",
            height=550,
            color="abandono_secundario",
            color_continuous_scale=["#4CAF50", "#FFC107", "#D32F2F"],
        )
        fig_aband.update_layout(yaxis_title="", xaxis_title="% Abandono Secundario 2024-2025", coloraxis_showscale=False)
        st.plotly_chart(fig_aband, use_container_width=True)

    # Pie chart
    st.subheader("Proporción de Riesgo")
    riesgo_counts = df_filtrado["riesgo"].value_counts().reindex(ORDEN_RIESGO).fillna(0)
    fig_pie = px.pie(
        values=riesgo_counts.values,
        names=riesgo_counts.index,
        color=riesgo_counts.index,
        color_discrete_map=COLOR_RIESGO,
        hole=0.4,
    )
    fig_pie.update_layout(height=350)
    st.plotly_chart(fig_pie, use_container_width=True)

# ── TAB 3: Detalle Centros ─────────────────────────────────────────
with tab_detalle:
    st.subheader("Centros Educativos Filtrados")

    col_sort = st.selectbox("Ordenar por", ["abandono_max", "matricula", "centros", "riesgo"], index=0)
    ascending = st.checkbox("Ascendente", value=False)

    cols_mostrar = ["centros", "regional", "distrito", "sector", "nivel", "matricula", "abandono_max", "riesgo", "riesgo_predicho", "provincia", "municipio"]
    df_show = df_filtrado[cols_mostrar].sort_values(col_sort, ascending=ascending)

    st.dataframe(
        df_show.style.map(
            lambda v: f"background-color: {COLOR_RIESGO.get(v, '')}" if v in COLOR_RIESGO else "",
            subset=["riesgo"],
        ),
        use_container_width=True,
        height=500,
    )
    st.caption(f"Mostrando {len(df_show):,} centros.")

# ── TAB 4: Tendencias ──────────────────────────────────────────────
with tab_tendencia:
    st.subheader("Evolución del Abandono Secundario por Regional (2021-2025)")

    año_col = [c for c in df_ind.columns if "lectivo" in c][0]
    ind_reg_hist = df_ind[df_ind["tipo"] == "regional"]

    fig_trend = px.line(
        ind_reg_hist,
        x=año_col,
        y="abandono_secundario",
        color="regional_distrito",
        markers=True,
        height=500,
    )
    fig_trend.update_layout(
        xaxis_title="Año Lectivo",
        yaxis_title="% Abandono Secundario",
        legend_title_text="Regional",
        legend=dict(font=dict(size=10)),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.subheader("Distritos con Mayor Deterioro (tendencia positiva)")
    top_deterioro = (
        df_filtrado.drop_duplicates(subset=["distrito"])
        .nlargest(15, "tendencia_abandono_sec")[["distrito", "regional", "abandono_sec_historico", "tendencia_abandono_sec", "abandono_secundario"]]
    )
    st.dataframe(top_deterioro, use_container_width=True, hide_index=True)

# ── Footer ──────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center; color:gray; font-size:0.85em;'>"
    "Datos: MINERD · Anuarios de Indicadores Educativos 2021-2025 · "
    "Desarrollado por <b>Eddy Luis Pullés Martín</b>"
    "</div>",
    unsafe_allow_html=True,
)
