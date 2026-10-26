# Proyecto Konzerta — análisis de ofertas de empleo en Panamá

Proyecto académico de **Introducción a la Programación para Ciencia de Datos**.

**Equipo:** Francia Vergara, Luis Santimateo y Yenia Rojas.  
**Fuente:** Konzerta.  
**Archivo original:** `datos/bronce/Konzerta 08-oct-2026.xlsx` (obtención documentada: 16-oct-2026).

## Objetivo
Analizar ofertas de empleo del archivo de Konzerta para describir demanda por área y subárea, salarios y experiencia, modalidades, distribución geográfica y evolución semanal de anuncios entre julio y octubre de 2026.

## Estructura

- `datos/bronce/`: Excel original, no se modifica.
- `datos/plata/`: datos normalizados, bitácora de limpieza y perfiles de calidad (generados por el notebook).
- `datos/oro/`: seis tablas agregadas CSV para consumo del dashboard (generadas por el notebook).
- `notebooks/Proyecto_Konzerta_KR.ipynb`: carga, calidad, limpieza, exploración, agregación y validación.
- `dashboard/app.py`: aplicación Streamlit que lee **únicamente capa oro**.
- `requirements.txt`: dependencias de Python.

## Instalación y ejecución local

Desde la carpeta `Proyecto_Konzerta`:

```bash
python -m pip install -r requirements.txt
jupyter notebook notebooks/Proyecto_Konzerta_KR.ipynb
```

Ejecuta **todas las celdas en orden** para producir los CSV de plata y oro. Si Jupyter no está instalado, instala `notebook` o abre el archivo con JupyterLab / VS Code.

Después:

```bash
streamlit run dashboard/app.py
```

En Google Colab, la celda de preparación monta Google Drive y utiliza `/content/drive/MyDrive/Proyecto_Konzerta`. Copia allí la estructura del proyecto y el Excel original antes de ejecutar.

## Archivos generados

**Plata:** `konzerta_limpio.csv`, `bitacora_limpieza.csv`, `perfil_bronce.csv`, `perfil_plata.csv`.

**Oro:** `oro_areas_subareas.csv`, `oro_modalidades_area.csv`, `oro_geografia.csv`, `oro_salarios_experiencia.csv`, `oro_salarios_nivel.csv`, `oro_tendencia_semanal.csv`.

## Preguntas de investigación

1. ¿Qué áreas y subáreas tienen más anuncios y vacantes?
2. ¿Cómo varían los salarios según la experiencia requerida?
3. ¿Qué modalidades de trabajo predominan por área?
4. ¿Cómo se distribuyen las ofertas por provincia, área y nivel laboral?
5. ¿Cómo evoluciona el volumen de anuncios por semana en el período observado?

## Limitaciones metodológicas

- Los datos representan únicamente anuncios capturados en el archivo, no todo el mercado laboral.
- En la ejecución registrada, 414 anuncios tenían salario máximo sin alerta y **solo 10** informaban además experiencia. Los resultados salariales por experiencia son exploratorios.
- No se ha confirmado de forma independiente la moneda ni periodicidad de todos los salarios.
- El archivo fue obtenido el **16 de octubre de 2026**. La serie semanal termina en la ventana observada y las semanas parciales no se comparan como semanas completas.
- Las cifras de vacantes dependen de los valores declarados en el archivo.
- Los archivos generados deben verificarse ejecutando el pipeline completo; guardar código en GitHub no ejecuta automáticamente el notebook.

## Flujo de datos

`Excel original (bronce) → limpieza + bitácora (plata) → agregaciones (oro) → Streamlit`

El dashboard no accede a bronce ni plata.

## Dashboard interactivo

La aplicación incluye cinco pestañas: panorama profesional, geografía, modalidades, salarios y evolución semanal; filtros por área y ubicación, elección entre anuncios y vacantes donde los datos lo permiten, tamaño del top de categorías, mapa de calor, indicadores y descarga de tablas CSV filtradas.

**Alcance de filtros:** área afecta panorama, modalidades y geografía; ubicación afecta solo geografía. Las tablas agregadas salariales y semanales no contienen área ni provincia y, por tanto, no admiten esos filtros. Los indicadores muestran explícitamente su ámbito. Los valores «Otra» y «Sin dato» en ubicación no son provincias oficiales: se conservan para evitar perder registros hasta verificar las localidades originales.

## Trabajar entre Mac, Colab y Google Drive

- **GitHub:** código fuente, notebook, dashboard y documentación. Actualiza la copia de Mac con Git después de comprobar cambios locales.
- **Colab / Drive:** al ejecutar el notebook desde Colab, los CSV se escriben en `/content/drive/MyDrive/Proyecto_Konzerta/datos/plata` y `datos/oro`.
- **Mac:** el dashboard lee exclusivamente `Proyecto_Konzerta/datos/oro`. Copia o sincroniza los seis CSV de Drive a esa carpeta antes de ejecutar Streamlit; no hay sincronización automática entre Drive y Mac incluida en este repositorio.
- **Precaución:** no ejecutes una copia de archivos sobre un notebook abierto con modificaciones no guardadas. El notebook ya no realiza `git pull` ni sobrescribe su propia copia al iniciar.

**Compatibilidad:** se recomienda Python 3.10 o posterior para el entorno local y las dependencias especificadas en `requirements.txt`.
