# Hallazgos e interpretaciones de la carga inicial

Los resultados siguientes corresponden al archivo completo; las aplicaciones recalculan la narrativa al filtrar.

## Tendencia histórica de operaciones y puntualidad

**Variables:** Year; ops (barras); ontime / ops (%) (línea).

**Justificación:** Barras y línea comparan volumen y nivel de servicio en ejes distintos. Comparar períodos equivalentes: 2026 termina en mayo.

**Interpretación:** La mayor puntualidad es 86.56% (2023) y la menor 76.42% (2025): brecha de 10.14 puntos porcentuales. Revisar capacidad en los períodos más bajos. Los años tienen cobertura desigual (2026: enero-mayo); filtra el mismo mes para comparar años.

## Composición del resultado operativo

**Variables:** ontime, delayed15, cancel, divert, Unclassified (conteos).

**Justificación:** La dona representa proporciones de categorías excluyentes y conserva el residuo sin clasificar. delayed60 es subconjunto de delayed15.

**Interpretación:** 79.34% de las operaciones son puntuales. Hay 7,959 operaciones sin clasificar; se conservan explícitamente. No sumar demora ≥60 a ≥15 porque se superponen. Decisión: revisar incidencias antes de asignar recursos.

## Puntualidad por radio de vuelo

**Variables:** Haul (categoría); ontime / ops (%).

**Justificación:** Comparar radios orienta la asignación de recursos; los límites de distancia del radio no están documentados en el JSON.

**Interpretación:** corto registra 82.41% y medio 77.07%. Investigar diferencias de rutas y operadores antes de atribuir el resultado al radio. Soporte: ≥30 operaciones.

## Evolución mensual observada

**Variables:** Year-Month; ontime / ops (%).

**Justificación:** El orden cronológico distingue cambios en el tiempo. Los meses sin observación son huecos, nunca ceros.

**Interpretación:** La mayor puntualidad es 99.75% (2023-02) y la menor 68.42% (2024-07): brecha de 31.33 puntos porcentuales. Revisar capacidad en los períodos más bajos. Los años tienen cobertura desigual (2026: enero-mayo); filtra el mismo mes para comparar años.

## Evolución mensual y comparación interanual

**Variables:** Year, Month; ops; Σontime / Σops; cancel / ops (%).

**Justificación:** Las curvas comparan los años por mes; con un año seleccionado se combina volumen, OTP y cancelación. La composición de aerolíneas y la cobertura pueden cambiar.

**Interpretación:** Lectura del agregado filtrado por mes: La mayor puntualidad es 82.95% (Abr) y la menor 71.01% (Jul): brecha de 11.94 puntos porcentuales. Revisar capacidad en los períodos más bajos. Los años tienen cobertura desigual (2026: enero-mayo); filtra el mismo mes para comparar años.

## Puntualidad e intervalo Wilson del 95%

**Variables:** Airline; ontime; ops; límite inferior y superior (%).

**Justificación:** Las barras de error expresan precisión bajo un modelo binomial. No cuantifican sesgo ni dependencia entre vuelos.

**Interpretación:** EM — Empire Airlines lidera con 89.29% (N=112); B6 — JetBlue Airways registra 71.71% (N=1,282,002). Investigar la mezcla de rutas y períodos: el ranking no ajusta confusores. Soporte mínimo: 30 operaciones. IC Wilson 95% bajo independencia binomial; estos agregados no permiten estimar correlación por aeropuerto/día. No es un intervalo predictivo; con millones de vuelos puede ser muy estrecho.

## Demora por bloque horario · resumen independiente

**Variables:** hour_block (hora); avg_delay (minutos).

**Justificación:** La línea compara el resumen horario suministrado. No hay conteos ni claves para ponderarlo o filtrarlo con el cubo.

**Interpretación:** El menor promedio es 65.6 min a las 08:00 y el mayor 98.4 min a las 04:00. El perfil no demuestra un efecto cascada. El denominador y el período del resumen no están documentados; no usarlo como promedio del cubo.

## Aeropuertos · ubicación y puntualidad

**Variables:** Latitud, longitud (coordenadas); otp (%); flights (conteo).

**Justificación:** La ubicación permite explorar concentraciones espaciales. Son aeropuertos seleccionados; no se deriva un mapa estatal.

**Interpretación:** FLL — Fort Lauderdale Hollywood International Airport presenta la menor puntualidad del resumen mostrado: 73.8%. Priorizar su diagnóstico junto con volumen y cancelación. Resumen independiente: sin fecha ni aerolínea; los filtros del cubo no se aplican y sus totales no se concilian con él.

## Aeropuertos · volumen, puntualidad y cancelación

**Variables:** flights (X); otp (Y, %); cancel (tamaño, %).

**Justificación:** La dispersión compara escala y servicio; el área de burbuja aumenta con la tasa de cancelación.

**Interpretación:** FLL — Fort Lauderdale Hollywood International Airport presenta la menor puntualidad del resumen mostrado: 73.8%. Priorizar su diagnóstico junto con volumen y cancelación. Resumen independiente: sin fecha ni aerolínea; los filtros del cubo no se aplican y sus totales no se concilian con él.

## Aerolíneas · escala y puntualidad

**Variables:** Airline; ops (X); OTP (Y, %); cancelRate (tamaño, %).

**Justificación:** Permite localizar operadores con gran exposición y menor puntualidad. Una asociación no demuestra causalidad.

**Interpretación:** EM — Empire Airlines lidera con 89.29% (N=112); B6 — JetBlue Airways registra 71.71% (N=1,282,002). Investigar la mezcla de rutas y períodos: el ranking no ajusta confusores. Soporte mínimo: 30 operaciones. La escala no demuestra resiliencia causal.

## Ranking de puntualidad por aerolínea

**Variables:** Airline (categoría); Σontime / Σops (%).

**Justificación:** Las barras ordenadas facilitan comparaciones. Son tasas ponderadas por operaciones; no promedios simples de porcentajes.

**Interpretación:** EM — Empire Airlines lidera con 89.29% (N=112); B6 — JetBlue Airways registra 71.71% (N=1,282,002). Investigar la mezcla de rutas y períodos: el ranking no ajusta confusores. Soporte mínimo: 30 operaciones.

## Minutos por causa · solo registros conciliados

**Variables:** carrierDelay, weatherDelay, nasDelay, secDelay, lateAirDelay (minutos).

**Justificación:** Comparar minutos identifica focos de intervención en el subconjunto consistente. Se excluyen filas cuya suma de causas no coincide con sumDelayMin (tolerancia 1 minuto).

**Interpretación:** Aeronave previa concentra 39.03% de los minutos conciliados. Priorizar el diagnóstico de esa causa. Se excluyen 139 filas; cobertura de operaciones: 92.44%. El hallazgo solo describe el subconjunto válido, no todo el universo.

## Recomendaciones y límites

1. Conciliar causas y estados sin clasificar con el productor del dataset.
2. Priorizar revisión operativa de julio y de operadores con menor OTP, controlando diferencias de cobertura y mezcla de rutas.
3. Usar comparaciones del mismo mes para años incompletos.
4. Solicitar microdatos con fecha, aeropuerto, estado, hora y banderas de incidencias antes de construir análisis conjunto semanal, causal o predictivo.
5. Validar el resumen independiente de hubs antes de asignar recursos.
