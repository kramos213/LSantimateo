# Proyecto Konzerta: análisis de ofertas laborales en Panamá

**Asignatura:** Introducción a la Programación para Ciencia de Datos — Maestría en Ciencias de los Datos, UIP  
**Integrantes:** Francia Vergara, Luis Santimateo y Yenia Rojas  
**Fuente:** conjunto de anuncios de empleo de Konzerta, archivo `Konzerta 08-oct-2026.xlsx`  
**Presentación prevista:** 7 de noviembre de 2026  
**Guía técnica para integrantes:** [README_LUIS.md](README_LUIS.md)

## 1. Resumen del proyecto

Se desarrolló un pipeline reproducible en Python para analizar anuncios laborales del archivo Konzerta, desde los datos originales hasta seis tablas agregadas y un dashboard interactivo en Streamlit y Plotly. El proyecto responde preguntas sobre demanda profesional, salarios y experiencia, modalidades, distribución territorial y evolución semanal. La arquitectura medallón separa las capas bronce, plata y oro; el dashboard lee **exclusivamente** los CSV de la capa oro.

**Alcance:** los resultados representan los anuncios del archivo analizado y no constituyen una estimación de todo el mercado laboral panameño.

## 2. Objetivo general y preguntas de investigación

**Objetivo:** transformar datos reales de anuncios laborales en información consistente, verificable y explorable mediante un flujo automatizado de limpieza, análisis y visualización.

Preguntas:

1. ¿Qué áreas y subáreas concentran más anuncios y vacantes?
2. ¿Qué relación descriptiva existe entre salarios informados, experiencia y nivel laboral?
3. ¿Cómo se distribuyen las modalidades de trabajo por área?
4. ¿Cómo se distribuyen los anuncios por ubicación, área y nivel laboral?
5. ¿Cómo evolucionan semanalmente los anuncios en el período observado de julio a octubre de 2026?

## 3. Fuente y documentación de datos

| Elemento | Descripción |
|---|---|
| Procedencia | Datos de ofertas de empleo de Konzerta, archivo proporcionado para el proyecto académico |
| Archivo original | `datos/bronce/Konzerta 08-oct-2026.xlsx` |
| Fecha de obtención | 16/10/2026 según la portada del notebook; **pendiente de confirmar** frente al nombre del archivo |
| Unidad de análisis | Un anuncio de empleo por fila |
| Tipos de variables | Categóricas (área, provincia, modalidad), numéricas (vacantes, salario, experiencia) y fechas |
| Confidencialidad | Uso académico; revisar el archivo antes de distribuirlo para confirmar ausencia de datos personales sensibles |

**Diccionario de datos (campos principales, verificar contra la fuente antes de la entrega):**

| Columna | Tipo esperado | Descripción |
|---|---|---|
| `id` | Identificador | Código del anuncio |
| `area`, `subarea` | Texto | Clasificación profesional |
| `provincia`, `localidad` | Texto | Ubicación declarada |
| `modalidad` | Texto | Modalidad laboral |
| `nivel_laboral` | Texto | Nivel requerido |
| `vacantes` | Número | Plazas declaradas por anuncio |
| `salario_min`, `salario_max` | Número | Límites salariales publicados, cuando existen |
| `experiencia_meses` | Número | Experiencia solicitada en meses |
| `fecha_publicacion` | Fecha | Publicación del anuncio |
| `fecha_finalizacion` | Fecha | Finalización declarada |
| `extraido` | Fecha | Marca de extracción, si está presente |

El diccionario completo, con todas las columnas y tipos reales, debe generarse o adjuntarse a partir del archivo original.

## 4. Metodología: arquitectura medallón

| Capa | Proceso | Evidencia |
|---|---|---|
| **Bronce** | Conservar el Excel original sin modificar y realizar el diagnóstico inicial | Excel y perfil previo |
| **Plata** | Normalizar columnas, textos, tipos, fechas y números; revisar faltantes, duplicados y atípicos; registrar decisiones | `konzerta_limpio.csv`, `bitacora_limpieza.csv`, `perfil_bronce.csv`, `perfil_plata.csv` |
| **Oro** | Crear agregaciones orientadas a las cinco preguntas | Seis CSV `oro_*.csv` |

La limpieza conserva valores faltantes numéricos cuando no existe una base para imputarlos. Las categorías ausentes se etiquetan como `Sin dato`. Los salarios con posibles anomalías se identifican para revisión y no se eliminan indiscriminadamente.

**Bitácora:** el notebook actual exporta una bitácora con `columna`, `problema`, `decision` y `filas_afectadas`. Antes de entregar, contrastar su formato con las indicaciones vigentes y la guía del equipo.

## 5. Análisis y visualizaciones

Las seis tablas oro son:

| Archivo | Pregunta atendida |
|---|---|
| `oro_areas_subareas.csv` | Áreas y subáreas con más anuncios y vacantes |
| `oro_salarios_experiencia.csv` | Salarios según experiencia |
| `oro_salarios_nivel.csv` | Salarios según nivel laboral |
| `oro_modalidades_area.csv` | Modalidades por área |
| `oro_geografia.csv` | Ubicación, área y nivel laboral |
| `oro_tendencia_semanal.csv` | Evolución semanal |

El dashboard incluye cinco secciones: **Panorama, Modalidades, Geografía, Salarios y Tendencia**, con gráficos Plotly, indicadores, filtros según dimensiones disponibles, tablas y descargas CSV. Los filtros de ubicación no afectan salarios o tendencias porque esas tablas oro no contienen la dimensión provincial.

**Interpretación preliminar y cautelas:** las comparaciones por áreas, modalidades y geografía describen la distribución de anuncios del archivo. El análisis salarial se basa en un subconjunto reducido de registros con información suficiente; no permite extrapolar conclusiones salariales a todo el mercado. Etiquetas como `Otra` o `Sin dato` no representan provincias oficiales. Las semanas iniciales o finales pueden ser parciales.

**Hallazgos cuantitativos finales:** pendientes de incorporar tras la ejecución y validación de los CSV definitivos. No se incluyen cifras no verificadas en este README.

## 6. Estructura y herramientas

```text
Proyecto_Konzerta/
├── datos/
│   ├── bronce/      # Excel original
│   ├── plata/       # resultados de limpieza
│   └── oro/         # seis CSV para dashboard
├── notebooks/
│   └── Proyecto_Konzerta_KR.ipynb
├── dashboard/
│   └── app.py
├── requirements.txt
├── README.md
└── README_LUIS.md
```

**Herramientas:** Python, pandas, openpyxl, Plotly, Streamlit, pathlib, Jupyter/Colab y GitHub. Las dependencias del entorno están definidas en `requirements.txt`.

## 7. Instrucciones de reproducción

**Requisito recomendado:** Python 3.10 o superior. Abrir una terminal en la carpeta raíz `Proyecto_Konzerta`.

**macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

Si la activación está restringida, utilizar `.\.venv\Scripts\python.exe` en los dos últimos comandos.

**Orden de ejecución:** colocar el Excel original en `datos/bronce`; abrir y ejecutar todas las celdas de `notebooks/Proyecto_Konzerta_KR.ipynb` en Jupyter, VS Code o Colab; verificar los CSV generados en `datos/plata` y `datos/oro`; iniciar el dashboard y abrir `http://localhost:8501`.

En Colab los resultados se guardan en Google Drive; para ejecutar Streamlit en Mac o Windows hay que copiar o sincronizar los seis CSV oro a la carpeta local. GitHub no sincroniza automáticamente los datos generados.

**Verificación pendiente:** ejecutar el flujo completo en una instalación limpia, comprobar la actualización tras modificar la fuente y probar filtros y descargas en los sistemas de destino.

## 8. Conclusiones y recomendaciones

La separación en capas facilita la trazabilidad del proceso, conserva el archivo original y permite que las visualizaciones se regeneren a partir de tablas procesadas. Las cinco preguntas ofrecen perspectivas complementarias sobre el archivo de anuncios laborales. Para interpretar correctamente los resultados se debe diferenciar anuncios de vacantes, documentar las fechas de observación y reconocer la limitada cobertura salarial.

Se recomienda completar el diccionario de datos, revisar ubicaciones ambiguas, confirmar la fecha de extracción, agregar interpretaciones verificadas a cada gráfico y demostrar la actualización del dashboard con una nueva ejecución del pipeline.

## 9. Aprendizajes y dificultades

**Aspectos técnicos abordados:** lectura y normalización de Excel, tipos de datos, valores faltantes, análisis exploratorio, agregaciones, arquitectura medallón, visualizaciones interactivas y ejecución en varios entornos.

**Reflexiones individuales:** cada integrante debe incorporar sus dificultades concretas, decisiones, aprendizajes y mejoras propuestas; no se atribuyen experiencias personales que todavía no se han documentado.

## 10. Grabación, defensa y entrega

**Enlace a la grabación colaborativa (mínimo una hora con participación de los tres integrantes):** PENDIENTE DE AÑADIR.

**Presentación:** 7 de noviembre de 2026. Las indicaciones actualizadas señalan una exposición y defensa de **30 minutos**, con demostración en vivo del pipeline y el dashboard.

**Entrega:** un ZIP por grupo, con nombre `Rojas_Santimateo_Vergara_Proyecto_IPCD.zip`, que incluya el archivo original, resultados limpios, tablas oro, notebook, dashboard, `requirements.txt` y presentación o documentación requerida. No incluir `.venv`.

**Criterios del PDF actualizado:** 50 puntos para trabajo entregado y 50 para sustentación. La guía interna del equipo menciona otros valores y duración; para la entrega se siguen las indicaciones más recientes del profesor.

---

**Documentación ampliada:** [README_LUIS.md](README_LUIS.md), con explicación de funciones, código, decisiones y recomendaciones de cambios basadas en los documentos del equipo.
