# US_Flights · Proyecto completo actualizado

Esta entrega reúne la última versión del dashboard HTML, la app Streamlit, el notebook ejecutado, los datos enriquecidos y el proyecto Power BI editable. Comparten datos, nombres, KPI, interpretaciones y los siete módulos: Panorama, Estacionalidad, Geografía, Aerolíneas, Marco del proyecto, Metodología y Conclusiones.

## Abrir la versión HTML

Abre **dashboard_US_Flights.html** en Chrome, Edge o Firefox. Incluye datos, Plotly, Leaflet, tipografía Manrope y geometría local. Los filtros muestran nombres completos de meses, aerolíneas y aeropuertos. Las tarjetas KPI conservan iconos, estados y colores del diseño.

El mapa real ofrece calles y satélite de Esri y requiere Internet. El mapa vectorial local permanece disponible sin conexión. Para modificar HTML, CSS y JavaScript por separado usa **web/index.html**, **web/style.css** y **web/dashboard.js**.

## Ejecutar Streamlit

En Windows, con Python 3.11 o posterior instalado, ejecuta **iniciar_streamlit.bat**. La primera ejecución instala dependencias y requiere Internet.

En una terminal, desde esta carpeta:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

La app incorpora los siete módulos, ocho KPI con iconos, filtros con nombres completos, tarjetas de metodología, cuatro conclusiones con sus recomendaciones y mapas de calles/satélite o vectoriales.

## Abrir Power BI

Extrae el paquete completo y abre **powerbi/US_Flights.pbip** en Power BI Desktop. Mantén juntas las carpetas US_Flights.Report y US_Flights.SemanticModel. Pulsa **Actualizar** para importar la instantánea embebida; no necesitas Python para abrirla.

Se incluyen siete páginas, nombres completos, meses ordenados, iconos, doce tarjetas metodológicas y cuatro conclusiones. Los filtros y controles de referencia OTP/soporte se sincronizan entre las cuatro vistas analíticas. El mapa nativo usa Azure Maps; la tabla geográfica permite consultar los datos sin fondo cartográfico. Las métricas, recursos, posiciones y referencias del modelo fueron auditados frente al HTML.

**Pendiente:** abrir y actualizar en Desktop, ejecutar DAX y comprobar el renderizado. Se entrega PBIP/PBIR, no un PBIX binario. Sigue **powerbi/LEEME_POWER_BI.md** y **powerbi/REVISION_POWER_BI.md**.

## Usar el notebook

Abre **analisis_US_Flights.ipynb** desde esta carpeta en Jupyter. Ya contiene las salidas ejecutadas: auditoría, métricas, doce análisis con variables e interpretación, tarjetas KPI, nombres completos, mapa interactivo, marco, doce tarjetas metodológicas y cuatro conclusiones visuales.

Para ejecutarlo localmente instala las dependencias y Jupyter:

```bash
python -m pip install -r requirements.txt
python -m pip install jupyter nbformat
python -m jupyter notebook
```

Confía en el notebook para mostrar los contenidos HTML/JavaScript. Las tarjetas se calculan desde la misma base; el mapa de calles/satélite requiere Internet y ofrece la alternativa vectorial. Las doce figuras analíticas se muestran una vez cada una en el notebook; el dashboard sitúa la comparativa mensual en dos vistas (trece ubicaciones).

## Datos y alcance

- **data/source.json:** copia íntegra del JSON original, conservada como referencia.
- **data_vuelos_2021_2026_con_nombres.json:** añade AirlineName/AirlineLabel al cubo y AirportName/AirportLabel a los hubs, sin alterar códigos ni cifras.
- **data/vuelos_auditados.csv:** agregados con nombres, residuos y banderas de calidad.
- **data/causas_no_conciliadas.csv:** filas excluidas exclusivamente del análisis de causas.
- **data/audit.json:** auditoría de la carga.
- **data/kpi_referencia_python.csv** y **powerbi/kpi_referencia_python.csv:** valores para contrastar métricas.

Cobertura: **enero de 2021 a mayo de 2026**, 65 meses, 3,344 agregados y 38,382,189 operaciones representadas. 2026 es parcial. Las tasas son cocientes de sumas; no promedios simples de porcentajes. La puntualidad global es 79.3408239431% y la referencia de 80% es interna.

Se conservan 7,959 operaciones sin categoría. Las 139 filas con causas no conciliadas solo se excluyen de la distribución de causas (92.4350% de cobertura de operaciones). Los resúmenes horarios y de aeropuertos carecen de claves para cruzarse con el cubo. No hay detalle estatal ni semanal suficiente. Wilson 95% supone un modelo binomial; no mide sesgo, dependencia ni desempeño futuro. La procedencia del extracto no fue cotejada con microdatos BTS/DOT.

## Filtros y referencias

Año, mes, aerolínea y radio filtran el cubo y sus KPI. Aeropuerto afecta solo el resumen geográfico. El horario permanece global. **Marco del proyecto, Metodología y Conclusiones usan la base completa**; los KPI superiores de HTML/Streamlit conservan el filtro activo.

Power BI usa visuales y mapas nativos, tipografía Segoe UI y soporte mediante opciones predefinidas. HTML/Streamlit incluyen Manrope, degradados CSS y entrada de soporte numérica. La equivalencia comprobada es de datos y significado analítico; la presentación se adapta a cada plataforma.

## Regenerar y verificar todo

```bash
python -m pip install -r requirements-build.txt
python build_project.py
```

El proceso regenera HTML, datos enriquecidos, notebook y Power BI, ejecuta verificaciones de datos y sincronización, y crea los dos ZIP **fuera** de esta carpeta. Excluye ZIP antiguos, cachés y capturas internas. Cierra Power BI Desktop antes de regenerar su proyecto.

Para incluir comprobación de interfaz, instala Chromium con Playwright y proporciona la ruta de su ejecutable. Para validar esquemas Microsoft se requiere Internet:

```bash
python -m playwright install chromium
python build_project.py --browser RUTA_AL_EJECUTABLE_CHROMIUM --schemas
```

**release_manifest.json** registra los archivos y hashes de la entrega, la referencia HTML y la auditoría de Power BI. Ninguna prueba automatizada local sustituye la apertura ni el motor DAX de Desktop.

## Documentación

- **docs/METODOLOGIA.md:** problema, modelo, calidad, incertidumbre y uso crítico de IA.
- **docs/MATRIZ_ANALITICA.md:** preguntas, variables, tareas y decisiones.
- **docs/DICCIONARIO_KPI.md:** fórmulas, unidades, frecuencia y dirección.
- **docs/HALLAZGOS.md:** interpretación de la carga inicial.
- **docs/MARCO_PROYECTO_2021_2026.md:** marco AeroPulse actualizado.
- **docs/CATALOGOS_Y_MAPA.md:** fuentes de nombres y cartografía.
- **docs/RUBRICA_Y_SUSTENTACION.md:** correspondencia con la guía y guion de defensa.
- **docs/VALIDACION.md:** alcance de las comprobaciones y pasos pendientes.
- **powerbi/revision_dashboard.json:** auditoría estructural y de datos del modelo.

El despliegue público en Streamlit Cloud, un repositorio remoto, Tableau y la publicación en Power BI Service no forman parte de los archivos creados. Para desplegar Streamlit, usa app.py como entrada y conserva las carpetas data, docs, web y la configuración de tema.

## Fuentes y licencias

El enlace de origen de datos se conserva en docs/METODOLOGIA.md. Los nombres de aerolíneas proceden del HTML original; los aeropuertos, del catálogo OurAirports. Los nombres actuales son identificadores descriptivos y no reconstruyen cambios históricos. Las coordenadas se conservan del proyecto. Leaflet, Plotly y Manrope incluyen sus avisos de licencia; los mapas muestran la atribución de sus proveedores. Ver docs/CATALOGOS_Y_MAPA.md.
