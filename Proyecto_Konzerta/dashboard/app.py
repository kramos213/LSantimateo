"""Konzerta | Dashboard académico multiplataforma, alimentado solo por capa oro."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Konzerta · Empleo en Panamá", page_icon="📊", layout="wide")
ROOT = Path(__file__).resolve().parents[1]
GOLD = ROOT / "datos" / "oro"
ARCHIVOS = {
    "areas": "oro_areas_subareas.csv",
    "modalidades": "oro_modalidades_area.csv",
    "geografia": "oro_geografia.csv",
    "experiencia": "oro_salarios_experiencia.csv",
    "niveles": "oro_salarios_nivel.csv",
    "semanas": "oro_tendencia_semanal.csv",
}
AZUL = "#2563eb"
COLORES = ["#2563eb", "#0d9488", "#7c3aed", "#ea580c", "#db2777", "#0891b2", "#65a30d"]
st.markdown("""
<style>
.stApp {background:#f6f8fc;color:#152238}
[data-testid="stSidebar"] {background:#edf3fb}
.block-container {padding-top:2rem;max-width:1350px}
h1,h2,h3 {color:#152238;letter-spacing:-.02em}
div[data-testid="stMetric"] {background:white;border:1px solid #e1e8f2;border-radius:12px;padding:16px}
[data-testid="stMetricValue"] {color:#12345c}
div[data-testid="stPlotlyChart"] {background:white;border:1px solid #e1e8f2;border-radius:12px}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def cargar_csv(ruta, modificado):
    return pd.read_csv(ruta, encoding="utf-8-sig")

def figura(fig, alto=420):
    fig.update_layout(
        template="plotly_white", height=alto, paper_bgcolor="white", plot_bgcolor="white",
        font=dict(color="#253858", size=12), margin=dict(l=25,r=30,t=55,b=40),
        title_font=dict(size=17,color="#172b4d"), legend_title_text="",
        hoverlabel=dict(bgcolor="white",font_color="#172b4d")
    )
    st.plotly_chart(fig, use_container_width=True)

def exportar(df, nombre, key):
    st.download_button(
        "Descargar CSV de esta sección", df.to_csv(index=False).encode("utf-8-sig"),
        file_name=nombre, mime="text/csv", key=key
    )

st.title("Mercado laboral en Panamá")
st.caption("Observatorio de ofertas publicadas en Konzerta · Proyecto académico de ciencia de datos")
st.info("Los resultados corresponden al archivo analizado, no a la totalidad de ofertas laborales de Panamá.")

faltantes = [nombre for nombre in ARCHIVOS.values() if not (GOLD/nombre).is_file()]
if faltantes:
    st.error("Faltan tablas de la capa oro en tu computadora.")
    st.code(str(GOLD))
    st.write("Archivos faltantes:", ", ".join(faltantes))
    st.caption("Ejecuta el notebook para generarlos y copia los seis CSV de Google Drive a la carpeta datos/oro de esta instalación.")
    st.stop()

try:
    datos = {k:cargar_csv(str(GOLD/v),(GOLD/v).stat().st_mtime_ns) for k,v in ARCHIVOS.items()}
except Exception as exc:
    st.error(f"No se pudieron leer los archivos de la capa oro: {exc}")
    st.stop()

columnas = {
    "areas": {"area","subarea","ofertas","vacantes"},
    "modalidades": {"area","modalidad","ofertas"},
    "geografia": {"provincia","area","nivel_laboral","ofertas"},
    "experiencia": {"rango_experiencia","ofertas","salario_max_mediana"},
    "niveles": {"nivel_laboral","ofertas","salario_max_mediana"},
    "semanas": {"semana_inicio","ofertas"},
}
for nombre, obligatorias in columnas.items():
    faltan = obligatorias-set(datos[nombre].columns)
    if faltan:
        st.error(f"El archivo {ARCHIVOS[nombre]} no contiene: {', '.join(sorted(faltan))}")
        st.stop()
for df in datos.values():
    for col in ("ofertas","vacantes","salario_max_mediana"):
        if col in df:
            df[col] = pd.to_numeric(df[col],errors="coerce").fillna(0)
areas, modalidades, geografia = datos["areas"],datos["modalidades"],datos["geografia"]
experiencia,niveles,semanas = datos["experiencia"],datos["niveles"],datos["semanas"]
semanas = semanas.copy()
semanas["semana_inicio"] = pd.to_datetime(semanas["semana_inicio"],errors="coerce")
semanas = semanas.dropna(subset=["semana_inicio"]).sort_values("semana_inicio")

with st.sidebar:
    st.header("Filtros")
    st.caption("Los filtros se aplican al panorama, modalidades y geografía según las dimensiones disponibles.")
    opciones_area = sorted(areas["area"].dropna().astype(str).unique().tolist())
    seleccion_area = st.multiselect("Áreas profesionales", opciones_area, default=opciones_area, key="areas")
    opciones_prov = sorted(geografia["provincia"].dropna().astype(str).unique().tolist())
    seleccion_prov = st.multiselect("Ubicaciones (solo geografía)", opciones_prov, default=opciones_prov, key="provincias")
    cantidad = st.slider("Mostrar primeras categorías", min_value=5,max_value=20,value=10,key="top")
    st.divider()
    st.caption("Salarios y evolución temporal son datos generales: sus CSV no contienen provincia ni área.")
    st.caption("Fuente de datos: seis CSV de datos/oro.")

af = areas[areas["area"].isin(seleccion_area)].copy()
mf = modalidades[modalidades["area"].isin(seleccion_area)].copy()
gf = geografia[geografia["area"].isin(seleccion_area)&geografia["provincia"].isin(seleccion_prov)].copy()
total = int(areas["ofertas"].sum())
c1,c2,c3,c4 = st.columns(4)
c1.metric("Ofertas · áreas elegidas",f"{int(af['ofertas'].sum()):,}")
c2.metric("Vacantes declaradas · áreas",f"{int(af['vacantes'].sum()):,}")
c3.metric("Ofertas · ubicación y área",f"{int(gf['ofertas'].sum()):,}")
c4.metric("Total de anuncios del archivo",f"{total:,}")

tab1,tab2,tab3,tab4,tab5 = st.tabs(["Panorama","Modalidades","Geografía","Salarios","Tendencia"])

with tab1:
    st.subheader("1. Áreas y subáreas con más ofertas")
    if af.empty:
        st.warning("No hay áreas seleccionadas.")
    else:
        top=af.groupby("area",as_index=False)[["ofertas","vacantes"]].sum().nlargest(cantidad,"ofertas")
        a,b=st.columns(2)
        with a:
            fig=px.bar(top.sort_values("ofertas"),x="ofertas",y="area",orientation="h",
                       text="ofertas",title="Ofertas por área",color_discrete_sequence=[AZUL])
            figura(fig,460)
        with b:
            sub=af.nlargest(cantidad,"ofertas").sort_values("ofertas")
            fig=px.bar(sub,x="ofertas",y="subarea",orientation="h",color="area",
                       title="Subáreas con más ofertas",color_discrete_sequence=COLORES)
            figura(fig,460)
        with st.expander("Consultar tabla y descargar"):
            st.dataframe(af.sort_values("ofertas",ascending=False),hide_index=True,use_container_width=True)
            exportar(af,"areas_filtradas.csv","exp_areas")

with tab2:
    st.subheader("2. Modalidades de trabajo")
    if mf.empty:
        st.warning("Selecciona un área para ver modalidades.")
    else:
        general=mf.groupby("modalidad",as_index=False)["ofertas"].sum()
        a,b=st.columns(2)
        with a:
            fig=px.pie(general,names="modalidad",values="ofertas",hole=.5,
                       title="Distribución general de modalidades",color_discrete_sequence=COLORES)
            figura(fig,440)
        with b:
            mejores=mf.groupby("area")["ofertas"].sum().nlargest(cantidad).index
            m=mf[mf["area"].isin(mejores)].copy()
            m["porcentaje"]=m["ofertas"]/m.groupby("area")["ofertas"].transform("sum")*100
            fig=px.bar(m,x="porcentaje",y="area",color="modalidad",orientation="h",
                       barmode="stack",title="Modalidades por área (%)",
                       color_discrete_sequence=COLORES)
            fig.update_layout(xaxis_range=[0,100])
            figura(fig,440)
        with st.expander("Consultar tabla y descargar"):
            st.dataframe(mf,hide_index=True,use_container_width=True)
            exportar(mf,"modalidades_filtradas.csv","exp_mod")

with tab3:
    st.subheader("3. Ubicación y nivel laboral")
    st.caption("«Otra» y «Sin dato» son categorías de la fuente; no deben interpretarse como provincias oficiales.")
    if gf.empty:
        st.warning("No hay registros para la combinación de área y ubicación.")
    else:
        a,b=st.columns(2)
        with a:
            prov=gf.groupby("provincia",as_index=False)["ofertas"].sum().sort_values("ofertas")
            fig=px.bar(prov,x="ofertas",y="provincia",orientation="h",
                       title="Ofertas por ubicación",color_discrete_sequence=[AZUL])
            figura(fig,450)
        with b:
            nivel=gf.groupby("nivel_laboral",as_index=False)["ofertas"].sum()
            fig=px.pie(nivel,names="nivel_laboral",values="ofertas",hole=.5,
                       title="Distribución por nivel laboral",color_discrete_sequence=COLORES)
            figura(fig,450)
        with st.expander("Consultar tabla y descargar"):
            st.dataframe(gf,hide_index=True,use_container_width=True)
            exportar(gf,"geografia_filtrada.csv","exp_geo")

with tab4:
    st.subheader("4. Salarios y experiencia")
    st.warning("Datos generales sin filtros de área o provincia. La moneda y periodicidad no están verificadas; la muestra con salario y experiencia es reducida.")
    a,b=st.columns(2)
    with a:
        if experiencia.empty:
            st.info("No hay datos salariales por experiencia.")
        else:
            fig=px.bar(experiencia,x="rango_experiencia",y="salario_max_mediana",
                       text="ofertas",title="Mediana de salario máximo por experiencia",
                       color_discrete_sequence=[AZUL])
            figura(fig,440)
            st.caption(f"Muestra: {int(experiencia['ofertas'].sum())} anuncios. Los números sobre las barras son recuentos.")
    with b:
        if niveles.empty:
            st.info("No hay datos salariales por nivel laboral.")
        else:
            fig=px.bar(niveles.sort_values("salario_max_mediana"),x="salario_max_mediana",
                       y="nivel_laboral",orientation="h",title="Mediana salarial por nivel",
                       color_discrete_sequence=["#0d9488"])
            figura(fig,440)
    with st.expander("Consultar tablas y descargar"):
        st.dataframe(experiencia,hide_index=True,use_container_width=True)
        exportar(experiencia,"salarios_experiencia.csv","exp_salexp")
        st.dataframe(niveles,hide_index=True,use_container_width=True)
        exportar(niveles,"salarios_nivel.csv","exp_salniv")

with tab5:
    st.subheader("5. Publicaciones por semana")
    st.caption("Tendencia general sin filtros de área o provincia. La primera y última semana pueden ser parciales.")
    if semanas.empty:
        st.warning("No hay fechas semanales válidas.")
    else:
        fig=px.line(semanas,x="semana_inicio",y="ofertas",markers=True,
                    title="Ofertas observadas por semana",color_discrete_sequence=[AZUL])
        figura(fig,460)
        with st.expander("Consultar serie y descargar"):
            st.dataframe(semanas,hide_index=True,use_container_width=True)
            exportar(semanas,"tendencia_semanal.csv","exp_semanas")

st.divider()
st.caption("Proyecto académico · Fuente: Konzerta · El dashboard lee únicamente la capa oro. No se realizan predicciones ni se generalizan los salarios a todo el mercado laboral.")
