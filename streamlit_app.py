import streamlit as st
import pandas as pd

st.title("Observatorio de Ciencia, Tecnología e Innovación")

st.write("Visualización de investigadores MinCiencias")

# cargar datos
df = pd.read_excel("datos/tarea_join/investigadores_consolidado.xlsx")

st.subheader("Vista de los datos")
st.dataframe(df)

st.subheader("Investigadores por género")

genero = df["NME_GENERO_PR"].value_counts()

st.bar_chart(genero)

st.subheader("Investigadores por área")

area = df["NME_GRAN_AREA_PR"].value_counts().head(10)

st.bar_chart(area)