# Proyecto Konzerta — Guía completa del análisis y dashboard

> **Guía de lectura para integrantes del equipo:** este documento explica qué se construyó, cómo funciona, por qué se eligió cada herramienta, cómo reproducir el análisis y qué limitaciones deben mencionarse al exponerlo.

**Asignatura:** Introducción a la Programación para Ciencia de Datos  
**Integrantes indicados en el notebook:** Francia Vergara, Luis Santimateo y Yenia Rojas  
**Fuente:** [Konzerta](https://www.konzerta.com/)  
**Archivo de entrada:** `Konzerta 08-oct-2026.xlsx`  
**Fecha de obtención consignada en la portada:** 16 de octubre de 2026 (conviene cotejarla con el archivo original).

## 1. ¿Qué hicimos y para qué?

Creamos un proyecto de análisis de anuncios de empleo publicados en Konzerta para estudiar cinco preguntas:

1. **Áreas y subáreas:** ¿qué perfiles profesionales concentran más anuncios y vacantes?
2. **Salarios:** ¿cómo se relacionan los salarios informados con la experiencia requerida y el nivel laboral?
3. **Modalidades:** ¿cuánto trabajo presencial, remoto o híbrido aparece en las distintas áreas?
4. **Geografía:** ¿cómo se distribuyen los anuncios por ubicación, área y nivel laboral?
5. **Tiempo:** ¿cómo cambia la cantidad de anuncios por semana entre julio y octubre de 2026, dentro del período observado?

El proyecto no consulta las ofertas en tiempo real: analiza un **archivo específico**. Cada fila representa un anuncio. **Un anuncio no equivale necesariamente a una vacante**: el campo `vacantes` registra cuántas plazas declara el anuncio.

La solución tiene dos productos: un **notebook de Jupyter** que prepara y analiza los datos y un **dashboard web con Streamlit** que presenta los resultados para explorarlos.

## 2. Arquitectura: de datos crudos a gráficos

```text
Excel original (BRONCE)
        │
        ▼
Lectura y perfilado de calidad
        │
        ▼
Normalización + bitácora (PLATA)
        │
        ▼
Análisis exploratorio y agregaciones (ORO)
        │
        ▼
Dashboard Streamlit + Plotly
```

Esta organización se conoce como **arquitectura medallón**. Separa el dato de origen, el dato limpio y los resúmenes listos para visualización.

| Capa | Qué contiene | Por qué se usa |
|---|---|---|
| **Bronce** | Excel original sin modificar | Permite regresar a la fuente y repetir el análisis |
| **Plata** | Datos estandarizados, bitácora y perfiles de calidad | Hace explícitas las decisiones de limpieza |
| **Oro** | Seis tablas agregadas | Evita que el dashboard repita la limpieza o lea el Excel |

**Decisión importante:** el dashboard **solo lee los seis CSV de oro**. El notebook es responsable de generar y actualizar esos archivos. Por tanto, el dashboard no cambia cuando se modifica el Excel hasta que se vuelve a ejecutar el pipeline y se actualizan los CSV.

## 3. Estructura de carpetas

```text
Proyecto_Konzerta/
├── datos/
│   ├── bronce/
│   │   └── Konzerta 08-oct-2026.xlsx
│   ├── plata/                     # generado por el notebook
│   └── oro/                       # generado por el notebook
├── notebooks/
│   └── Proyecto_Konzerta_KR.ipynb
├── dashboard/
│   └── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

- **`notebooks/Proyecto_Konzerta_KR.ipynb`:** ejecuta el pipeline y desarrolla las cinco preguntas.
- **`dashboard/app.py`:** contiene la interfaz y los gráficos interactivos.
- **`requirements.txt`:** lista las dependencias instalables.
- **`.gitignore`:** excluye, entre otros, los entornos virtuales y archivos temporales.
- **`README.md`:** esta documentación.

## 4. Herramientas utilizadas y por qué

| Herramienta | Uso real en el proyecto | Justificación |
|---|---|---|
| **Python** | Lenguaje del notebook y del dashboard | Permite automatizar el proceso completo |
| **pandas** | Leer Excel, limpiar, agrupar, resumir y exportar CSV | Simplifica el manejo de tablas |
| **pathlib** | Construir rutas de carpetas y archivos | Funciona en macOS, Windows y Colab |
| **re** | Sustituir caracteres y espacios mediante expresiones regulares | Ayuda a normalizar nombres y textos |
| **unicodedata** | Separar acentos y marcas Unicode en nombres de columnas | Produce nombres consistentes |
| **Plotly Express** | Gráficos de barras, líneas, dona y otras visualizaciones | Ofrece interacción, zoom y detalles al pasar el cursor |
| **Streamlit** | Construcción del dashboard, filtros, pestañas, métricas y descargas | Permite publicar una interfaz web usando Python |
| **openpyxl** | Motor de lectura de archivos Excel usado por pandas | Necesario para trabajar con `.xlsx` |
| **Jupyter / Colab** | Ejecutar el análisis por celdas | Facilita revisar cada etapa y mostrar evidencias |
| **Git / GitHub** | Versionar notebook, código y documentación | Permite compartir cambios y recuperar versiones |
| **Google Drive** | Guardar datos y resultados al ejecutar en Colab | Conserva los archivos fuera de la sesión temporal |

**Nota:** `pathlib`, `re` y `unicodedata` pertenecen a la biblioteca estándar de Python; no requieren instalación por separado.

## 5. Explicación paso a paso del notebook

### 5.1. Configuración del entorno

La primera celda de código detecta si se ejecuta en Google Colab mediante `"google.colab" in sys.modules`. Si está en Colab, monta Drive y utiliza `/content/drive/MyDrive/Proyecto_Konzerta`. En ejecución local, busca la carpeta `Proyecto_Konzerta` a partir del directorio de trabajo y sus carpetas superiores.

Se definen las rutas `BRONCE`, `PLATA`, `ORO`, `NOTEBOOKS` y `DASHBOARD` con `Path`, y se crean las carpetas necesarias con `mkdir(parents=True, exist_ok=True)`.

**Por qué:** el mismo notebook puede ejecutarse en Mac, Windows y Colab sin cambiar las rutas manualmente, siempre que la estructura de carpetas sea la esperada.

### 5.2. Capa bronce: leer y examinar el archivo

```python
crudos = pd.read_excel(archivo_excel)
konzerta = crudos.copy()
```

- `pd.read_excel()`: carga el Excel a un DataFrame.
- `copy()`: evita trabajar directamente sobre la tabla original.
- `shape`, `head()` e `info()`: permiten comprobar tamaño, ejemplos y tipos de datos.
- `isna().sum()`: cuenta valores faltantes.
- `duplicated().sum()`: detecta filas repetidas.
- `describe().T`: resume las variables numéricas.

**Por qué:** antes de modificar datos es necesario saber qué contienen, qué falta y qué valores podrían ser incorrectos.

### 5.3. Capa plata: normalización y limpieza

Se inicia desde `crudos.copy(deep=True)` para que la limpieza sea reproducible.

**a) Normalización de columnas.** La función personalizada `normalizar_columna(nombre)` utiliza `unicodedata.normalize("NFKD", ...)` y `re.sub()` para quitar marcas diacríticas, reemplazar caracteres especiales por guiones bajos y convertir los nombres a minúsculas (`snake_case`). Esto facilita escribir código sin diferencias de acentos o espacios.

**b) Limpieza de textos.** Se usa `astype("string")`, `str.strip()` y `str.replace(r"\s+", " ", regex=True)` para quitar espacios sobrantes; las cadenas vacías se convierten en nulos. El notebook excluye `descripcion` y `url` de esa transformación textual.

**c) Conversión de tipos.** `pd.to_datetime(..., errors="coerce")` interpreta fechas; `pd.to_numeric(..., errors="coerce")` interpreta números. Los valores no interpretables quedan como ausentes en lugar de provocar la interrupción del proceso.

**d) Tratamiento de faltantes.** En `area`, `subarea`, `provincia`, `localidad`, `nivel_laboral` y `modalidad`, los nulos se representan como `Sin dato`. En campos numéricos se conservan los nulos para **no inventar salarios, edades ni vacantes**.

**e) Duplicados.** `drop_duplicates()` elimina únicamente filas idénticas. El notebook también revisa identificadores repetidos durante la exploración inicial.

**f) Revisión salarial.** Se calculan cuartiles (`quantile(0.25)` y `quantile(0.75)`) y el rango intercuartílico (IQR). Se marcan registros con importes inconsistentes o extremos en la nueva columna `estado_salario`, con valores `Sin dato`, `Registro sin alerta` o `Revisar`. **Se conservan los importes; no se borran automáticamente los valores atípicos.**

**g) Bitácora.** La función `registrar(columna, problema, decision, filas_afectadas)` guarda cada decisión de limpieza en una lista, que luego se convierte en un DataFrame. Esto permite explicar qué se modificó y cuántas filas se vieron afectadas.

**h) Verificación.** Se comparan los perfiles antes y después de la limpieza, la cantidad de registros, los tipos y los faltantes. Se comprueba también la presencia de columnas esenciales.

### 5.4. Exportación de plata

El notebook genera:

| Archivo | Contenido |
|---|---|
| `konzerta_limpio.csv` | Tabla estandarizada con los anuncios |
| `bitacora_limpieza.csv` | Problemas detectados y decisiones tomadas |
| `perfil_bronce.csv` | Tipos y faltantes antes de limpiar |
| `perfil_plata.csv` | Tipos, faltantes y etiquetas `Sin dato` después de limpiar |

Se usa `to_csv(index=False, encoding="utf-8-sig")` para producir archivos compatibles con herramientas que abren CSV en español.

### 5.5. Análisis exploratorio: las cinco preguntas

**Pregunta 1 — Áreas y subáreas.** `groupby()` agrupa por `area` o por `["area", "subarea"]`. `agg(ofertas=("id","size"), vacantes=("vacantes","sum"))` cuenta anuncios y suma vacantes declaradas. `sort_values()` ordena los resultados y `head(10)` selecciona las categorías más frecuentes. Se calculan porcentajes sobre el total.

**Pregunta 2 — Salarios y experiencia.** Se filtran anuncios con salario máximo positivo y estado `Registro sin alerta`. Luego se seleccionan aquellos con experiencia informada. `pd.cut()` clasifica meses de experiencia en rangos; `groupby().agg()` calcula promedio, mediana, mínimo y máximo salarial. El nivel laboral se analiza por separado. Se utilizan barras y un gráfico de caja en el notebook. **No debe afirmarse que exista una relación salarial generalizable** debido a la pequeña muestra que incluye salario y experiencia simultáneamente.

**Pregunta 3 — Modalidad.** `value_counts()` resume las modalidades. `pd.crosstab(..., normalize="index")` obtiene porcentajes de modalidad dentro de cada área; `melt()` reorganiza los datos para dibujar barras apiladas. Así se comparan proporciones, no solo números absolutos.

**Pregunta 4 — Geografía y nivel laboral.** `groupby()` combina provincia, área y nivel laboral para contar anuncios y comparar ubicaciones. La etiqueta **`Otra` no es una provincia oficial**; si aparece, debe investigarse en la fuente original. El notebook incluye una consulta de registros con ese valor. No se debe cambiar automáticamente por una provincia concreta.

**Pregunta 5 — Evolución semanal.** `pd.to_datetime()` interpreta fechas de publicación; `dt.to_period("W-SUN").dt.start_time` agrupa las semanas comenzando el lunes; `pd.date_range()` y `reindex(fill_value=0)` incluyen semanas sin registros. El código limita el análisis al **16 de octubre de 2026**, fecha documentada en la portada, y marca `semana_parcial` para evitar comparar semanas incompletas como si fueran completas.

## 6. Capa oro: los archivos que alimentan Streamlit

Las seis tablas se crean con `groupby()`, `agg()`, `reset_index()` y `to_csv()`:

| Archivo | Agrupación / contenido | Uso en el dashboard |
|---|---|---|
| `oro_areas_subareas.csv` | Área y subárea; ofertas y vacantes | Panorama profesional |
| `oro_modalidades_area.csv` | Área y modalidad; ofertas | Modalidades de trabajo |
| `oro_geografia.csv` | Provincia, área y nivel laboral; ofertas y vacantes | Distribución geográfica |
| `oro_salarios_experiencia.csv` | Rangos de experiencia y estadísticas salariales | Salarios por experiencia |
| `oro_salarios_nivel.csv` | Nivel laboral y estadísticas salariales | Salarios por nivel |
| `oro_tendencia_semanal.csv` | Semana de inicio, ofertas y marca de semana parcial | Tendencia temporal |

Al final se ejecutan verificaciones con `assert`: los totales de ofertas de las agregaciones principales deben coincidir con la cantidad de anuncios limpios y los seis archivos deben existir.

**Atención:** estas comprobaciones son parte del código, pero hay que ejecutar el notebook completo para confirmar que pasan con la versión actual del Excel.

## 7. ¿Cómo funciona el dashboard?

El archivo `dashboard/app.py` utiliza:

- **`st.set_page_config()`**: define título, icono y diseño ancho.
- **`st.cache_data`**: almacena temporalmente los CSV leídos para no recargarlos en cada interacción. La función de lectura recibe también la fecha de modificación del archivo para invalidar la caché cuando cambia.
- **`st.sidebar.multiselect()`**: filtra áreas y ubicaciones disponibles.
- **`st.slider()`**: cambia la cantidad de categorías mostradas.
- **`st.metric()`**: presenta indicadores numéricos.
- **`st.tabs()`**: organiza las cinco preguntas en secciones.
- **`px.bar()`, `px.pie()`, `px.line()`**: crean gráficos interactivos.
- **`st.plotly_chart()`**: muestra gráficos dentro de Streamlit.
- **`st.expander()` y `st.dataframe()`**: permiten consultar tablas sin saturar la página.
- **`st.download_button()`**: descarga la tabla de la sección en CSV.
- **`st.error()`, `st.warning()` y `st.stop()`**: explican archivos faltantes, filtros sin resultados o problemas de lectura.

**Comportamiento de filtros (importante para explicarlo):**

| Sección | Filtro de área | Filtro de ubicación |
|---|---|---|
| Panorama | Sí | No |
| Modalidades | Sí | No |
| Geografía | Sí | Sí |
| Salarios | No | No |
| Tendencia | No | No |

Esto **no es un error de Streamlit**: las tablas oro de salarios y semanas no contienen las columnas `area` ni `provincia`, así que no sería correcto aplicarles esos filtros. Los indicadores del dashboard distinguen explícitamente entre totales por área y totales filtrados por ubicación.

**Limitación de la versión actual:** no se han realizado pruebas funcionales completas del dashboard con los seis CSV reales en Mac y Windows. Los controles y la estructura están implementados, pero deben validarse ejecutando la aplicación.

## 8. Instalación y ejecución

Se recomienda **Python 3.10 o superior**. El entorno virtual `.venv` se crea de forma independiente en cada computadora.

### macOS — Terminal

Desde la carpeta principal `Proyecto_Konzerta`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

### Windows — PowerShell

Desde la misma carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

Si PowerShell bloquea la activación, se puede ejecutar el intérprete del entorno sin activarlo:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

El dashboard se abre normalmente en **http://localhost:8501**. Para detenerlo, presiona **Ctrl+C** en la terminal.

**Antes de ejecutar Streamlit**, asegúrate de que existan los seis CSV en `Proyecto_Konzerta/datos/oro`. Si no existen, primero ejecuta el notebook en orden con Jupyter, VS Code o Colab. En Mac/Windows puedes abrir el notebook desde VS Code con la extensión de Jupyter; `requirements.txt` no instala por sí solo la interfaz de Jupyter.

### Google Colab y Google Drive

En Colab, el notebook monta Google Drive y usa:

```text
/content/drive/MyDrive/Proyecto_Konzerta/
```

Allí debe existir `datos/bronce/Konzerta 08-oct-2026.xlsx`. Al ejecutar todas las celdas se generan `datos/plata` y `datos/oro` en Drive.

**Drive no sincroniza automáticamente esos CSV con la carpeta local de GitHub.** Para usar el dashboard en Mac o Windows hay que copiar/sincronizar los seis CSV de `datos/oro` a la carpeta local correspondiente. GitHub versiona el código, pero no ejecuta el pipeline automáticamente.

## 9. Guía rápida para explicar el proyecto a otra persona

**¿De dónde salen los datos?** Del Excel original de anuncios de Konzerta.

**¿Por qué no graficamos directamente el Excel?** Porque primero verificamos su calidad, estandarizamos valores y documentamos las decisiones de limpieza.

**¿Por qué tres capas?** Para conservar la fuente, separar las transformaciones y alimentar el dashboard con tablas listas para consulta.

**¿Qué hace pandas?** Lee el Excel, revisa faltantes y duplicados, transforma fechas y números, agrupa registros y genera los CSV.

**¿Qué hace Plotly?** Convierte las tablas de resultados en gráficos interactivos.

**¿Qué hace Streamlit?** Presenta esos gráficos y permite cambiar filtros, consultar tablas y descargarlas desde una página web.

**¿Cómo se actualiza?** Se reemplaza o actualiza el Excel de origen, se ejecuta el notebook completo, se generan nuevamente las capas plata y oro y se sincronizan los CSV donde corre el dashboard.

**¿Por qué los salarios tienen advertencias?** Porque pocos anuncios informan salario y experiencia al mismo tiempo, y la moneda/periodicidad no están confirmadas de forma homogénea.

**¿Qué significa «Otra» en provincia?** Es un valor presente en la dimensión de ubicación; no es una provincia oficial y requiere revisar la localidad original.

## 10. Limitaciones y puntos pendientes de revisión

1. **Representatividad:** los anuncios del Excel no equivalen a todas las ofertas de empleo de Panamá.
2. **Salarios:** el notebook documenta 414 anuncios con salario máximo sin alerta y 10 con salario y experiencia, según una ejecución registrada. Estas cantidades pueden variar si cambia la fuente.
3. **Ubicaciones:** revisar `Otra` y `Sin dato` antes de interpretar un mapa o una comparación provincial.
4. **Fechas:** confirmar que el 16 de octubre de 2026 sea la fecha de extracción correcta; el nombre del Excel incluye el 8 de octubre.
5. **Sincronización:** no existe aún una sincronización automática completa Mac/Windows ↔ Drive ↔ GitHub.
6. **Pruebas:** ejecutar notebook y dashboard con los CSV actuales; comprobar filtros, tablas, descargas y gráficos en macOS y Windows.
7. **Actualización:** la interfaz muestra datos estáticos del archivo, no información en tiempo real.

## 11. Lista de verificación para la entrega

- [ ] Confirmar que el Excel original está en `datos/bronce`.
- [ ] Ejecutar el notebook completo, sin errores.
- [ ] Verificar los cuatro CSV de plata.
- [ ] Verificar los seis CSV de oro y sus totales.
- [ ] Comprobar los cinco apartados del dashboard.
- [ ] Probar filtros y descargas de cada sección.
- [ ] Revisar la interpretación de `Otra` y las fechas.
- [ ] Probar instalación y ejecución en los sistemas que usará el equipo.
- [ ] Documentar capturas de resultados y conclusiones sin generalizaciones indebidas.

---

**Resumen en una frase:** el notebook transforma y documenta los datos de Konzerta mediante las capas bronce, plata y oro; el dashboard consume exclusivamente la capa oro para explorar cinco preguntas sobre las ofertas de empleo.


## 12. Recomendaciones de cambios a partir de los documentos del equipo

Esta sección distingue **requisitos obligatorios** (PDF actualizado del profesor: `Proyecto final Introducción a la Programación para Ciencia de Datos (1).pdf`) de **recomendaciones de trabajo** (documento `Guia_paso_a_paso_Proyecto_Konzerta_Equipo.docx`, versión 24/10/2026). El objetivo es que cada integrante entienda qué se sugirió, qué se incorporó y qué debe verificarse. **No se atribuyen al profesor requisitos que solo figuran en la guía del compañero.**

### 12.1. Matriz de recomendaciones y estado

| Fuente | Recomendación o requisito | Situación en nuestro proyecto | Acción pendiente |
|---|---|---|---|
| Profesor | Conservar el Excel sin modificar en bronce | El notebook lee `datos/bronce` y transforma una copia | Comprobar integridad del archivo en la entrega |
| Profesor | Normalizar tipos, textos, faltantes, duplicados y atípicos; justificar decisiones | Se implementó limpieza y bitácora de cuatro campos | Revisar si las categorías equivalentes requieren unificación adicional; validar reglas con la fuente |
| Guía del equipo | Bitácora simplificada de dos columnas: Columna y Justificación | El notebook conserva cuatro columnas, que aportan trazabilidad | Si el equipo desea el formato de la guía, crear una **vista resumida** sin perder el registro detallado. El PDF del profesor exige justificación, pero no impone dos columnas |
| Profesor | Al menos dos tablas oro y cinco gráficos que cuenten una historia | Hay seis tablas oro y cinco secciones del dashboard | Verificar gráficos, títulos, ejes, unidades e interpretaciones con los CSV reales |
| Profesor | Dashboard alimentado solo por oro y actualizable al reejecutar el pipeline | Streamlit solo lee oro; el notebook exporta las tablas | Demostrar actualización de datos en el entorno de entrega, sin editar cifras a mano |
| Guía del equipo | Repartir preguntas en bloques A/B/C, limpiar e integrar entre los tres | Las cinco preguntas están implementadas en un notebook | Acordar responsables, revisión cruzada y comprobar que los tres entienden todas las secciones |
| Profesor | Diccionario de datos, fuente, fecha y README para ejecutar | Hay diccionario en notebook y guía técnica en README | Confirmar fecha de obtención y trasladar hallazgos, conclusiones y aprendizajes definitivos al material de entrega |
| Profesor | Grabación colaborativa de al menos una hora, con los tres integrantes, enlazada en README | No se ha verificado la grabación ni su enlace | Grabar, comprobar permisos y añadir URL al README |
| Profesor | Presentación/defensa de 30 minutos, demostración en vivo y defensa individual | El README explica el funcionamiento, pero no reemplaza el ensayo | Preparar presentación, demostración y respuestas individuales |
| Profesor | ZIP grupal ejecutable en otra computadora | Existe estructura del proyecto y `requirements.txt` | Probar el ZIP descomprimido en otra ruta y, de ser posible, en Mac y Windows |

### 12.2. Cambios recomendados al notebook y al dashboard

**Prioridad alta — antes de la entrega**

1. **Verificar la ejecución completa:** ejecutar todas las celdas del notebook desde cero, confirmar los cuatro CSV de plata, los seis CSV de oro y las validaciones finales. El código guardado en GitHub no equivale a una ejecución comprobada.
2. **Validar los datos geográficos:** revisar las filas clasificadas como `Otra` y `Sin dato` antes de interpretar la distribución provincial. No asignar provincias sin evidencia en `localidad`.
3. **Revisar la fecha de extracción:** el nombre del Excel menciona 08-oct-2026, mientras que la portada consigna 16-oct-2026. Confirmar la fecha válida en los metadatos o en el procedimiento de obtención y ajustar el análisis temporal si corresponde.
4. **Verificar filtros y descargas del dashboard:** comprobar que cada filtro afecta solo las secciones que pueden calcularse con las dimensiones de oro y que las tablas exportadas coinciden con lo mostrado.
5. **Revisar la presentación de los gráficos:** todos deben incluir títulos claros, ejes y unidades cuando correspondan, y una interpretación breve basada en resultados realmente observados. Organizar la exposición en contexto → hallazgos → conclusión.
6. **Comprobar actualización automática:** modificar de manera controlada una copia del Excel de prueba, reejecutar el pipeline y verificar que los CSV oro y el dashboard cambian sin edición manual. Restaurar después los datos originales.

**Prioridad media — mejorar la comprensión y defensa**

7. Añadir al informe o presentación una comparación concreta **antes/después**: dimensiones, tipos, faltantes y ejemplos de normalización, obtenidos de los perfiles bronce y plata.
8. Explicar por qué se conservan nulos numéricos y por qué los salarios atípicos se marcan para revisión en lugar de eliminarlos automáticamente.
9. Explicar la diferencia entre **ofertas** (anuncios) y **vacantes** (plazas declaradas), y que la muestra salarial con experiencia es muy pequeña.
10. Preparar una reflexión personal de cada integrante sobre dificultades, decisiones y aprendizajes, sin inventar resultados de pruebas no realizadas.

### 12.3. Organización sugerida por la guía del compañero

La guía del 24 de octubre propone distribuir el trabajo así, **como sugerencia, no como exigencia del profesor**:

- **Bloque A:** preguntas 1 y 4 — áreas, vacantes, geografía y nivel laboral; revisa el bloque B.
- **Bloque B:** preguntas 3 y 5 — modalidades y evolución semanal; revisa el bloque C.
- **Bloque C:** pregunta 2 — salarios y experiencia, además de calidad de datos; revisa el bloque A.

La limpieza inicial, la integración, las pruebas y la preparación de la defensa deben ser colaborativas. La guía propone una **primera versión completa el 28/10/2026**, como fecha interna; el PDF actualizado fija la **presentación para el 07/11/2026**.

### 12.4. Aclaración sobre versiones de los documentos

Para evitar confusiones durante la defensa:

- **Duración de la defensa:** el PDF actualizado del profesor indica **30 minutos**, aunque la guía del equipo mencione 20.
- **Rúbrica:** el PDF actualizado distribuye **50 puntos para el trabajo y 50 para la sustentación**; la guía del equipo reproduce una distribución diferente. Usar la rúbrica actualizada.
- **Carpetas:** el PDF actualizado pide explícitamente `datos/bronce`, `datos/plata`, `datos/oro`, `notebooks` y `reporte` o `dashboard`; nuestra estructura sigue ese esquema.
- **Enlace a la grabación:** el PDF actualizado solicita incluirlo en el **README**. Puede repetirse en la presentación para facilitar el acceso, pero no debe faltar en el README.

### 12.5. Información pendiente para cerrar la documentación

**Enlace a la grabación colaborativa:** pendiente de añadir y verificar.  
**Hallazgos definitivos:** actualizar con las cifras de la última ejecución validada.  
**Conclusiones y aprendizajes personales:** completar y revisar entre los tres integrantes.  
**Evidencia de ejecución multiplataforma y demostración de actualización:** pendiente de documentar.
