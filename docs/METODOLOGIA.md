# Metodología y decisiones de diseño

## Problema y usuario
Los responsables de operaciones necesitan localizar deterioros de puntualidad, dimensionar incidencias y priorizar diagnósticos por período, aerolínea y radio de vuelo. Este proyecto describe el cubo suministrado; no predice vuelos individuales ni identifica efectos causales.

Las cinco decisiones apoyadas son: (1) priorizar revisión de períodos con menor OTP; (2) seleccionar operadores para diagnóstico de servicio considerando su volumen; (3) revisar asignación por radio; (4) focalizar causas en datos conciliados; (5) identificar aeropuertos del resumen con menor puntualidad y mayor cancelación.

## Alcance y procedencia
Se utiliza exactamente el JSON adjunto: 3,344 agregados y 38,382,189 operaciones representadas, desde enero de 2021 hasta mayo de 2026 (65 meses). 2021-2025 contienen 12 meses; 2026 contiene 5. La fuente declarada por Data.txt es https://www.kaggle.com/datasets/umerhafeezsiddiqui/2021-2026-us-flights . No se descargaron ni verificaron los microdatos originales, su licencia o su correspondencia con BTS/DOT. No se certifica completitud del universo de vuelos de EE. UU.

Granularidad del cubo: Year × Month × Airline × OriginState × Haul. Los conteos y minutos son aditivos; las tasas se recalculan como cocientes de sumas. Todas las filas de OriginState son US; no se puede analizar diferencias estatales con este cubo. Haul solo trae corto, medio y largo; no se inventan límites de distancia.

## Control de calidad
- No se encontraron nulos en campos requeridos ni claves de agregado duplicadas.
- 108 filas contienen un residuo total de 7,959 operaciones: ops − ontime − delayed15 − cancel − divert. Se conserva como Unclassified; no se reasigna.
- 139 filas no concilian la suma de causas con sumDelayMin (tolerancia de 1 minuto por agregado). Se mantienen en los KPI del cubo y se excluyen exclusivamente de la distribución de causas. Este análisis cubre el 92.4350% de las operaciones; no es una muestra aleatoria.
- carrierDelay suma 1,988,566,601 minutos sin depurar, superior a los 508,544,837 minutos de sumDelayMin. No hay evidencia suficiente para corregir ese campo. La cuarentena evita atribuciones distorsionadas.
- El resumen dow tiene una sola fila, dow=1, con todas las operaciones. No permite identificar un ciclo semanal; no se usa para afirmar que todos los vuelos sean lunes.
- No existe tabla conjunta día×hora. Se omite el mapa de calor sintético que calculaba el HTML original.
- hubs y hourly no tienen año, mes, aerolínea ni radio. Permanecen desconectados del cubo. Las tasas de hubs se usan como porcentajes ya resumidos; no se reconstruyen conteos ontime redondeando porcentajes.
- El perfil horario no trae denominador ni definición verificable de avg_delay. Se muestra únicamente como resumen suministrado; no se promedia, pondera ni interpreta como efecto cascada.
- El máximo mensual observado es inusualmente alto (99.75% en febrero de 2023). Se conserva el dato y se recomienda cotejarlo con microdatos antes de decisiones de alto impacto.

## Definiciones y filtros
La semántica de llegada puntual (demora <15 minutos, no cancelada ni desviada) procede del HTML original y requiere validación con el diccionario del origen. El denominador de OTP, cancelación, desvíos y demoras es ops, que incluye incidencias: estas tasas no se llaman tasas sobre vuelos completados. Demora ≥60 se incluye en demora ≥15 y no se suma al mix.

Los filtros de año, mes, aerolínea y radio afectan todos los KPI y gráficos del cubo. El selector de aeropuerto afecta solo el mapa y la dispersión de hubs. El soporte mínimo por defecto de 30 operaciones limita radios, rankings e intervalos; no garantiza representatividad ni elimina sesgos. En Power BI se entrega soporte de 30 fijo en medidas visuales, editable en DAX. La referencia de 80% es una decisión interna; no se atribuye al DOT. En HTML/Streamlit puede ajustarse.

Sin datos se muestra “Sin datos”; no se sustituye una tasa indefinida por cero. Las series temporales preservan huecos para meses no observados. Para comparar años, seleccionar el mismo mes; 2026 no representa un año completo. La estacionalidad reúne años con cobertura desigual.

## Incertidumbre
Los intervalos Wilson del 95% se calculan a partir de ontime y ops por aerolínea con z=1.96. Son intervalos bajo un modelo binomial con independencia; no son intervalos predictivos. Si los datos son un censo del período, la tasa observada es descriptiva y el intervalo solo tiene lectura de modelo para un proceso hipotético. No incorpora correlación por clima, día o aeropuerto, sesgo de cobertura ni errores de medición. Los agregados impiden estimar esos efectos. Con grandes N los intervalos pueden ser visualmente estrechos.

## Diseño, accesibilidad y navegación
Se conserva el fondo #070d18, tarjetas #10192b, texto #e8eef8, secundario #8b97ab, acento #2ee6a6, turquesa #2ec4b6, dorado #f5b942, alerta #f07178 y azul #5b8def. El color identifica series y alertas; valores, etiquetas y textos comunican el significado sin depender solo del color. La referencia se distingue con línea discontinua. Barras parten de cero; mapa con escala OTP fija de 60 a 100. Burbujas comparan magnitud, no causalidad. Manrope en HTML con tipografía local de respaldo; fuentes estándar en Streamlit y Power BI.

Wireframe: barra lateral con navegación y filtros → encabezado con alcance → aviso de calidad → ocho KPI → gráficos con variables, justificación e interpretación → exportación de datos. Cuatro vistas: Panorama (año, mix, radio), Estacionalidad (mensual, mes del año, Wilson, horario), Geografía (mapa y hubs), Aerolíneas (dispersión, ranking y causas); Marco del proyecto adapta el diseño AeroPulse al cubo 2021–2026 y Metodología ofrece la consulta técnica.

## Auditoría de IA
Se utilizó IA para revisar el código fuente, detectar inconsistencias, redactar código e interpretaciones y preparar la implementación comparativa. Los hallazgos numéricos se recalculan desde los agregados; no se usan los ejemplos embebidos del HTML original. Se descartaron el cruce día×hora generado artificialmente, las inferencias causales del perfil horario y la etiqueta “meta DOT 80%”. Se conserva el archivo de origen y el registro de exclusiones. La validación técnica se registra en docs/VALIDACION.md; Power BI requiere comprobación final en Desktop.
