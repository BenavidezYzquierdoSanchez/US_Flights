# Preguntas, variables, tareas y decisiones

| Pregunta analítica | Variables | Tarea y gráfico | Decisión |
|---|---|---|---|
| ¿Cómo cambia la puntualidad entre años? | Year, ontime, ops | Comparar: línea anual | Revisar deterioros con cobertura comparable |
| ¿Qué proporción tiene cada estado operativo? | ontime, delayed15, cancel, divert, residuo | Composición: barras | Dimensionar incidentes y revisar clasificaciones |
| ¿Qué radio registra menor OTP? | Haul, ontime, ops | Comparar: barras | Revisar mezcla de rutas |
| ¿Cuándo se registraron los mínimos mensuales? | Year-Month, ontime, ops | Tendencia: línea | Priorizar revisión de períodos |
| ¿Qué meses concentran menor puntualidad? | Month, ontime, ops | Estacionalidad: línea | Planificar revisión estacional con cautela |
| ¿Con qué precisión se compara OTP? | Airline, ontime, ops | Incertidumbre: barras Wilson | Distinguir volumen y precisión de modelo |
| ¿Qué horarios tienen menor demora resumida? | hour_block, avg_delay | Perfil: línea independiente | Investigar origen y denominador |
| ¿Dónde se ubican hubs con menor OTP? | Lat, Lon, otp, flights | Geografía: mapa de puntos | Priorizar diagnóstico local |
| ¿Qué hubs combinan volumen y cancelación? | flights, otp, cancel | Relación: burbujas | Revisar exposición operativa |
| ¿Qué operadores combinan escala y menor OTP? | Airline, ops, OTP, cancelRate | Relación: dispersión | Seleccionar operadores para diagnóstico |
| ¿Qué operadores lideran OTP? | Airline, ontime, ops | Ordenar: ranking de barras | Comparar servicio sin atribuir causalidad |
| ¿Qué causas acumulan más minutos conciliados? | Cinco causas y CauseValid | Comparar: barras | Priorizar diagnóstico de causas válidas |
