# Validación de la entrega completa

La entrega se regeneró desde las fuentes del dashboard final y del mismo JSON original. El archivo release_manifest.json registra hashes, módulos y resultados para identificar esta versión sin depender de ZIP anteriores.

## Datos y métricas

- 3,344 agregados únicos; 38,382,189 operaciones representadas; cobertura de enero de 2021 a mayo de 2026.
- Sin nulos en campos requeridos ni claves duplicadas; conteos enteros no negativos y demora ≥60 contenida en demora ≥15.
- 7,959 operaciones sin categoría conservadas como Unclassified.
- 139 filas excluidas solo de la distribución de causas; 3,205 filas válidas y 92.435025006% de cobertura de operaciones.
- Las tasas usan cocientes de sumas. La demora media usa delayed15 como denominador. Los cortes vacíos muestran tasas vacías, no cero.
- JavaScript y Python coinciden en 19 combinaciones de filtros dentro de 1e-8.

## HTML

Se verificaron siete módulos, ocho KPI con SVG, nombres completos de 22 aerolíneas y 35 aeropuertos, doce meses con nombres completos en orden cronológico, trece ubicaciones de gráficos, filtros, corte vacío, exportación CSV, mapa vectorial y selección de aeropuerto. La interfaz funciona en el modo sin conexión con solicitudes HTTP/HTTPS bloqueadas y a 390 píxeles sin desbordamiento horizontal.

Metodología contiene doce tarjetas y Conclusiones cuatro tarjetas con sus recomendaciones. El mapa real usa calles/satélite de Esri; se comprobó su servicio y la alternativa sin conexión. La carga de teselas depende de Internet y del proveedor. La revisión de interfaz de esta regeneración se hizo con el mapa local para no depender de servicios externos.

## Streamlit y notebook

Streamlit se comprobó con AppTest en sus siete módulos y con los nombres completos de meses. Las tarjetas e interpretaciones provienen de los mismos componentes que el HTML. Las pruebas de servidor real de la integración verificaron KPI, columnas, iconos y mapa sin excepciones.

El notebook se regeneró y ejecutó: 21 celdas de código sin errores, doce figuras analíticas y cuatro salidas HTML enriquecidas para KPI, mapa, metodología y conclusiones. Los contenidos interactivos necesitan un visor de notebook con HTML/JavaScript habilitado y confianza en el documento. Los mapas de calles/satélite requieren Internet; la geometría vectorial es local.

## Power BI

Se comparó la instantánea embebida fila por fila contra las dimensiones, conteos, minutos, etiquetas y banderas del dashboard. La auditoría comprobó siete páginas, doce análisis en trece ubicaciones, doce tarjetas metodológicas, cuatro conclusiones, meses ordenados, catálogos, recursos, referencias y límites del lienzo de 215 visuales.

Los 225 archivos de definición pasaron validación con los esquemas públicos de Microsoft. Los filtros sincronizados y controles de soporte/referencia están definidos en PBIR y DAX. El paquete exclusivo incluye el CSV de referencia y consulta de validación.

**Pendiente:** abrir y actualizar el proyecto en Power BI Desktop, ejecutar el motor DAX y comprobar el renderizado y el comportamiento de sincronización. La validación de esquema y datos no equivale a ejecutar Desktop. Se entrega PBIP/PBIR, no un PBIX binario.

## Reproducibilidad y límites

build_project.py regenera HTML, datos, notebook y Power BI y ejecuta las comprobaciones antes de empaquetar. El ZIP final excluye otros ZIP, capturas internas y cachés. El mapa, controles, tipografía y distribución se adaptan al motor de cada plataforma: Azure Maps y visuales nativos en Power BI; Leaflet/Plotly en HTML y Streamlit.

No se verificó el extracto contra microdatos originales, no se creó un repositorio remoto y no se desplegó Streamlit Cloud ni Power BI Service. Tableau no forma parte de estas tres implementaciones. Las limitaciones de agregación, cobertura y dependencia estadística se explican en METODOLOGIA.md.

## Resultados consultables

- test_results.json: datos, figuras y pruebas HTML.
- notebook_validation.json: ejecución y paneles del notebook.
- schema_validation.json: esquemas PBIR.
- ../powerbi/revision_dashboard.json: auditoría de sincronización del modelo.
- ../powerbi/REVISION_POWER_BI.md: alcance y pasos de comprobación en Desktop.
