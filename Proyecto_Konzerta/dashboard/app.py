"""Dashboard interactivo de Konzerta. Fuente exclusiva: seis CSV de capa oro."""
from pathlib import Path
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Konzerta | Observatorio laboral", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
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
PALETTE = ["#38BDF8", "#A78BFA", "#34D399", "#FBBF24", "#FB7185", "#2DD4BF", "#818CF8", "#FDA4AF"]
st.markdown("""
<style>
.stApp {background:linear-gradient(140deg,#0b1222 0%,#111b31 55%,#0b1222 100%);color:#eaf2ff}
[data-testid="stSidebar"] {background:#111b2d}
h1,h2,h3 {letter-spacing:-.025em}
div[data-testid="stMetric"] {background:#17243a;border:1px solid #31425c;border-radius:16px;padding:16px}
div[data-testid="stMetricLabel"] {color:#a9bfd8}
div[data-testid="stMetricValue"] {color:#f3f8ff}
[data-testid="stPlotlyChart"] {border:1px solid #293d56;border-radius:14px;overflow:hidden}
.hero {padding:24px 28px;border-radius:20px;background:linear-gradient(110deg,#142a4b,#22365d 65%,#182b43);border:1px solid #345075;margin-bottom:16px}
.eyebrow {color:#67e8f9;font-size:12px;letter-spacing:.14em;font-weight:700}
.hero h1 {font-size:2.2rem;margin:7px 0;color:white}
.hero p {color:#c8d9ef;margin:0}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Cargando capa oro…")
def cargar_oro(archivos):
    return {clave: pd.read_csv(GOLD / nombre, encoding="utf-8-sig") for clave, nombre in archivos}

def grafico(fig, altura=420):
    fig.update_layout(
        height=altura, template="plotly_dark", paper_bgcolor="#111b2d",
        plot_bgcolor="#111b2d", font=dict(color="#dbeafe"),
        margin=dict(l=22,r=22,t=65,b=30), title_font_size=17,
        legend=dict(orientation="h",y=-0.25), hovermode="closest"
    )
    st.plotly_chart(fig, use_container_width=True)

def tabla_descargable(df, nombre):
    st.download_button(
        "⬇️ Descargar tabla CSV", df.to_csv(index=False).encode("utf-8-sig"),
        file_name=nombre, mime="text/csv", key="descargar_"+nombre
    )

faltantes = [nombre for nombre in FILES.values() if not (GOLD / nombre).is_file()]
if faltantes:
    st.error("No se encontraron todos los archivos de la capa oro en: "+str(GOLD))
    st.code("\n".join(faltantes))
    st.info("Ejecuta el notebook hasta la exportación de capa oro y sincroniza los CSV de Google Drive a datos/oro en tu Mac.")
    st.stop()

try:
    data = cargar_oro(tuple(FILES.items()))
except Exception as exc:
    st.error(f"No se pudieron leer los CSV: {exc}")
    st.stop()

required = {
    "areas": {"area","subarea","ofertas","vacantes"},
    "modalidades": {"area","modalidad","ofertas"},
    "geografia": {"provincia","area","nivel_laboral","ofertas","vacantes"},
    "salarios_experiencia": {"rango_experiencia","ofertas","salario_max_mediana"},
    "salarios_nivel": {"nivel_laboral","ofertas","salario_max_mediana"},
    "semanal": {"semana_inicio","ofertas"},
}
errores = [f"{k}: {', '.join(sorted(v-set(data[k].columns)))}" for k,v in required.items() if v-set(data[k].columns)]
if errores:
    st.error("Hay columnas faltantes en la capa oro:")
    st.code("\n".join(errores))
    st.stop()

areas, mod, geo = data["areas"], data["modalidades"], data["geografia"]
sal_exp, sal_nivel, semanal = data["salarios_experiencia"], data["salarios_nivel"], data["semanal"]
semanal = semanal.copy()
semanal["semana_inicio"] = pd.to_datetime(semanal["semana_inicio"],errors="coerce")
semanal = semanal.dropna(subset=["semana_inicio"]).sort_values("semana_inicio")
for df in data.values():
    if "ofertas" in df:
        df["ofertas"] = pd.to_numeric(df["ofertas"],errors="coerce").fillna(0)
    if "vacantes" in df:
        df["vacantes"] = pd.to_numeric(df["vacantes"],errors="coerce").fillna(0)

st.markdown('<div class="hero"><div class="eyebrow">OBSERVATORIO DEL MERCADO LABORAL · PANAMÁ</div><h1>Explorador de ofertas Konzerta</h1><p>Datos de 2026 · Pipeline bronce → plata → oro · Visualizaciones interactivas</p></div>', unsafe_allow_html=True)
st.caption("Fuente: archivo Konzerta 08-oct-2026.xlsx. Las cifras describen anuncios capturados, no todo el mercado laboral panameño.")

with st.sidebar:
    st.header("🎛️ Panel de control")
    st.caption("Explora áreas, modalidades y distribución territorial.")
    opciones_area = sorted(areas["area"].dropna().astype(str).unique())
    seleccion_areas = st.multiselect("Áreas profesionales", opciones_area, default=opciones_area)
    opciones_prov = sorted(geo["provincia"].dropna().astype(str).unique())
    seleccion_prov = st.multiselect("Ubicaciones registradas", opciones_prov, default=opciones_prov)
    metricas = st.radio("Medida principal", ["Anuncios", "Vacantes declaradas"], horizontal=True)
    top_n = st.slider("Cantidad de categorías", 5, 20, 10)
    st.divider()
    st.info("El filtro de áreas afecta áreas, subáreas, modalidades y geografía. El filtro de ubicación afecta solo geografía. Salarios y tendencia muestran el total del archivo.")
    if st.button("Restablecer filtros", use_container_width=True):
        st.session_state.clear()
        st.rerun()

areas_f = areas[areas["area"].isin(seleccion_areas)].copy()
mod_f = mod[mod["area"].isin(seleccion_areas)].copy()
geo_f = geo[geo["area"].isin(seleccion_areas) & geo["provincia"].isin(seleccion_prov)].copy()
columna = "ofertas" if metricas=="Anuncios" else "vacantes"
total_general = int(areas["ofertas"].sum())
total_area = int(areas_f["ofertas"].sum())
total_geo = int(geo_f["ofertas"].sum())
total_vacantes = int(areas_f["vacantes"].sum())

c1,c2,c3,c4 = st.columns(4)
c1.metric("Anuncios · áreas", f"{total_area:,}", f"{total_area/total_general:.1%} del archivo" if total_general else None)
c2.metric("Vacantes · áreas", f"{total_vacantes:,}")
c3.metric("Anuncios · ubicación y área", f"{total_geo:,}")
c4.metric("Áreas seleccionadas", f"{len(seleccion_areas):,}")

tab1,tab2,tab3,tab4,tab5 = st.tabs(["📊 Panorama","🧭 Geografía","🏠 Modalidades","💰 Salarios","📅 Evolución"])

with tab1:
    st.subheader("¿Dónde se concentran las oportunidades?")
    totales = areas_f.groupby("area",as_index=False)[["ofertas","vacantes"]].sum().sort_values(columna,ascending=False).head(top_n)
    if totales.empty:
        st.warning("Selecciona al menos un área profesional.")
    else:
        fig = px.bar(totales.sort_values(columna),x=columna,y="area",orientation="h",
                     text=columna, title=f"Áreas con más {metricas.lower()}",
                     labels={"area":"Área profesional",columna:metricas},color=columna,
                     color_continuous_scale=["#2563eb","#38bdf8","#67e8f9"])
        fig.update_traces(textposition="outside",cliponaxis=False)
        fig.update_layout(coloraxis_showscale=False)
        grafico(fig,470)
        st.subheader("Especialidades destacadas")
        sub = areas_f.sort_values(columna,ascending=False).head(top_n)
        fig2 = px.bar(sub.sort_values(columna),x=columna,y="subarea",color="area",
                      orientation="h",title="Subáreas por área profesional",
                      labels={"subarea":"Subárea",columna:metricas,"area":"Área"},
                      color_discrete_sequence=PALETTE)
        grafico(fig2,470)
        with st.expander("Ver y descargar datos de áreas y subáreas"):
            st.dataframe(areas_f.sort_values("ofertas",ascending=False),hide_index=True,use_container_width=True)
            tabla_descargable(areas_f,"konzerta_areas_filtradas.csv")

with tab2:
    st.subheader("Distribución territorial")
    st.caption("«Otra» y «Sin dato», si aparecen, son etiquetas del archivo, no provincias oficiales. No se reasignan sin comprobar la localidad.")
    if geo_f.empty:
        st.warning("No hay resultados para la combinación seleccionada.")
    else:
        por_prov = geo_f.groupby("provincia",as_index=False)[["ofertas","vacantes"]].sum().sort_values(columna)
        left,right=st.columns([1.1,1])
        with left:
            fig=px.bar(por_prov,x=columna,y="provincia",orientation="h",text=columna,
                       title=f"{metricas} por ubicación registrada",color_discrete_sequence=["#38bdf8"])
            grafico(fig,480)
        with right:
            niveles=geo_f.groupby("nivel_laboral",as_index=False)["ofertas"].sum().sort_values("ofertas",ascending=False)
            fig=px.pie(niveles,names="nivel_laboral",values="ofertas",hole=.62,
                       title="Niveles laborales · selección geográfica",
                       color_discrete_sequence=PALETTE)
            grafico(fig,480)
        heat=geo_f.groupby(["provincia","area"],as_index=False)["ofertas"].sum()
        top_areas=heat.groupby("area")["ofertas"].sum().nlargest(top_n).index
        heat=heat[heat["area"].isin(top_areas)]
        if not heat.empty:
            piv=heat.pivot_table(index="provincia",columns="area",values="ofertas",aggfunc="sum",fill_value=0)
            fig=px.imshow(piv,aspect="auto",text_auto=True,title="Mapa de calor · ubicación × área",
                          labels={"x":"Área profesional","y":"Ubicación","color":"Anuncios"},
                          color_continuous_scale="Blues")
            grafico(fig,max(380,50*len(piv)+160))
        with st.expander("Ver y descargar datos geográficos"):
            st.dataframe(geo_f,hide_index=True,use_container_width=True)
            tabla_descargable(geo_f,"konzerta_geografia_filtrada.csv")

with tab3:
    st.subheader("¿Qué modalidades de trabajo predominan?")
    if mod_f.empty:
        st.warning("Selecciona al menos un área.")
    else:
        general=mod_f.groupby("modalidad",as_index=False)["ofertas"].sum()
        l,r=st.columns([1,1.3])
        with l:
            fig=px.pie(general,names="modalidad",values="ofertas",hole=.62,
                       title="Modalidades en las áreas seleccionadas",color_discrete_sequence=PALETTE)
            grafico(fig)
        with r:
            top=mod_f.groupby("area")["ofertas"].sum().nlargest(top_n).index
            detalle=mod_f[mod_f["area"].isin(top)].copy()
            detalle["porcentaje"]=detalle["ofertas"]/detalle.groupby("area")["ofertas"].transform("sum")*100
            fig=px.bar(detalle,x="porcentaje",y="area",color="modalidad",orientation="h",
                       barmode="stack",title="Composición porcentual por área",
                       labels={"porcentaje":"Porcentaje (%)","area":"Área"},color_discrete_sequence=PALETTE)
            fig.update_layout(xaxis_range=[0,100])
            grafico(fig)
        with st.expander("Ver y descargar modalidades"):
            st.dataframe(mod_f,hide_index=True,use_container_width=True)
            tabla_descargable(mod_f,"konzerta_modalidades_filtradas.csv")

with tab4:
    st.subheader("Salarios publicados: análisis exploratorio")
    st.warning("Los filtros territoriales y de áreas no afectan esta sección: las tablas salariales de capa oro no contienen esas dimensiones. La moneda y periodicidad no están verificadas.")
    l,r=st.columns(2)
    with l:
        if not sal_exp.empty:
            fig=px.bar(sal_exp,x="rango_experiencia",y="salario_max_mediana",
                       text="ofertas",title="Mediana del salario máximo · experiencia",
                       labels={"rango_experiencia":"Experiencia","salario_max_mediana":"Importe (unidad no confirmada)"},
                       color_discrete_sequence=["#38bdf8"])
            grafico(fig)
            st.caption(f"Solo {int(sal_exp['ofertas'].sum())} anuncios con salario y experiencia válidos. Los números sobre las barras indican tamaño de muestra.")
        else:
            st.info("No hay registros suficientes para experiencia y salario.")
    with r:
        if not sal_nivel.empty:
            fig=px.bar(sal_nivel.sort_values("salario_max_mediana"),x="salario_max_mediana",
                       y="nivel_laboral",orientation="h",text="ofertas",
                       title="Mediana del salario máximo · nivel laboral",
                       labels={"nivel_laboral":"Nivel","salario_max_mediana":"Importe (unidad no confirmada)"},
                       color_discrete_sequence=["#a78bfa"])
            grafico(fig)
        else:
            st.info("No hay salarios por nivel laboral.")
    with st.expander("Consultar y descargar tablas salariales"):
        st.write("Salarios según experiencia")
        st.dataframe(sal_exp,hide_index=True,use_container_width=True)
        tabla_descargable(sal_exp,"konzerta_salarios_experiencia.csv")
        st.write("Salarios según nivel")
        st.dataframe(sal_nivel,hide_index=True,use_container_width=True)
        tabla_descargable(sal_nivel,"konzerta_salarios_nivel.csv")

with tab5:
    st.subheader("Evolución semanal de anuncios")
    st.caption("Serie descriptiva del archivo. Las semanas inicial y final pueden estar incompletas; no representa predicción ni seguimiento en tiempo real.")
    if semanal.empty:
        st.info("No hay semanas válidas.")
    else:
        fechas=semanal["semana_inicio"].dt.date
        inicio,fin=st.select_slider("Período observado",options=sorted(fechas.unique()),
                                     value=(fechas.min(),fechas.max()))
        periodo=semanal[(fechas>=inicio)&(fechas<=fin)]
        fig=px.area(periodo,x="semana_inicio",y="ofertas",markers=True,
                    title="Anuncios por semana",labels={"semana_inicio":"Semana que inicia","ofertas":"Anuncios"},
                    color_discrete_sequence=["#38bdf8"])
        grafico(fig,460)
        a,b=st.columns(2)
        a.metric("Anuncios del período",f"{int(periodo['ofertas'].sum()):,}")
        b.metric("Semanas representadas",f"{len(periodo):,}")
        with st.expander("Ver y descargar serie semanal"):
            st.dataframe(periodo,hide_index=True,use_container_width=True)
            tabla_descargable(periodo,"konzerta_tendencia_semanal.csv")

st.divider()
st.subheader("Conclusiones y alcance")
st.write("Este observatorio compara la concentración de anuncios por área, ubicación y modalidad a partir de datos agregados. "
         "Las cifras salariales son exploratorias por su baja cobertura y la tendencia semanal describe únicamente el período capturado.")
st.caption("Fuente exclusiva: seis CSV de datos/oro. No se consulta bronce ni plata desde Streamlit. Dashboard académico, no una muestra representativa de todo Panamá.")
