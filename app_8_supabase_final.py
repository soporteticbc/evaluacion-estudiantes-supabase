
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from supabase import create_client

# Conexión a Supabase
SUPABASE_URL = "https://hdgzzerdfphnalntfmnh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkZ3p6ZXJkZnBobmFsbnRmbW5oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2ODQ3NDYsImV4cCI6MjA2ODI2MDc0Nn0.PrZGzatAjsVcMepmKdhlT303Cf1FbFAcGnhzlrUhPeU"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Archivos de datos locales
archivo_estudiantes = "estudiantes 1 1 1.csv"
archivo_preguntas = "preguntas 1 1 1.csv"
archivo_maestros = "maestros.csv"

st.title("Evaluación de Estudiantes")

menu = ["Evaluar estudiantes", "Ver reportes", "Reportes generales por estudiante"]
opcion = st.sidebar.selectbox("Menú", menu)

# Cargar datos
if os.path.exists(archivo_maestros):
    maestros_df = pd.read_csv(archivo_maestros, encoding="latin1")
    lista_maestros = sorted(maestros_df["maestro"].dropna().unique())
    maestro = st.sidebar.selectbox("Selecciona tu nombre", lista_maestros)
else:
    st.error("No se encontró el archivo de maestros.")
    st.stop()

if opcion == "Evaluar estudiantes":
    if os.path.exists(archivo_estudiantes) and os.path.exists(archivo_preguntas):
        estudiantes = pd.read_csv(archivo_estudiantes, encoding="latin1")
        preguntas = pd.read_csv(archivo_preguntas, encoding="latin1")

        cursos_maestro = maestros_df[maestros_df["maestro"] == maestro]["curso"].unique()
        curso = st.selectbox("Selecciona un curso", cursos_maestro)

        if curso:
            materias_maestro = maestros_df[(maestros_df["maestro"] == maestro) & (maestros_df["curso"] == curso)]["materia"].unique()
            materia = st.selectbox("Selecciona una materia", materias_maestro)

            estudiantes_curso = estudiantes[estudiantes["curso"] == curso]
            estudiante = st.selectbox("Selecciona un estudiante", estudiantes_curso["nombre"].unique())

            preguntas_materia = preguntas[preguntas["materia"] == materia]

            respuestas = []
            for _, row in preguntas_materia.iterrows():
                pregunta = row["texto"]
                respuesta = st.radio(pregunta, [
                    "Incumplimiento",
                    "Incumplimiento parcial",
                    "Cumplimiento",
                    "Excede cumplimiento"
                ], key=pregunta)
                respuestas.append({
                    "maestro": maestro,
                    "curso": curso,
                    "estudiante": estudiante,
                    "materia": materia,
                    "pregunta": pregunta,
                    "respuesta": respuesta
                })

            if st.button("Guardar respuestas"):
                query = supabase.table("respuestas").select("*").match({
                    "maestro": maestro,
                    "curso": curso,
                    "estudiante": estudiante,
                    "materia": materia
                }).execute()

                if query.data:
                    st.error("Ya has evaluado a este estudiante para esta materia.")
                else:
                    for r in respuestas:
                        supabase.table("respuestas").insert(r).execute()
                    st.success("Respuestas guardadas exitosamente.")
    else:
        st.error("Faltan archivos de estudiantes o preguntas.")

elif opcion == "Ver reportes":
    query = supabase.table("respuestas").select("*").eq("maestro", maestro).execute()
    data = query.data
    if data:
        df = pd.DataFrame(data)
        estudiante = st.selectbox("Selecciona un estudiante", df["estudiante"].unique())
        materia = st.selectbox("Selecciona una materia", df["materia"].unique())

        if estudiante and materia:
            df_filtrado = df[(df["estudiante"] == estudiante) & (df["materia"] == materia)]
            conteo_respuestas = df_filtrado["respuesta"].value_counts()

            fig, ax = plt.subplots()
            ax.pie(conteo_respuestas, labels=conteo_respuestas.index, autopct='%1.1f%%')
            ax.axis('equal')
            st.pyplot(fig)
    else:
        st.warning("No hay respuestas guardadas para este maestro.")

elif opcion == "Reportes generales por estudiante":
    query = supabase.table("respuestas").select("*").execute()
    data = query.data
    if data:
        df_total = pd.DataFrame(data)
        estudiante = st.selectbox("Selecciona un estudiante", df_total["estudiante"].unique())

        if estudiante:
            df_est = df_total[df_total["estudiante"] == estudiante]
            resumen = df_est.groupby(["materia", "respuesta"]).size().unstack(fill_value=0)
            st.dataframe(resumen)

            resumen.plot(kind="bar", stacked=True, figsize=(10, 5))
            st.pyplot(plt.gcf())
    else:
        st.warning("No hay respuestas disponibles.")

# Pie de página
st.markdown("""
<style>
.footer {
position: fixed;
bottom: 0;
width: 100%;
text-align: center;
color: gray;
}
</style>
<div class="footer">
<p>Steven Nehemias Polanco Rojas, IT SUPPORT</p>
</div>
""", unsafe_allow_html=True)
