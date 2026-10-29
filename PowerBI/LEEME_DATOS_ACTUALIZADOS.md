# AeroPulse — sincronización de datos con HTML

Los datos de las tablas Vuelos (3,344 filas), Hubs (35 filas) y Horarios (10 filas) se han reinsertado desde el JSON proporcionado por el usuario, conservando exactamente todos los campos numéricos originales. Los campos auxiliares del modelo se conservaron para no romper las relaciones y los visuales. La referencia de día de semana también se conserva sin alteración.

**Medida corregida:** `Demora media` ahora equivale a `SUM(Vuelos[sumDelayMin]) / SUM(Vuelos[ops])` (minutos por operación), de acuerdo con las definiciones del HTML. No se modificaron colores ni distribución.

**Verificación:** `CONTROL_DATOS_HTML_vs_PowerBI.csv` permite cotejar operaciones, puntuales, demoras y tasas por año. Las tablas Hubs y Horarios son referencias independientes: no responden a los filtros del cubo de vuelos, como también se indica en el HTML.

**Abrir:** `AeroPulse.pbip` en Power BI Desktop. No hace falta elegir un archivo externo al actualizar, porque los datos están integrados en el modelo mediante Power Query M. Si aparece una alerta sobre actualización, revisa las opciones del modelo y pulsa Actualizar.

**Limitación:** se verificó la igualdad de registros y la sintaxis JSON, pero no se pudo ejecutar Power BI Desktop desde este entorno para comparar visualmente las tarjetas después de la carga.
