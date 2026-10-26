"""Dashboard Konzerta: consume exclusivamente tablas agregadas de la capa oro."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Mercado laboral | Konzerta", page_icon="📊", layout="wide")
ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "datos" / "oro"
FILES = {
    "areas": "oro_areas_subareas.csv",
    "modalidades": "oro_modalidades_area.csv",
    "geografia": "oro_geografia.csv",
    "salarios_experiencia": "oro_salarios_experiencia.csv",
    "salarios_nivel": "oro_salarios_nivel.csv",
    "semanal": "oro_tendencia_semanal.csv",
}

@st.cache_data
def cargar_oro():
    return {nombre: pd.read_csv(GOLD / archivo) for nombre, archivo in FILES.items()}

faltantes = [nombre for nombre in FILES.values() if not (GOLD / nombre).is_file()]
if faltantes:
    st.error("Faltan archivos de la capa oro. Ejecuta el notebook hasta la sección 'Capa oro'.")
    st.code("\n".join(faltantes))
    st.stop()

data = cargar_oro()
areas = data["areas"]
modalidades = data["modalidades"]
geografia = data["geografia"]
sal_exp = data["salarios_experiencia"]
sal_nivel = data["salarios_nivel"]
semanal = data["semanal"]
semanal["semana_inicio"] = pd.to_datetime(semanal["semana_inicio"], errors="coerce")

st.title("Análisis de ofertas de empleo de Konzerta")
st.caption("Panamá · archivo de octubre de 2026 · fuente: Konzerta · datos agregados (capa oro)")
st.info("Los resultados describen los anuncios presentes en el archivo y no representan la totalidad del mercado laboral panameño.")

# Los filtros se aplican únicamente sobre agregados de la capa oro.
opciones_area = sorted(areas["area"].dropna().astype(str).unique().tolist())
seleccion_areas = st.sidebar.multiselect("Áreas profesionales", opciones_area, default=opciones_area)
opciones_prov = sorted(geografia["provincia"].dropna().astype(str).unique().tolist())
seleccion_prov = st.sidebar.multiselect("Provincias", opciones_prov, default=opciones_prov)
areas_filtradas = areas[areas["area"].isin(seleccion_areas)]
modalidades_filtradas = modalidades[modalidades["area"].isin(seleccion_areas)]
geo_filtrada = geografia[
    geografia["area"].isin(seleccion_areas) & geografia["provincia"].isin(seleccion_prov)
]

k1,k2,k3 = st.columns(3)
k1.metric("Anuncios (áreas seleccionadas)", f"{int(areas_filtradas['ofertas'].sum()):,}")
k2.metric("Vacantes registradas", f"{int(areas_filtradas['vacantes'].sum()):,}")
k3.metric("Provincias seleccionadas", len(seleccion_prov))

st.subheader("1. Contexto: áreas con mayor número de anuncios")
area_totales = (areas_filtradas.groupby("area",as_index=False)[["ofertas","vacantes"]]
                .sum().sort_values("ofertas",ascending=False).head(10))
if not area_totales.empty:
    fig = px.bar(area_totales.sort_values("ofertas"),x="ofertas",y="area",orientation="h",
                 title="Diez áreas con más anuncios",labels={"ofertas":"Anuncios","area":"Área"})
    st.plotly_chart(fig,use_container_width=True)
else:
    st.warning("No hay áreas con el filtro seleccionado.")

st.subheader("2. Hallazgo: subáreas con más oportunidades")
sub = areas_filtradas.sort_values("ofertas",ascending=False).head(12)
if not sub.empty:
    fig = px.bar(sub.sort_values("ofertas"),x="ofertas",y="subarea",color="area",
                 orientation="h",title="Doce combinaciones área-subárea principales")
    st.plotly_chart(fig,use_container_width=True)

st.subheader("3. Hallazgo: modalidades por área")
mod = modalidades_filtradas.copy()
if not mod.empty:
    mod["porcentaje"] = mod["ofertas"] / mod.groupby("area")["ofertas"].transform("sum") * 100
    top = area_totales["area"].tolist()
    mod = mod[mod["area"].isin(top)]
    fig = px.bar(mod,x="porcentaje",y="area",color="modalidad",orientation="h",
                 barmode="stack",title="Distribución porcentual de modalidades por área")
    fig.update_layout(xaxis_range=[0,100])
    st.plotly_chart(fig,use_container_width=True)

st.subheader("4. Hallazgo: distribución geográfica y nivel laboral")
geo_prov = geo_filtrada.groupby("provincia",as_index=False)["ofertas"].sum().sort_values("ofertas")
if not geo_prov.empty:
    fig = px.bar(geo_prov,x="ofertas",y="provincia",orientation="h",
                 title="Anuncios por provincia y áreas seleccionadas")
    st.plotly_chart(fig,use_container_width=True)
geo_nivel = geo_filtrada.groupby(["provincia","nivel_laboral"],as_index=False)["ofertas"].sum()
if not geo_nivel.empty:
    geo_nivel["porcentaje"] = geo_nivel["ofertas"] / geo_nivel.groupby("provincia")["ofertas"].transform("sum") * 100
    fig = px.bar(geo_nivel,x="porcentaje",y="provincia",color="nivel_laboral",
                 orientation="h",barmode="stack",title="Participación por nivel laboral y provincia")
    fig.update_layout(xaxis_range=[0,100])
    st.plotly_chart(fig,use_container_width=True)

st.subheader("5. Hallazgo: salarios según experiencia")
if not sal_exp.empty:
    fig = px.bar(sal_exp,x="rango_experiencia",y="salario_max_mediana",
                 title="Mediana del salario máximo por experiencia informada",
                 labels={"rango_experiencia":"Experiencia","salario_max_mediana":"Mediana salarial"})
    st.plotly_chart(fig,use_container_width=True)
    st.caption("Muestra limitada: solo ofertas con salario sin alerta y experiencia registrada. No extrapolar al mercado.")
else:
    st.warning("No hay registros suficientes con salario y experiencia.")
if not sal_nivel.empty:
    st.dataframe(sal_nivel,use_container_width=True,hide_index=True)

st.subheader("6. Tendencia: publicaciones semanales observadas")
if not semanal.empty:
    fig = px.line(semanal,x="semana_inicio",y="ofertas",markers=True,
                  title="Anuncios por semana (hasta la fecha de extracción)")
    st.plotly_chart(fig,use_container_width=True)
    st.caption("Las semanas inicial y final pueden ser parciales; no se proyecta la demanda después de la extracción.")

st.subheader("Conclusión y límites")
st.write("Las áreas, ubicaciones y modalidades se comparan mediante recuentos de anuncios agregados. "
         "Las diferencias salariales son exploratorias debido a la escasa coincidencia de salario y experiencia; "
         "la serie semanal refleja la ventana de observación del archivo, no una predicción.")
st.caption("Dashboard construido únicamente con los seis CSV de datos/oro; no lee el Excel original ni los CSV de plata.")
