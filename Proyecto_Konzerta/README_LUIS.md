# Guía exhaustiva del notebook — Luis

**Archivo explicado:** `notebooks/Proyecto_Konzerta_KR.ipynb` (54 celdas en la versión consultada). Esta guía sigue el **orden real del notebook**; no es código alternativo. Se incluyen las celdas de Python completas para que puedas relacionar cada explicación con las instrucciones exactas.

## Cómo estudiar cada celda

1. Lee el objetivo y la explicación antes de ejecutar.
2. Observa qué variables de celdas anteriores utiliza; Jupyter mantiene esas variables en memoria.
3. Ejecuta de arriba abajo; después inspecciona la salida con `display()`.
4. Si hay un error, comprueba primero la ruta, los nombres de columnas y si se ejecutaron las celdas anteriores.
5. Nunca sustituyas resultados por números escritos a mano: el pipeline debe recalcularse desde el Excel.

## Glosario fundamental

- **DataFrame:** tabla de pandas con filas y columnas; **Series:** una columna o vector de datos.
- **Variable:** nombre que guarda un valor; **función:** bloque reutilizable de instrucciones; **argumento:** dato enviado a una función; **método:** función asociada a un objeto, como `.head()`.
- **Lista `[]`:** secuencia de elementos; **diccionario `{}`:** asociaciones clave–valor; **tupla `()`:** agrupación ordenada.
- **`for`:** repite instrucciones para cada elemento; **`if`:** ejecuta condicionalmente; **`def`:** declara una función; **`return`:** devuelve un resultado (las funciones `registrar` y `normalizar_columna` tienen comportamientos distintos: la primera modifica una lista; la segunda devuelve un texto).
- **`=` vs `==`:** asignación frente a comparación; **`&` y `|`:** Y y O para condiciones booleanas de pandas; **`~`:** negación booleana.
- **`NaN` / `pd.NA`:** valor ausente; no equivale al número cero ni a la cadena `Sin dato`.
- **`.copy()`:** copia una tabla para transformarla sin depender de vistas; **`.loc[]`:** selecciona filas y columnas por etiquetas/condiciones.
- **`groupby()`:** agrupa filas; **`agg()`:** calcula estadísticas; **`reset_index()`:** vuelve a convertir las claves de grupo en columnas.
- **`size` vs `sum`:** cantidad de anuncios frente a suma de vacantes; **`mean` vs `median`:** promedio frente a valor central ordenado.
- **`dropna=False`:** conserva los grupos con nulos; **`errors='coerce'`:** reemplaza conversiones imposibles por valores ausentes; **`observed=True`:** incluye categorías observadas en agrupaciones categóricas.
- **`index=False`:** no exporta la numeración de filas como columna adicional; **`encoding='utf-8-sig'`:** CSV compatible con muchos lectores de Excel.

## Recorrido celda por celda

### Celda 1 · Explicación

**Qué presenta el notebook:** # **Análisis de ofertas de empleo de Konzerta** **Curso:** Introducción a la Programación para Ciencia de Datos **Integrantes:** Francia Vergara, Luis Santimateo y Yenia Rojas **Fuente:** Konzerta **Archivo utilizado:** Konzerta 08-oct-2026.xlsx **Fecha de obtención del archivo:** 16-oct-2026 ###**Contexto del proyecto** En este proyecto buscamos conocer las características de las oportunidades de empleo incluidas en el archivo de Konzerta. Nos interesa identificar qué áreas profesionales concentran más anuncios y vacantes, dónde se ubican las oportunidades y qué modalidades de trabajo ofrecen. También exploraremos la información salarial, su relación con la experiencia solicitada y la cantidad de anuncios publicados por semana. Para interpretar estos resultados, tendremos en cuenta los datos faltantes y los valores que requieren revisión. ###**Objetivo del análisis** Analizar las ofertas de empleo de Konzerta mediante la re

### Celda 2 · Código

**Objetivo y explicación de las funciones:** Detecta Colab con `sys.modules`; `Path.cwd()` toma la carpeta actual y `resolve()` su ruta absoluta. `next(..., None)` busca la raíz del proyecto entre la carpeta y sus antecesoras. `is_dir()` verifica directorios; `raise FileNotFoundError` explica un error de ubicación. El operador `/` de `Path` une carpetas de forma compatible con Windows y Mac. `mkdir(parents=True, exist_ok=True)` crea carpetas anidadas sin fallar si existen; `touch(exist_ok=True)` crea archivos vacíos si faltan. **Precaución:** si README o requirements no existen, `touch` crea archivos vacíos, no su contenido.

**Código original de la celda:**

```python
# CONFIGURACIÓN DEL ENTORNO
# Compatible con Google Colab, Windows y macOS

from pathlib import Path
import sys

EN_COLAB = "google.colab" in sys.modules

if EN_COLAB:
    from google.colab import drive
    drive.mount("/content/drive")
    PROYECTO = Path("/content/drive/MyDrive/Proyecto_Konzerta")
else:
    actual = Path.cwd().resolve()

    PROYECTO = next(
        (
            ruta for ruta in [actual, *actual.parents]
            if ruta.name == "Proyecto_Konzerta"
        ),
        None
    )

    if PROYECTO is None:
        candidato = actual / "Proyecto_Konzerta"
        if candidato.is_dir():
            PROYECTO = candidato
        else:
            raise FileNotFoundError(
                "Abre JupyterLab desde Proyecto_Konzerta."
            )

BRONCE = PROYECTO / "datos" / "bronce"
PLATA = PROYECTO / "datos" / "plata"
ORO = PROYECTO / "datos" / "oro"
NOTEBOOKS = PROYECTO / "notebooks"
DASHBOARD = PROYECTO / "dashboard"

for carpeta in [BRONCE, PLATA, ORO, NOTEBOOKS, DASHBOARD]:
    carpeta.mkdir(parents=True, exist_ok=True)

(PROYECTO / "README.md").touch(exist_ok=True)
(PROYECTO / "requirements.txt").touch(exist_ok=True)

print("Entorno:", "Google Colab" if EN_COLAB else "Local")
print("Proyecto:", PROYECTO)
print("Configuración completada correctamente.")
```

### Celda 3 · Explicación

**Qué presenta el notebook:** # **Lectura y revisión inicial de los datos** Leemos el archivo de Konzerta y conservamos una tabla original como referencia. Después creamos una copia para trabajar y comparar los cambios realizados durante la limpieza. Cada fila representa un anuncio de empleo. Revisamos el tamaño del archivo, sus primeros registros y los tipos de datos para conocer su estructura antes de comenzar la limpieza.

### Celda 4 · Código

**Objetivo y explicación de las funciones:** `pd.read_excel()` carga el archivo original en un DataFrame. `is_file()` comprueba que existe. `copy()` evita transformar la referencia de lectura. `shape[0]` y `shape[1]` son filas y columnas. `head(3)` muestra tres anuncios; `display()` representa una tabla en Jupyter; `info()` enseña tipos y no nulos.

**Código original de la celda:**

```python
# CAPA BRONCE: LECTURA DEL ARCHIVO ORIGINAL

import pandas as pd

archivo_excel = BRONCE / "Konzerta 08-oct-2026.xlsx"

if not archivo_excel.is_file():
    raise FileNotFoundError(
        f"No se encontró el archivo: {archivo_excel}"
    )

crudos = pd.read_excel(archivo_excel)
konzerta = crudos.copy()

print(f"Total de anuncios: {crudos.shape[0]:,}")
print(f"Total de columnas: {crudos.shape[1]}")

display(
    konzerta[
        ["id", "titulo", "area", "provincia", "modalidad"]
    ].head(3)
)

konzerta.info()
```

### Celda 5 · Explicación

**Qué presenta el notebook:** ## **Revisión de valores faltantes** Revisamos cuántos datos faltan en cada columna y qué porcentaje representan sobre el total de anuncios. Esto nos ayuda a reconocer las limitaciones de la información y a decidir cómo tratarla durante la limpieza. Las decisiones sobre estos faltantes se documentan en la bitácora para explicar qué hicimos y por qué.

### Celda 6 · Código

**Objetivo y explicación de las funciones:** `len()` cuenta filas. `isna()` detecta nulos y `sum()` los cuenta por columna. La división por el total y `*100` produce porcentajes; `round(2)` redondea solo para presentación. `pd.DataFrame()` construye el resumen y `sort_values(ascending=False)` ordena los mayores faltantes primero.

**Código original de la celda:**

```python
# Medimos los faltantes sobre la tabla original, antes de la limpieza
total_anuncios = len(crudos)
faltantes_por_columnas = crudos.isna().sum()

porcentaje_por_columna = (faltantes_por_columnas / total_anuncios * 100).round(2)

# Reunimos cantidades y porcentajes en una sola tabla
resumen_faltante = pd.DataFrame({"cantidad_faltante": faltantes_por_columnas, "porcentaje_faltante": porcentaje_por_columna}).sort_values(by="cantidad_faltante", ascending=False)
display(resumen_faltante)
```

### Celda 7 · Explicación

**Qué presenta el notebook:** # **Revisión de duplicados** Comprobamos si hay filas completamente iguales y si algún identificador de anuncio aparece más de una vez. Estas repeticiones podrían alterar los conteos de ofertas y vacantes. Revisamos ambas situaciones porque un anuncio puede conservar el mismo identificador y tener diferencias en otros campos. Las decisiones sobre su tratamiento se documentan en la bitácora de limpieza.

### Celda 8 · Código

**Objetivo y explicación de las funciones:** `duplicated()` devuelve un booleano por fila; `sum()` cuenta los verdaderos. Aplicado a `crudos` compara todas las columnas; aplicado a `crudos['id']` identifica identificadores repetidos. Son verificaciones distintas.

**Código original de la celda:**

```python
# Buscamos repeticiones en los datos originales
duplicados_completos = crudos.duplicated().sum()
duplicados_id = crudos["id"].duplicated().sum()

print("Filas completamente duplicadas:", duplicados_completos)
print("Repeticiones de id:", duplicados_id)
```

### Celda 9 · Explicación

**Qué presenta el notebook:** **No se encontraron filas completamente duplicadas ni identificadores repetidos en los datos originales. Por este motivo, no es necesario eliminar anuncios por duplicación.**

### Celda 10 · Explicación

**Qué presenta el notebook:** # **Revisión de valores numéricos** Revisamos las vacantes, los salarios, las edades y la experiencia para conocer sus valores habituales e identificar cifras que necesitan validación. Primero consultamos las estadísticas de cada variable, como el promedio, la mediana y los valores mínimos y máximos. Después observamos los cinco anuncios con mayores salarios máximos registrados. Esta revisión sirve para orientar la limpieza. Un valor extremo requiere evaluación antes de decidir su tratamiento. Además, la moneda de los importes salariales sigue pendiente de confirmar, lo que limita su comparación entre anuncios.

### Celda 11 · Código

**Objetivo y explicación de las funciones:** Una lista de nombres selecciona columnas. `describe()` calcula recuento, media, desviación, percentiles y extremos; `.T` transpone la tabla. `round(2)` facilita lectura; `sort_values('salario_max',ascending=False).head(5)` muestra los cinco salarios máximos más altos, sin afirmar que sean válidos.

**Código original de la celda:**

```python
# Seleccionamos las variables numéricas relevantes para el análisis
columnas_numericas = ["vacantes", "salario_min", "salario_max", "edad_min", "edad_max", "experiencia_meses"]
resumen_numerico = crudos[columnas_numericas].describe().T

# Redondeamos la presentación para facilitar la lectura
display(resumen_numerico.round(2))

# Revisamos los anuncios con mayores importes salariales registrados
columnas_salario = ["id", "titulo", "salario_min", "salario_max", "salario_frecuencia", "salario_tipo"]

display(crudos[columnas_salario].sort_values(by="salario_max", ascending=False).head(5))
```

### Celda 12 · Explicación

**Qué presenta el notebook:** # **Limpieza de datos** Aplicamos los ajustes identificados durante la revisión inicial. Cada ejecución comienza con una nueva copia de los datos originales para que podamos repetir el proceso y comparar los cambios. Primero quitamos los espacios sobrantes en los nombres de empresa y convertimos la fecha de extracción a un formato de fecha y hora. Guardamos el perfil inicial de los datos y registramos cada decisión en la bitácora de limpieza.

### Celda 13 · Código

**Objetivo y explicación de las funciones:** `copy(deep=True)` reinicia la limpieza desde el original. `dtypes.astype(str)` describe tipos. `registrar(...)` es una función creada por el equipo: añade un diccionario a `registros_bitacora` usando `append()`, y `int()` transforma la cantidad a entero. `normalizar_columna(nombre)` convierte a texto, usa `unicodedata.normalize('NFKD')` para separar acentos, `unicodedata.combining()` para descartar marcas, `re.sub()` para convertir grupos de caracteres no alfanuméricos en `_`, `strip('_')` para quitar guiones de extremos y `lower()` para minúsculas. `tolist()` guarda nombres previos y `zip()` empareja nombres anteriores y nuevos para contar cambios. `select_dtypes(include=['object','string'])` selecciona columnas textuales. `continue` omite `descripcion` y `url`. `astype('string')` convierte al tipo texto de pandas; `.str.strip()` quita espacios laterales; `.str.replace(r'\s+',' ',regex=True)` compacta espacios; `.replace('',pd.NA)` marca vacíos; `fillna('')`, `ne()` y `sum()` cuentan cambios. `pd.to_datetime(...,errors='coerce')` y `pd.to_numeric(...,errors='coerce')` convierten fechas/números, dejando nulos cuando no se pueden interpretar. `notna()` permite medir cuántos valores originalmente presentes se perdieron en la conversión.

**Código original de la celda:**

```python
# CAPA PLATA: NORMALIZACIÓN DE DATOS

import re
import unicodedata

konzerta = crudos.copy(deep=True)

perfil_antes = pd.DataFrame({
    "tipo": konzerta.dtypes.astype(str),
    "faltantes": konzerta.isna().sum()
})

registros_bitacora = []

def registrar(columna, problema, decision, filas_afectadas):
    registros_bitacora.append({
        "columna": columna,
        "problema": problema,
        "decision": decision,
        "filas_afectadas": int(filas_afectadas)
    })

# Normalizar nombres de columnas
def normalizar_columna(nombre):
    nombre = unicodedata.normalize("NFKD", str(nombre))
    nombre = "".join(
        c for c in nombre
        if not unicodedata.combining(c)
    )
    nombre = re.sub(r"[^a-zA-Z0-9]+", "_", nombre)
    return nombre.strip("_").lower()

nombres_anteriores = konzerta.columns.tolist()
konzerta.columns = [
    normalizar_columna(c) for c in konzerta.columns
]

registrar(
    "nombres_columnas",
    "Posibles nombres sin formato uniforme",
    "Normalizar a snake_case",
    sum(a != b for a, b in zip(
        nombres_anteriores, konzerta.columns
    ))
)

# Limpiar columnas de texto
columnas_texto = konzerta.select_dtypes(
    include=["object", "string"]
).columns

for columna in columnas_texto:
    if columna in ["descripcion", "url"]:
        continue

    original = konzerta[columna].astype("string")

    limpio = (
        original.str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .replace("", pd.NA)
    )

    cambios = original.fillna("").ne(
        limpio.fillna("")
    ).sum()

    konzerta[columna] = limpio

    if cambios > 0:
        registrar(
            columna,
            "Espacios sobrantes o textos vacíos",
            "Normalizar espacios y convertir vacíos a nulos",
            cambios
        )

# Convertir fechas
for columna in [
    "fecha_publicacion",
    "fecha_finalizacion",
    "extraido"
]:
    if columna in konzerta.columns:
        antes = konzerta[columna].notna()

        konzerta[columna] = pd.to_datetime(
            konzerta[columna],
            errors="coerce"
        )

        registrar(
            columna,
            "Fechas no interpretables",
            "Convertir a datetime",
            (antes & konzerta[columna].isna()).sum()
        )

# Convertir números
for columna in [
    "vacantes", "salario_min", "salario_max",
    "edad_min", "edad_max", "experiencia_meses"
]:
    if columna in konzerta.columns:
        antes = konzerta[columna].notna()

        konzerta[columna] = pd.to_numeric(
            konzerta[columna],
            errors="coerce"
        )

        registrar(
            columna,
            "Valores numéricos no interpretables",
            "Convertir a tipo numérico",
            (antes & konzerta[columna].isna()).sum()
        )

print("Normalización completada.")
print("Filas:", len(konzerta))
print("Columnas:", len(konzerta.columns))
```

### Celda 14 · Explicación

**Qué presenta el notebook:** # **Tratamiento de faltantes y revisión de salarios** En las categorías que utilizaremos para agrupar los anuncios, representamos la información ausente con la etiqueta “Sin dato”. Los faltantes numéricos se conservan como valores ausentes. Para los salarios, aplicamos reglas que permiten identificar importes que requieren revisión. También utilizamos el rango intercuartílico (IQR), que mide la dispersión de la mitad central de los salarios máximos registrados. **Clasificamos los anuncios en tres grupos:** **Sin dato:** no tienen salario mínimo ni máximo registrado. **Registro sin alerta:** tienen algún importe registrado y no activan las reglas aplicadas. **Revisar:** presentan algún importe o rango que necesita validación. Los importes se conservan. Estas categorías reflejan las comprobaciones realizadas; la moneda sigue pendiente de confirmar.

### Celda 15 · Código

**Objetivo y explicación de las funciones:** `fillna('Sin dato')` conserva los anuncios sin categoría. `drop_duplicates().copy()` elimina filas idénticas, no todos los ID repetidos. `quantile(.25)` y `quantile(.75)` calculan Q1 y Q3; `iqr=Q3-Q1` mide el rango intercuartílico y los límites `Q1-1.5*IQR`, `Q3+1.5*IQR` sirven para señalar extremos. Los operadores `|` significan O y `&` significan Y sobre series booleanas; cada condición va entre paréntesis. `loc[filtro,columna]` asigna la clasificación `Sin dato`, `Registro sin alerta` o `Revisar`. `value_counts()` resume las categorías. **Importante:** el indicador `Revisar` no confirma que el salario sea erróneo; tampoco corrige monedas o periodicidades.

**Código original de la celda:**

```python
# CAPA PLATA: FALTANTES, DUPLICADOS Y SALARIOS

categorias = [
    "area", "subarea", "provincia",
    "localidad", "nivel_laboral", "modalidad"
]

for columna in categorias:
    faltantes = int(konzerta[columna].isna().sum())

    konzerta[columna] = (
        konzerta[columna]
        .astype("string")
        .fillna("Sin dato")
    )

    registrar(
        columna,
        "Valores faltantes en categorías",
        "Reemplazar nulos por Sin dato",
        faltantes
    )

# Eliminar duplicados completos
duplicados_eliminados = int(konzerta.duplicated().sum())

konzerta = konzerta.drop_duplicates().copy()

registrar(
    "todas_las_columnas",
    "Filas completamente duplicadas",
    "Eliminar registros idénticos",
    duplicados_eliminados
)

# Revisar valores salariales mediante IQR
q1 = konzerta["salario_max"].quantile(0.25)
q3 = konzerta["salario_max"].quantile(0.75)
iqr = q3 - q1

limite_inferior = q1 - 1.5 * iqr
limite_superior = q3 + 1.5 * iqr

alerta_salario = (
    (konzerta["salario_min"] <= 1)
    | (konzerta["salario_max"] <= 0)
    | (konzerta["salario_min"] > konzerta["salario_max"])
    | (konzerta["salario_max"] < limite_inferior)
    | (konzerta["salario_max"] > limite_superior)
)

con_salario = (
    konzerta["salario_min"].notna()
    | konzerta["salario_max"].notna()
)

konzerta["estado_salario"] = "Sin dato"

konzerta.loc[
    con_salario, "estado_salario"
] = "Registro sin alerta"

konzerta.loc[
    con_salario & alerta_salario, "estado_salario"
] = "Revisar"

cantidad_alertas = int(
    (konzerta["estado_salario"] == "Revisar").sum()
)

registrar(
    "estado_salario",
    "Importes inconsistentes o extremos",
    "Conservar salarios y marcar para revisión",
    cantidad_alertas
)

print("Duplicados eliminados:", duplicados_eliminados)
print("Alertas salariales:", cantidad_alertas)

display(konzerta["estado_salario"].value_counts())
```

### Celda 16 · Código

**Objetivo y explicación de las funciones:** El bucle revisa cada columna; `continue` excluye `estado_salario` de la bitácora adicional. `pd.DataFrame(registros_bitacora,columns=[...])` establece las cuatro columnas. `eq('Sin dato')` compara con esa etiqueta y `sum()` cuenta coincidencias. Se imprimen registros y perfiles para demostrar las decisiones de limpieza.

**Código original de la celda:**

```python
# CAPA PLATA: BITÁCORA Y PERFIL DE CALIDAD

for columna in konzerta.columns:

    if columna == "estado_salario":
        continue

    cantidad = int(konzerta[columna].isna().sum())

    if cantidad > 0:
        registrar(
            columna,
            "Valores faltantes después de la limpieza",
            "Conservar los nulos sin inventar información",
            cantidad
        )

bitacora = pd.DataFrame(
    registros_bitacora,
    columns=[
        "columna",
        "problema",
        "decision",
        "filas_afectadas"
    ]
)

perfil_despues = pd.DataFrame({
    "tipo": konzerta.dtypes.astype(str),
    "faltantes": konzerta.isna().sum(),
    "sin_dato": konzerta.eq("Sin dato").sum()
})

print("Registros originales:", len(crudos))
print("Registros limpios:", len(konzerta))
print("Duplicados eliminados:", duplicados_eliminados)

print("\nBITÁCORA DE LIMPIEZA")
display(bitacora)

print("\nPERFIL DE CALIDAD")
display(perfil_despues)
```

### Celda 17 · Explicación

**Qué presenta el notebook:** # **Verificación de la limpieza** Comparamos la cantidad de filas y columnas, los tipos de datos y los valores faltantes antes y después de la limpieza. La columna sin_dato cuenta las etiquetas que representan información ausente. Esto permite distinguirlas de los valores nulos que conservamos. Finalmente, presentamos la bitácora completa para explicar qué cambios realizamos y cuál fue su justificación.

### Celda 18 · Código

**Objetivo y explicación de las funciones:** `pd.DataFrame(...,index=['Antes','Después'])` compara dimensiones. `join(how='outer',lsuffix=...,rsuffix=...)` combina perfiles, incluso columnas nuevas. Una comprensión de lista detecta columnas esenciales ausentes y `raise ValueError` detiene el flujo si faltan. `duplicated().sum()` confirma si quedaron filas idénticas.

**Código original de la celda:**

```python
# CAPA PLATA: VERIFICACIÓN FINAL

comparacion_dimensiones = pd.DataFrame({
    "filas": [crudos.shape[0], konzerta.shape[0]],
    "columnas": [crudos.shape[1], konzerta.shape[1]]
}, index=["Antes", "Después"])

display(comparacion_dimensiones)

comparacion_perfiles = perfil_antes.join(
    perfil_despues,
    how="outer",
    lsuffix="_antes",
    rsuffix="_despues"
)

display(comparacion_perfiles)

duplicados_restantes = int(konzerta.duplicated().sum())

columnas_esenciales = [
    "id", "titulo", "area", "subarea",
    "provincia", "modalidad",
    "fecha_publicacion", "vacantes"
]

faltan_columnas = [
    c for c in columnas_esenciales
    if c not in konzerta.columns
]

if faltan_columnas:
    raise ValueError(
        f"Faltan columnas esenciales: {faltan_columnas}"
    )

print("Duplicados restantes:", duplicados_restantes)
print("Columnas esenciales verificadas.")
print("Registros procesados:", len(konzerta))
print("Registros de bitácora:", len(bitacora))
```

### Celda 19 · Código

**Objetivo y explicación de las funciones:** `to_csv()` exporta datos. `index=False` evita una columna de índice extra; `encoding='utf-8-sig'` facilita lectura con Excel; `glob('*.csv')` encuentra los CSV y `sorted()` los lista ordenados. Los perfiles conservan índice porque identifica la columna de origen.

**Código original de la celda:**

```python
# CAPA PLATA: EXPORTAR RESULTADOS

PLATA.mkdir(parents=True, exist_ok=True)

konzerta.to_csv(
    PLATA / "konzerta_limpio.csv",
    index=False,
    encoding="utf-8-sig"
)

bitacora.to_csv(
    PLATA / "bitacora_limpieza.csv",
    index=False,
    encoding="utf-8-sig"
)

perfil_antes.to_csv(
    PLATA / "perfil_bronce.csv",
    encoding="utf-8-sig"
)

perfil_despues.to_csv(
    PLATA / "perfil_plata.csv",
    encoding="utf-8-sig"
)

print("Archivos de la capa plata generados:")

for archivo in sorted(PLATA.glob("*.csv")):
    print(archivo.name)
```

### Celda 20 · Explicación

**Qué presenta el notebook:** El proceso estandariza los espacios en los nombres de empresa, convierte la fecha de extracción y añade una clasificación de la información salarial. En las categorías seleccionadas, la etiqueta “Sin dato” permite incluir los anuncios con información incompleta. Los faltantes numéricos se conservan como valores ausentes. En estado_salario, los campos del perfil anterior aparecen como NaN porque esa columna se creó durante la limpieza. Los importes marcados como “Revisar” mantienen sus valores originales. Su clasificación indica que requieren validación antes de interpretar las diferencias salariales

### Celda 21 · Explicación

**Qué presenta el notebook:** **Fuente:** [Konzerta](https://www.konzerta.com/)

### Celda 22 · Explicación

**Qué presenta el notebook:** # **Diccionario de datos** Este diccionario explica las columnas que utilizaremos en el análisis. Los tipos de datos corresponden a la tabla después de la limpieza. Incluimos las 31 columnas originales y estado_salario, que creamos para distinguir la disponibilidad de importes salariales y los casos que requieren revisión.

### Celda 23 · Código

**Objetivo y explicación de las funciones:** El diccionario `descripciones` relaciona nombres de columnas con su significado. `konzerta.columns` y `dtypes.astype(str)` extraen nombres y tipos reales; `.map(descripciones)` asigna una descripción a cada columna; `style.set_properties()` cambia únicamente su presentación en Jupyter.

**Código original de la celda:**

```python
# Explicamos el significado de cada columna
descripciones = {"id": "Identificador del anuncio de empleo.",
    "titulo": "Nombre del puesto publicado.",
    "empresa": "Nombre de la empresa anunciante, cuando se informa.",
    "empresa_confidencial": "Indica si la empresa se presenta como confidencial.",
    "industria": "Sector de actividad registrado para la empresa.",
    "empresa_tamano": "Categoría de tamaño de la empresa.",
    "fecha_publicacion": "Fecha de publicación del anuncio.",
    "fecha_finalizacion": "Fecha de finalización indicada para el anuncio.",
    "provincia": "Provincia registrada para la oferta.",
    "localidad": "Localidad registrada para la oferta.",
    "area": "Área profesional a la que pertenece el anuncio.",
    "subarea": "Subárea o especialidad profesional del anuncio.",
    "nivel_laboral": "Nivel o jerarquía del puesto.",
    "tipo_trabajo": "Clasificación del trabajo, como Full-time o Part-time.",
    "modalidad": "Forma de trabajo: presencial, híbrida o remota.",
    "contratacion": "Tipo de contratación, como indeterminado o temporal.",
    "vacantes": "Cantidad de puestos ofrecidos en el anuncio.",
    "salario_min": "Importe salarial mínimo registrado; moneda sin confirmar.",
    "salario_max": "Importe salarial máximo registrado; moneda sin confirmar.",
    "salario_frecuencia": "Periodicidad del salario registrado, por ejemplo mensual.",
    "salario_tipo": "Tipo de importe salarial registrado, por ejemplo bruto.",
    "edad_min": "Edad mínima solicitada, en años.",
    "edad_max": "Edad máxima solicitada, en años.",
    "experiencia_meses": "Experiencia requerida registrada en meses.",
    "educacion": "Nivel educativo solicitado.",
    "educacion_estado": "Situación de los estudios, como graduado o en curso.",
    "idiomas": "Idiomas y niveles de dominio indicados en el anuncio.",
    "apto_discapacidad": "Indica si el anuncio señala que es apto para personas con discapacidad.",
    "descripcion": "Texto del anuncio con información del puesto y sus requisitos.",
    "url": "Enlace al anuncio original.",
    "extraido": "Fecha y hora de extracción registradas en el dataset.",
    "estado_salario": "Clasificación creada en la limpieza según disponibilidad de importes y alertas."}

# Obtenemos los tipos directamente de la tabla limpia
diccionario_datos = pd.DataFrame({"columna": konzerta.columns,"tipo": list(konzerta.dtypes.astype(str))})

diccionario_datos["descripcion"] = (diccionario_datos["columna"].map(descripciones))

display(diccionario_datos.style.set_properties(**{"text-align": "left"}).set_table_styles([
        {"selector": "th", "props": [("text-align", "left")]}]))
```

### Celda 24 · Explicación

**Qué presenta el notebook:** # **Análisis exploratorio de datos** ###**Pregunta 1. Áreas y subáreas con mayor demanda** ¿Qué áreas y subáreas profesionales presentan mayor demanda según las ofertas y vacantes publicadas? Comenzamos agrupando los anuncios por área profesional. Contaremos las ofertas y sumaremos las vacantes registradas. Una oferta corresponde a un anuncio; las vacantes representan los puestos que ese anuncio ofrece. Esta diferencia permite observar tanto la cantidad de publicaciones como los puestos anunciados.

### Celda 25 · Código

**Objetivo y explicación de las funciones:** Esta celda establece el contexto para el análisis exploratorio (EDA); revisa sus comentarios y las tablas presentadas. El EDA busca frecuencias, distribuciones y relaciones sin inferir causalidad.

**Código original de la celda:**

```python
# Contamos los anuncios y sumamos sus vacantes por área profesional
tabla_areas = (konzerta.groupby("area", dropna=False).agg(ofertas=("id", "size"),vacantes=("vacantes", "sum")).reset_index().sort_values(by="ofertas", ascending=False))

# Calculamos la participación de cada área en el total de anuncios
tabla_areas["porcentaje_ofertas"] = (tabla_areas["ofertas"] / len(konzerta) * 100).round(2)

display(tabla_areas)
```

### Celda 26 · Código

**Objetivo y explicación de las funciones:** Esta celda forma parte del análisis exploratorio. Lee sus comentarios, identifica las variables de entrada y comprueba la tabla o gráfico generado; las operaciones detalladas se describen en el glosario y en las celdas contiguas.

**Código original de la celda:**

```python
import plotly.express as px

# Seleccionamos las diez áreas con más anuncios
top_areas = tabla_areas.head(10).sort_values(by="ofertas")

fig = px.bar(top_areas, x="ofertas", y="area", orientation="h", text="ofertas", title="Las 10 áreas con más ofertas en el dataset de Konzerta",
    labels={"ofertas": "Número de ofertas (anuncios)" ,"area": "Área profesional"})

fig.update_layout(height=650)
fig.show()
```

### Celda 27 · Explicación

**Qué presenta el notebook:** Comercial, Ventas y Negocios encabezan las publicaciones del dataset con 801 anuncios, equivalentes al 26.60 % del total. Aunque Administración tiene más anuncios (446) que Atención al Cliente (146), esta última reúne más vacantes (1,608 frente a 625), lo que refleja una mayor cantidad de puestos por anuncio en promedio.

### Celda 28 · Explicación

**Qué presenta el notebook:** ### **Análisis de subáreas profesionales con mayor demanda** Dentro de las áreas identificadas, existen subáreas o especialidades específicas. Vamos a agrupar los datos por `area` y `subarea` para analizar cuáles son las disciplinas específicas más solicitadas en la plataforma de Konzerta.

### Celda 29 · Código

**Objetivo y explicación de las funciones:** Se calculan porcentajes y rankings para interpretar el peso de las áreas; el denominador es el número de anuncios de la tabla, no todas las ofertas del país.

**Código original de la celda:**

```python
# Agrupamos por área y subárea para contar ofertas y sumar vacantes
tabla_subareas = (
    konzerta.groupby(["area", "subarea"], dropna=False)
    .agg(ofertas=("id", "size"), vacantes=("vacantes", "sum"))
    .reset_index()
    .sort_values(by="ofertas", ascending=False)
)

# Calculamos la participación porcentual de cada subárea sobre el total general
tabla_subareas["porcentaje_ofertas"] = (tabla_subareas["ofertas"] / len(konzerta) * 100).round(2)

# Mostramos las 15 subáreas con mayor número de ofertas
display(tabla_subareas.head(15))
```

### Celda 30 · Explicación

**Qué presenta el notebook:** ### **Visualización de las subáreas más demandadas** Para facilitar la comprensión visual de las especialidades más buscadas, creamos un gráfico de barras horizontales con las 10 subáreas que concentran más ofertas en el dataset.

### Celda 31 · Código

**Objetivo y explicación de las funciones:** `px.bar()` crea barras interactivas; `x`, `y` y `color` asignan variables. `orientation='h'` muestra barras horizontales; `title` y `labels` describen el gráfico. `color_discrete_sequence` fija una paleta. `update_layout()` ajusta alto y leyenda; `show()` lo presenta en el notebook.

**Código original de la celda:**

```python
# Seleccionamos las diez subáreas líderes
top_subareas = tabla_subareas.head(10).sort_values(by="ofertas")

fig_sub = px.bar(
    top_subareas,
    x="ofertas",
    y="subarea",
    orientation="h",
    text="ofertas",
    title="Las 10 subáreas profesionales con más ofertas en Konzerta",
    labels={"ofertas": "Número de ofertas (anuncios)", "subarea": "Subárea o especialidad"},
    color="area",
    color_discrete_sequence=px.colors.qualitative.Safe
)

fig_sub.update_layout(height=600, legend_title_text="Área Principal")
fig_sub.show()
```

### Celda 32 · Explicación

**Qué presenta el notebook:** ### **Pregunta 2. Salarios según experiencia requerida y nivel laboral** ¿Cómo varían los salarios ofrecidos según la experiencia solicitada? Se seleccionan anuncios con salarios sin alertas y experiencia informada; se calculan medianas y promedios por rangos de meses. El nivel laboral se estudia como dimensión complementaria. **Limitación:** en la última ejecución registrada había 414 ofertas con salario máximo sin alerta, pero solo **10** con salario y experiencia informada. La muestra combinada es muy pequeña y no permite generalizar una relación salarial al mercado laboral. La moneda y periodicidad de los importes no están confirmadas.

### Celda 33 · Código

**Objetivo y explicación de las funciones:** Se filtran salarios con `estado_salario == 'Registro sin alerta'`, `notna()` y `>0`. El operador `&` combina requisitos. `pd.cut()` agrupa meses de experiencia en intervalos definidos por `bins` y `labels`. `groupby(observed=True)` trabaja con categorías efectivamente presentes. `agg()` calcula `size`, `mean`, `median`, `min` y `max`; `reset_index()` normaliza la tabla; `sort_values()` ordena por mediana. `round(2)` solo formatea la visualización. La muestra conjunta es pequeña y debe informarse.

**Código original de la celda:**

```python
# ==========================================================
# SALARIOS Y EXPERIENCIA REQUERIDA
# ==========================================================

# 1. Seleccionar anuncios sin alertas salariales
salarios_validos = konzerta[
    (konzerta["estado_salario"] == "Registro sin alerta")
    & (konzerta["salario_max"].notna())
    & (konzerta["salario_max"] > 0)
].copy()

# 2. Seleccionar registros con experiencia válida
salarios_experiencia = salarios_validos[
    (salarios_validos["experiencia_meses"].notna())
    & (salarios_validos["experiencia_meses"] >= 0)
].copy()

# 3. Crear rangos de experiencia
salarios_experiencia["rango_experiencia"] = pd.cut(
    salarios_experiencia["experiencia_meses"],
    bins=[-0.01, 12, 36, 60, float("inf")],
    labels=[
        "0 a 12 meses",
        "13 a 36 meses",
        "37 a 60 meses",
        "Más de 60 meses"
    ]
)

# 4. Calcular estadísticas salariales por experiencia
resumen_salarios_experiencia = (
    salarios_experiencia
    .groupby(
        "rango_experiencia",
        observed=True
    )
    .agg(
        ofertas=("id", "size"),
        salario_max_promedio=("salario_max", "mean"),
        salario_max_mediana=("salario_max", "median"),
        salario_max_minimo=("salario_max", "min"),
        salario_max_maximo=("salario_max", "max")
    )
    .reset_index()
)

# 5. Mantener el análisis complementario por nivel laboral
resumen_salarios_nivel = (
    salarios_validos
    .groupby("nivel_laboral", dropna=False)
    .agg(
        ofertas=("id", "size"),
        salario_min_promedio=("salario_min", "mean"),
        salario_max_promedio=("salario_max", "mean"),
        salario_max_mediana=("salario_max", "median")
    )
    .reset_index()
    .sort_values(
        by="salario_max_mediana",
        ascending=False
    )
)

# 6. Mostrar resultados
print("PREGUNTA 2: SALARIOS SEGÚN EXPERIENCIA")
print("Ofertas con salario máximo:", len(salarios_validos))
print("Ofertas con salario y experiencia:", len(salarios_experiencia))

print("\nSALARIOS POR RANGO DE EXPERIENCIA")
display(resumen_salarios_experiencia.round(2))

print("\nSALARIOS POR NIVEL LABORAL")
display(resumen_salarios_nivel.round(2))
```

### Celda 34 · Explicación

**Qué presenta el notebook:** ### **Visualizaciones salariales: experiencia y nivel laboral** El gráfico de barras compara la mediana del salario máximo entre rangos de experiencia; el diagrama de cajas permite examinar la dispersión salarial por nivel laboral. Los resultados son descriptivos y deben interpretarse con cautela debido a los pocos registros que informan simultáneamente salario y experiencia.

### Celda 35 · Código

**Objetivo y explicación de las funciones:** `if not ...empty` evita graficar tablas vacías. `px.bar()` compara medianas; `px.box()` muestra distribución y valores extremos por nivel. `update_traces(texttemplate=...,textposition=...)` controla etiquetas; `update_layout()` configura títulos y altura; `show()` representa el gráfico. Un gráfico de caja no prueba causalidad.

**Código original de la celda:**

```python
# ==========================================================
# VISUALIZACIONES SALARIALES
# ==========================================================

import plotly.express as px

# GRÁFICO 1: Salarios según experiencia requerida

if not resumen_salarios_experiencia.empty:

    fig_experiencia = px.bar(
        resumen_salarios_experiencia,
        x="rango_experiencia",
        y="salario_max_mediana",
        text="salario_max_mediana",
        color="rango_experiencia",
        title="Mediana salarial según experiencia requerida",
        labels={
            "rango_experiencia": "Experiencia requerida",
            "salario_max_mediana": "Mediana del salario máximo"
        },
        color_discrete_sequence=px.colors.qualitative.Safe
    )

    fig_experiencia.update_traces(
        texttemplate="%{text:,.2f}",
        textposition="outside"
    )

    fig_experiencia.update_layout(
        height=500,
        showlegend=False,
        xaxis_title="Rango de experiencia",
        yaxis_title="Mediana del salario máximo"
    )

    fig_experiencia.show()

else:
    print("No hay datos suficientes para graficar salarios por experiencia.")


# GRÁFICO 2: Distribución salarial según nivel laboral

if not salarios_validos.empty:

    fig_salarios = px.box(
        salarios_validos,
        x="nivel_laboral",
        y="salario_max",
        color="nivel_laboral",
        title="Distribución de salarios máximos por nivel laboral",
        labels={
            "nivel_laboral": "Nivel laboral",
            "salario_max": "Salario máximo ofrecido"
        },
        color_discrete_sequence=px.colors.qualitative.Safe
    )

    fig_salarios.update_layout(
        height=600,
        showlegend=False,
        xaxis_title="Nivel laboral",
        yaxis_title="Salario máximo ofrecido"
    )

    fig_salarios.show()

else:
    print("No hay datos salariales suficientes para el gráfico.")
```

### Celda 36 · Explicación

**Qué presenta el notebook:** ### **Pregunta 3. Modalidades de trabajo por área profesional** ¿Qué modalidades de trabajo son más frecuentes y cómo cambian según el área? Primero, analizaremos la distribución general de la variable `modalidad` para observar cuál es la opción predominante en el mercado laboral capturado por Konzerta.

### Celda 37 · Código

**Objetivo y explicación de las funciones:** `value_counts()` cuenta cada modalidad. `reset_index()` convierte la serie de frecuencias en tabla. `rename(columns={'count':'ofertas'})` da un nombre significativo. Dividir entre `len(konzerta)` y multiplicar por 100 da porcentaje del archivo.

**Código original de la celda:**

```python
# Distribución general de modalidades de trabajo
dist_modalidad = (
    konzerta["modalidad"].value_counts()
    .reset_index()
    .rename(columns={"count": "ofertas"})
)
dist_modalidad["porcentaje"] = (dist_modalidad["ofertas"] / len(konzerta) * 100).round(2)

display(dist_modalidad)
```

### Celda 38 · Explicación

**Qué presenta el notebook:** ### **Relación entre la Modalidad y las 10 Áreas Principales** Para comprender si la modalidad varía según la disciplina o tipo de profesión, cruzaremos estas variables enfocándonos en las 10 áreas con más anuncios.

### Celda 39 · Código

**Objetivo y explicación de las funciones:** `sort_values().head(10)['area'].tolist()` obtiene las áreas líderes. `isin()` filtra anuncios cuya área está en esa lista. `pd.crosstab(fila,columna,normalize='index')` produce proporciones por fila; `*100` las convierte a porcentajes. `melt(id_vars='area',var_name='modalidad',value_name='porcentaje')` pasa de tabla ancha a larga, formato apropiado para Plotly. `reversed()` invierte el orden visual; `px.bar(...,barmode='stack')` apila modalidades hasta 100%; `hovertemplate` personaliza la información al pasar el cursor.

**Código original de la celda:**

```python
# ==========================================================
# MODALIDADES DE TRABAJO POR ÁREA
# ==========================================================

# 1. Seleccionar las diez áreas con más ofertas
top_10_areas_nombres = (
    tabla_areas
    .sort_values("ofertas", ascending=False)
    .head(10)["area"]
    .tolist()
)

konzerta_top_areas = konzerta[
    konzerta["area"].isin(top_10_areas_nombres)
].copy()

# 2. Calcular la distribución porcentual por área
tabla_cruzada = (
    pd.crosstab(
        konzerta_top_areas["area"],
        konzerta_top_areas["modalidad"],
        normalize="index"
    ) * 100
).round(2).reset_index()

# 3. Convertir la tabla a formato largo
tabla_cruzada_larga = tabla_cruzada.melt(
    id_vars="area",
    var_name="modalidad",
    value_name="porcentaje"
)

# 4. Ordenar las áreas por número de ofertas
orden_areas = list(reversed(top_10_areas_nombres))

# 5. Crear el gráfico interactivo
fig_mod_area = px.bar(
    tabla_cruzada_larga,
    x="porcentaje",
    y="area",
    color="modalidad",
    orientation="h",
    category_orders={"area": orden_areas},
    title="Modalidades de trabajo en las 10 áreas con más ofertas",
    labels={
        "porcentaje": "Porcentaje de ofertas (%)",
        "area": "Área profesional",
        "modalidad": "Modalidad de trabajo"
    },
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig_mod_area.update_layout(
    height=650,
    barmode="stack",
    xaxis_range=[0, 100],
    legend_title_text="Modalidad"
)

fig_mod_area.update_traces(
    hovertemplate="%{y}: %{x:.2f}%<extra>%{fullData.name}</extra>"
)

fig_mod_area.show()

print("DISTRIBUCIÓN PORCENTUAL POR ÁREA")
display(tabla_cruzada)
```

### Celda 40 · Explicación

**Qué presenta el notebook:** ### **Pregunta 4. Distribución por provincia, área profesional y nivel laboral** ¿Cómo se distribuyen las oportunidades según ubicación, área y nivel laboral? Se calculan anuncios y porcentajes por provincia, cruces de provincia con área y con nivel laboral, y una tabla conjunta. Se comparan las cinco provincias con más anuncios; los resultados describen únicamente la muestra de Konzerta.

### Celda 41 · Código

**Objetivo y explicación de las funciones:** `value_counts()` muestra etiquetas geográficas. `loc[...]` filtra las filas cuyo texto de provincia, tras `str.strip().str.lower()`, es `otra`; `head(20)` presenta una muestra. Esta inspección no modifica los datos ni convierte `Otra` en provincia oficial.

**Código original de la celda:**

```python
print(konzerta["provincia"].value_counts())

display(
    konzerta.loc[
        konzerta["provincia"].str.strip().str.lower() == "otra",
        ["titulo", "provincia", "localidad", "modalidad"]
    ].head(20)
)
```

### Celda 42 · Código

**Objetivo y explicación de las funciones:** `groupby(['provincia','area'],dropna=False)` y otras combinaciones cruzan dimensiones; `agg(ofertas=('id','size'))` cuenta anuncios. `value_counts()` obtiene la distribución simple. `reset_index()` y `sort_values()` facilitan comparar. Las categorías originales se preservan para auditoría.

**Código original de la celda:**

```python
# ==========================================================
# DISTRIBUCIÓN GEOGRÁFICA Y LABORAL
# ==========================================================

# 1. Distribución general por provincia
dist_provincia = (
    konzerta["provincia"]
    .value_counts()
    .reset_index()
    .rename(columns={"count": "ofertas"})
)

dist_provincia["porcentaje"] = (
    dist_provincia["ofertas"] / len(konzerta) * 100
).round(2)

print("OFERTAS POR PROVINCIA")
display(dist_provincia)


# 2. Distribución por provincia y área profesional
tabla_provincia_area = (
    konzerta
    .groupby(["provincia", "area"], dropna=False)
    .agg(ofertas=("id", "size"))
    .reset_index()
    .sort_values("ofertas", ascending=False)
)

print("\nOFERTAS POR PROVINCIA Y ÁREA")
display(tabla_provincia_area.head(20))


# 3. Distribución por provincia y nivel laboral
tabla_provincia_nivel = (
    konzerta
    .groupby(["provincia", "nivel_laboral"], dropna=False)
    .agg(ofertas=("id", "size"))
    .reset_index()
    .sort_values("ofertas", ascending=False)
)

print("\nOFERTAS POR PROVINCIA Y NIVEL LABORAL")
display(tabla_provincia_nivel.head(20))


# 4. Distribución conjunta
tabla_geografica_completa = (
    konzerta
    .groupby(
        ["provincia", "area", "nivel_laboral"],
        dropna=False
    )
    .agg(ofertas=("id", "size"))
    .reset_index()
    .sort_values("ofertas", ascending=False)
)

print("\nDISTRIBUCIÓN GEOGRÁFICA COMPLETA")
display(tabla_geografica_completa.head(20))
```

### Celda 43 · Explicación

**Qué presenta el notebook:** ### **Visualización de la distribución por Provincia** Creamos un gráfico interactivo para representar cómo se reparten las oportunidades de empleo en el territorio nacional.

### Celda 44 · Código

**Objetivo y explicación de las funciones:** `px.bar(...,orientation='h')` representa porcentaje por ubicación; `update_traces(texttemplate='%{text:.2f}%')` muestra dos decimales; `update_layout(showlegend=False)` oculta una leyenda redundante.

**Código original de la celda:**

```python
fig_prov = px.bar(
    dist_provincia,
    x="porcentaje",
    y="provincia",
    orientation="h",
    text="porcentaje",
    title="Distribución porcentual de Ofertas de Empleo por Provincia en Panamá",
    labels={"porcentaje": "Porcentaje del total (%)", "provincia": "Provincia"},
    color="provincia",
    color_discrete_sequence=px.colors.qualitative.Prism
)

fig_prov.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
fig_prov.update_layout(height=500, showlegend=False)
fig_prov.show()
```

### Celda 45 · Código

**Objetivo y explicación de las funciones:** `head(5)` selecciona las ubicaciones con más anuncios y `head(10)` las áreas principales. `isin()` restringe la tabla cruzada. `px.bar(...,barmode='group')` coloca las barras lado a lado para comparar áreas dentro de cada ubicación. Las ubicaciones no oficiales deben tratarse con cautela.

**Código original de la celda:**

```python
# ==========================================================
# OFERTAS POR PROVINCIA Y ÁREA PROFESIONAL
# ==========================================================

# Seleccionar las cinco provincias con más anuncios
top_5_provincias = (
    dist_provincia
    .head(5)["provincia"]
    .tolist()
)

# Seleccionar las diez áreas profesionales con más anuncios
top_10_areas = (
    tabla_areas
    .sort_values("ofertas", ascending=False)
    .head(10)["area"]
    .tolist()
)

# Filtrar los registros
datos_geograficos = tabla_provincia_area[
    tabla_provincia_area["provincia"].isin(top_5_provincias)
    & tabla_provincia_area["area"].isin(top_10_areas)
].copy()

# Crear gráfico de barras agrupadas
fig_prov_area = px.bar(
    datos_geograficos,
    x="provincia",
    y="ofertas",
    color="area",
    barmode="group",
    title="Ofertas laborales por provincia y área profesional",
    labels={
        "provincia": "Provincia",
        "ofertas": "Cantidad de ofertas",
        "area": "Área profesional"
    },
    category_orders={
        "provincia": top_5_provincias
    },
    color_discrete_sequence=px.colors.qualitative.Safe
)

fig_prov_area.update_layout(
    height=650,
    xaxis_title="Provincia",
    yaxis_title="Número de ofertas",
    legend_title_text="Área profesional"
)

fig_prov_area.show()
```

### Celda 46 · Código

**Objetivo y explicación de las funciones:** `groupby('provincia')['ofertas'].transform('sum')` repite el total de cada provincia en cada fila para calcular proporciones. Luego `ofertas/total_provincia*100` obtiene el porcentaje por nivel. `px.bar(...,barmode='stack')` permite comparar composición relativa.

**Código original de la celda:**

```python
# ==========================================================
# NIVEL LABORAL POR PROVINCIA
# ==========================================================

# Seleccionar las cinco provincias con más ofertas
top_5_provincias = (
    dist_provincia
    .head(5)["provincia"]
    .tolist()
)

# Filtrar las ofertas de esas provincias
datos_nivel_provincia = tabla_provincia_nivel[
    tabla_provincia_nivel["provincia"].isin(top_5_provincias)
].copy()

# Calcular el total de ofertas por provincia
datos_nivel_provincia["total_provincia"] = (
    datos_nivel_provincia
    .groupby("provincia")["ofertas"]
    .transform("sum")
)

# Calcular la participación de cada nivel laboral
datos_nivel_provincia["porcentaje"] = (
    datos_nivel_provincia["ofertas"]
    / datos_nivel_provincia["total_provincia"] * 100
)

# Crear gráfico de barras apiladas
fig_nivel_provincia = px.bar(
    datos_nivel_provincia,
    x="porcentaje",
    y="provincia",
    color="nivel_laboral",
    orientation="h",
    title="Distribución de niveles laborales por provincia",
    labels={
        "porcentaje": "Porcentaje de ofertas (%)",
        "provincia": "Provincia",
        "nivel_laboral": "Nivel laboral"
    },
    category_orders={
        "provincia": list(reversed(top_5_provincias))
    },
    color_discrete_sequence=px.colors.qualitative.Safe
)

fig_nivel_provincia.update_layout(
    height=600,
    barmode="stack",
    xaxis_range=[0, 100],
    legend_title_text="Nivel laboral"
)

fig_nivel_provincia.update_traces(
    hovertemplate="%{y}: %{x:.2f}%<extra>%{fullData.name}</extra>"
)

fig_nivel_provincia.show()
```

### Celda 47 · Explicación

**Qué presenta el notebook:** ### **Pregunta 5. Evolución semanal de las ofertas (julio–octubre de 2026)** Las ofertas se filtran por su fecha de publicación entre el 1 de julio y el 31 de octubre de 2026 y se agrupan en semanas que empiezan el lunes. Se conservan semanas sin registros dentro del intervalo observado. **La extracción del archivo se realizó el 16 de octubre de 2026**: no corresponde interpretar las fechas posteriores a esa extracción como semanas sin demanda; el gráfico se limita a la ventana realmente observada.

### Celda 48 · Código

**Objetivo y explicación de las funciones:** `pd.to_datetime(errors='coerce')` interpreta fechas; `pd.Timestamp` establece límites y `min()` evita usar semanas posteriores a la fecha de extracción documentada. `between()` filtra fechas; `pd.Timedelta` permite incluir el día final completo. `.dt.to_period('W-SUN').dt.start_time` agrupa semanas lunes–domingo. `pd.date_range(freq='W-MON')` crea todas las semanas observadas; `groupby().size().reindex(fill_value=0)` incluye semanas sin registros. `rename_axis()` y `reset_index(name='ofertas')` producen una tabla utilizable. `semana_parcial` marca la primera y última semana si no están completas.

**Código original de la celda:**

```python
# ==========================================================
# EVOLUCIÓN SEMANAL OBSERVADA
# ==========================================================
fechas_publicacion = pd.to_datetime(konzerta["fecha_publicacion"], errors="coerce")
fecha_inicio = pd.Timestamp("2026-07-01")
fecha_fin_teorica = pd.Timestamp("2026-10-31")
# Fecha de obtención documentada en la portada del proyecto
fecha_extraccion = pd.Timestamp("2026-10-16")
fecha_fin_observada = min(fecha_fin_teorica, fecha_extraccion)
ofertas_periodo = konzerta.loc[
    fechas_publicacion.between(fecha_inicio, fecha_fin_observada + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1))
].copy()
ofertas_periodo["fecha_publicacion"] = fechas_publicacion.loc[ofertas_periodo.index]
ofertas_periodo["semana_inicio"] = (
    ofertas_periodo["fecha_publicacion"].dt.to_period("W-SUN").dt.start_time
)
semanas_observadas = pd.date_range(
    start=fecha_inicio.to_period("W-SUN").start_time,
    end=fecha_fin_observada.to_period("W-SUN").start_time,
    freq="W-MON"
)
tendencia_semanal = (
    ofertas_periodo.groupby("semana_inicio").size()
    .reindex(semanas_observadas, fill_value=0)
    .rename_axis("semana_inicio").reset_index(name="ofertas")
)
tendencia_semanal["semana_parcial"] = (
    (tendencia_semanal["semana_inicio"] < fecha_inicio)
    | (tendencia_semanal["semana_inicio"] + pd.Timedelta(days=6) > fecha_fin_observada)
)
print("Ofertas en el período observado:", len(ofertas_periodo))
print("Último día de observación:", fecha_fin_observada.date())
print("Semanas (incluye semanas parciales):", len(tendencia_semanal))
display(tendencia_semanal)
```

### Celda 49 · Explicación

**Qué presenta el notebook:** ### **Visualización de la tendencia semanal** El gráfico presenta el volumen semanal observado desde julio hasta la fecha de extracción, con marcadores para las semanas. La primera y última semana pueden estar incompletas, por lo que sus cantidades no son directamente comparables con semanas completas.

### Celda 50 · Código

**Objetivo y explicación de las funciones:** `px.line(markers=True)` dibuja la serie semanal con puntos. `update_traces()` cambia grosor, tamaño de marcadores y texto emergente; `update_layout(hovermode='x unified')` agrupa detalles al pasar el cursor. El gráfico describe el período capturado, no predice ofertas.

**Código original de la celda:**

```python
# ==========================================================
# GRÁFICO DE EVOLUCIÓN SEMANAL
# ==========================================================
fig_linea = px.line(
    tendencia_semanal,
    x="semana_inicio",
    y="ofertas",
    markers=True,
    title="Evolución semanal de ofertas de empleo (julio–octubre de 2026)",
    labels={"semana_inicio": "Semana de publicación", "ofertas": "Número de ofertas"}
)
fig_linea.update_traces(
    line=dict(width=3), marker=dict(size=8),
    hovertemplate="Semana del %{x|%d/%m/%Y}<br>Ofertas: %{y}<extra></extra>"
)
fig_linea.update_layout(height=500, hovermode="x unified")
fig_linea.show()
print("Nota: la primera y última semana pueden estar incompletas.")
```

### Celda 51 · Explicación

**Qué presenta el notebook:** ## **Capa oro: tablas agregadas para el dashboard** Se construyen tablas agregadas a partir de la capa plata. El dashboard de Streamlit **solo lee archivos de la capa oro**. Las cifras representan anuncios del archivo, no todo el mercado laboral. Las agregaciones de salarios incluyen exclusivamente registros sin alertas y las de experiencia se interpretan con precaución.

### Celda 52 · Código

**Objetivo y explicación de las funciones:** `groupby(...).agg(...).reset_index()` genera tablas agregadas por las dimensiones de cada pregunta. `.copy()` reutiliza resúmenes salariales y temporales ya calculados. El diccionario `tablas_oro` asocia nombre de archivo y DataFrame; `for nombre, tabla in tablas_oro.items()` recorre los seis resultados. `to_csv(index=False,encoding='utf-8-sig')` los guarda. **El dashboard consume estos archivos y no el Excel original.**

**Código original de la celda:**

```python
# ==========================================================
# GENERACIÓN Y EXPORTACIÓN DE TABLAS AGREGADAS
# ==========================================================
ORO.mkdir(parents=True, exist_ok=True)

oro_areas = (
    konzerta.groupby(["area", "subarea"], dropna=False)
    .agg(ofertas=("id", "size"), vacantes=("vacantes", "sum"))
    .reset_index()
    .sort_values("ofertas", ascending=False)
)
oro_modalidades = (
    konzerta.groupby(["area", "modalidad"], dropna=False)
    .agg(ofertas=("id", "size"))
    .reset_index()
)
oro_geografia = (
    konzerta.groupby(["provincia", "area", "nivel_laboral"], dropna=False)
    .agg(ofertas=("id", "size"), vacantes=("vacantes", "sum"))
    .reset_index()
)
oro_salarios_experiencia = resumen_salarios_experiencia.copy()
oro_salarios_nivel = resumen_salarios_nivel.copy()
oro_tendencia_semanal = tendencia_semanal.copy()

tablas_oro = {
    "oro_areas_subareas.csv": oro_areas,
    "oro_modalidades_area.csv": oro_modalidades,
    "oro_geografia.csv": oro_geografia,
    "oro_salarios_experiencia.csv": oro_salarios_experiencia,
    "oro_salarios_nivel.csv": oro_salarios_nivel,
    "oro_tendencia_semanal.csv": oro_tendencia_semanal,
}
for nombre, tabla in tablas_oro.items():
    tabla.to_csv(ORO / nombre, index=False, encoding="utf-8-sig")
    print(f"{nombre}: {len(tabla)} filas")
print("Capa oro generada:", ORO)
```

### Celda 53 · Explicación

**Qué presenta el notebook:** ## **Validación de la capa oro** Se comprueba que las tablas agregadas reproduzcan el total de anuncios cuando corresponda, que existan los archivos de salida y que la información salarial sea presentada como una muestra restringida.

### Celda 54 · Código

**Objetivo y explicación de las funciones:** `assert` comprueba condiciones indispensables: que las sumas de anuncios de tres tablas agregadas coincidan con `len(konzerta)` y que todos los archivos existan (`all(...is_file()...)`). Si falla una condición, la ejecución se interrumpe con `AssertionError`. No sustituye las pruebas visuales del dashboard.

**Código original de la celda:**

```python
# ==========================================================
# VALIDACIÓN DE TOTALES Y ARCHIVOS
# ==========================================================
total_ofertas = len(konzerta)
assert int(oro_areas["ofertas"].sum()) == total_ofertas
assert int(oro_modalidades["ofertas"].sum()) == total_ofertas
assert int(oro_geografia["ofertas"].sum()) == total_ofertas
assert all((ORO / nombre).is_file() for nombre in tablas_oro)
print("Validación correcta: las agregaciones principales coinciden con", total_ofertas, "anuncios.")
print("Salarios con experiencia:", len(salarios_experiencia), "ofertas (interpretar con cautela).")
```

## Ejemplo guiado: cómo leer una agregación

```python
resumen = (
    konzerta.groupby("area", dropna=False)
    .agg(ofertas=("id", "size"), vacantes=("vacantes", "sum"))
    .reset_index()
    .sort_values("ofertas", ascending=False)
)
```

- `konzerta` es el DataFrame limpio; `groupby("area")` forma un grupo por área.
- `ofertas=("id","size")` cuenta las filas de cada grupo, incluso si el valor de `id` fuera nulo; es un conteo de anuncios.
- `vacantes=("vacantes","sum")` suma plazas declaradas, que no tienen por qué ser iguales a los anuncios.
- `reset_index()` transforma el índice de grupos en una columna normal.
- `sort_values(...,ascending=False)` coloca primero las áreas con más anuncios.
- **Comprobación:** `resumen["ofertas"].sum()` debe coincidir con `len(konzerta)` si todos los anuncios pertenecen a un grupo.

## Recomendaciones técnicas que deben explicarse en la defensa

- La celda de limpieza usa `registrar()` para documentar decisiones, pero la guía del equipo solicita un formato resumido de bitácora de dos columnas; verificar la exigencia oficial antes de cambiar el archivo.
- La columna `provincia` puede contener `Otra`. No es una provincia oficial y debe revisarse contra `localidad` antes de corregirla.
- La mediana salarial se calcula solo sobre anuncios con datos salariales suficientes y sin alertas; no se debe presentar como salario típico del mercado panameño.
- El análisis semanal tiene una fecha de extracción escrita en el código (`2026-10-16`): confirmar que coincida con el origen real del Excel.
- El notebook exporta seis tablas oro; el dashboard solo lee esas tablas. Si se cambia el Excel, hay que volver a ejecutar todas las celdas y sincronizar los CSV de oro.
- El notebook contiene comprobaciones `assert`, pero todavía deben realizarse pruebas de ejecución completa y de filtros/descargas del dashboard en los sistemas de destino.

## Documentación adicional del proyecto

La explicación de los requisitos, recomendaciones de cambio, arquitectura, instalación y entrega está en las secciones originales que siguen a esta guía.

---

# Documentación complementaria del equipo

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


## 12. Recomendaciones de cambios basadas en los documentos del equipo y del profesor

Esta sección distingue **requisitos de las indicaciones actualizadas del profesor** y **recomendaciones organizativas de la guía del equipo**. No todos los cambios sugeridos se han aplicado todavía al código.

| Prioridad | Cambio recomendado | Motivo / fuente | Estado a comprobar |
|---|---|---|---|
| Alta | Añadir un diccionario de datos con columna, tipo y descripción | Exigencia del profesor para documentar la fuente | No está completo en este README |
| Alta | Revisar la bitácora de limpieza y su justificación | El profesor exige documentar decisiones sobre nulos, duplicados y atípicos; la guía del equipo recomienda exactamente dos columnas «Columna» y «Justificación» | El notebook exporta cuatro columnas; acordar formato final según el PDF vigente |
| Alta | Probar el pipeline completo desde una copia limpia en Mac y Windows | La entrega debe reproducirse en otra computadora siguiendo el README | Pendiente de prueba integral |
| Alta | Confirmar que el dashboard se actualiza tras cambiar el Excel y volver a ejecutar el notebook | Requisito de reporte automático, solo con capa oro | Pendiente de demostración completa |
| Alta | Incorporar el enlace real a la grabación colaborativa de al menos una hora | Requisito obligatorio de trabajo en grupo; debe participar todo el equipo | Pendiente de proporcionar enlace |
| Alta | Preparar el PDF de presentación y el ZIP final | Entregables del profesor, además del código | Pendiente |
| Media | Agregar una o dos líneas de interpretación a cada gráfico y un hilo narrativo de contexto → hallazgos → conclusión | Storytelling de la rúbrica | Revisar en notebook, dashboard y presentación |
| Media | Confirmar fecha de extracción, volumen y cobertura de variables | Evita contradicciones entre portada, nombre del archivo y resultados | Pendiente de validación |
| Media | Revisar «Otra» y «Sin dato» como categorías geográficas, sin imputar provincias arbitrariamente | Mejora la calidad e interpretación | Pendiente |
| Media | Repartir preguntas por bloques y hacer revisión cruzada | Sugerencia de la guía del equipo: A (1 y 4), B (3 y 5), C (2 y calidad) | Organización sugerida, no requisito del profesor |
| Media | Documentar aprendizajes individuales y preparar la defensa de todo el código | La defensa evalúa dominio individual | Pendiente de cada integrante |

**Advertencia sobre versiones de instrucciones:** la guía de equipo del 24 de octubre menciona una bitácora de dos columnas, una defensa de 20 minutos y una rúbrica 60/40. Sin embargo, el PDF actualizado «Proyecto final Introducción a la Programación para Ciencia de Datos (1).pdf» establece **presentación de 30 minutos** y evaluación **50 puntos trabajo / 50 sustentación**. Para la entrega debe prevalecer el PDF actualizado del profesor y conviene confirmar cualquier contradicción directamente con él.

**Fechas del PDF actualizado:** avance del notebook después del 31 de octubre; revisión del dashboard el 6 de noviembre; presentación y defensa el **7 de noviembre de 2026**. La meta del 28 de octubre mencionada en la guía del equipo es interna, no la fecha oficial de entrega.

**Próximo paso recomendado al equipo:** ejecutar juntos el notebook desde la primera celda, contrastar los CSV exportados con el dashboard, registrar evidencias, completar el diccionario y preparar una defensa en la que cualquiera pueda explicar cada fase.
