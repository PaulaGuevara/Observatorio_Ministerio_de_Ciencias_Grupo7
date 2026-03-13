import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Observatorio de Ciencia, Tecnología e Innovación",
    page_icon="🔬",
    layout="wide",
)

st.title("Observatorio de Ciencia, Tecnología e Innovación")
st.markdown(
    "Investigadores Reconocidos por Convocatoria – Minciencias Colombia (2017, 2019, 2021)"
)


@st.cache_data
def cargar_datos():
    return pd.read_csv("datos/tarea_join/investigadores_consolidado.csv")


df = cargar_datos()

st.sidebar.header("Filtros")

años = sorted(df["ANO_CONVO"].dropna().unique())
año_sel = st.sidebar.multiselect("Año de convocatoria", años, default=años)

df_filtrado = df[df["ANO_CONVO"].isin(año_sel)] if año_sel else df

st.subheader("Resumen general")
col1, col2, col3 = st.columns(3)
col1.metric("Total investigadores", f"{len(df_filtrado):,}")
col2.metric(
    "Departamentos",
    df_filtrado["NME_DEPARTAMENTO_RES_PR"].nunique(),
)
col3.metric("Áreas de conocimiento", df_filtrado["NME_GRAN_AREA_PR"].nunique())

st.subheader("Distribución por género")
genero = df_filtrado["NME_GENERO_PR"].value_counts().reset_index()
genero.columns = ["Género", "Cantidad"]
st.bar_chart(genero.set_index("Género"))

st.subheader("Top 10 departamentos de residencia")
top_dep = (
    df_filtrado["NME_DEPARTAMENTO_RES_PR"]
    .value_counts()
    .head(10)
    .reset_index()
)
top_dep.columns = ["Departamento", "Cantidad"]
st.bar_chart(top_dep.set_index("Departamento"))

st.subheader("Distribución por gran área de conocimiento")
gran_area = df_filtrado["NME_GRAN_AREA_PR"].value_counts().reset_index()
gran_area.columns = ["Gran Área", "Cantidad"]
st.bar_chart(gran_area.set_index("Gran Área"))

st.subheader("Datos crudos")
st.dataframe(df_filtrado.head(100), use_container_width=True)
