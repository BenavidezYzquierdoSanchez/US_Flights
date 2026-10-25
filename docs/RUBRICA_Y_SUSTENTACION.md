# Correspondencia con la guía del proyecto integrador

| Requisito del PDF adjunto | Entrega | Estado |
|---|---|---|
| Problema, usuario y 3–5 decisiones | METODOLOGIA.md | Incluido: 5 decisiones |
| Mínimo 8 preguntas y matriz | MATRIZ_ANALITICA.md | Incluido: 12 preguntas |
| Mínimo 6 KPI documentados | DICCIONARIO_KPI.md | Incluido: 8 KPI |
| Modelo de datos y preparación | analytics.py; modelo Power BI; auditoría | Incluido |
| Wireframe y auditoría visual | METODOLOGIA.md; revisión interna del dashboard | Incluido como wireframe textual y revisión visual |
| Notebook reproducible | analisis_US_Flights.ipynb | Ejecutado |
| ≥5 gráficos justificados e interpretados | 12 gráficos en 4 vistas | Incluido |
| Incertidumbre | Wilson 95% por aerolínea | Incluido con supuestos |
| Temporal y geoespacial | Series y mapa de aeropuertos | Incluido con límites de cobertura |
| Streamlit desplegado | app.py y configuración | Implementado y probado localmente; despliegue público pendiente |
| Power BI y medidas comparadas con Python | PBIP, DAX, consulta y CSV de referencia | Archivos y paridad de datos comprobados; ejecución Desktop/DAX pendiente |
| Vista comparativa Tableau | Fuera de las tres plataformas solicitadas | No incluida |
| Matriz de arquitectura | Tabla siguiente | Incluida |
| Auditoría crítica de IA | METODOLOGIA.md | Incluida |
| Repositorio operativo | Paquete de fuentes | No se creó un repositorio remoto |
| Defensa ejecutiva 12–15 minutos | Guion siguiente | Incluido como apoyo; no equivale a una presentación de diapositivas |

## Matriz de decisión de arquitectura

| Criterio | HTML/CSS/JavaScript | Streamlit | Power BI |
|---|---|---|---|
| Uso recomendado | Distribución autónoma y consulta rápida | Análisis reproducible y extensible en Python | Reporte institucional con modelo semántico |
| Ejecución | Navegador; archivo local | Servidor Python local o alojamiento | Desktop; publicación opcional en servicio |
| Datos en esta entrega | JSON integrado | JSON local con pandas | Instantánea M comprimida de tablas auditadas |
| Narrativa | JavaScript recalcula textos | Python recalcula textos | Medidas DAX de texto por gráfico |
| Modelo | Arreglos y agrupaciones | DataFrames y funciones | Dimensiones, relaciones y medidas |
| Interacciones | Filtros globales y aeropuerto independiente | Filtros globales y aeropuerto independiente | Segmentadores por página y selección de visuales |
| Actualización | Regenerar o cargar JSON compatible | Reemplazar JSON y regenerar auditoría | Regenerar proyecto o adaptar Power Query |
| Compartir | Archivo sin instalación | URL tras desplegar | PBIP/PBIX; permisos/licencias según publicación |
| Límite actual | No hay backend ni control de acceso | No se ha desplegado | Desktop no disponible en este entorno |

Decisión propuesta: Streamlit como motor analítico por su trazabilidad Python; HTML como entrega portátil; Power BI como alternativa institucional. Elegir según usuarios, mantenimiento y forma de distribución; ninguna plataforma resuelve las carencias del dataset.

## Guion de sustentación · 14 minutos

1. **0:00–1:30 · Problema y decisiones.** Presentar al responsable de operaciones y las cinco decisiones; definir OTP con su denominador.
2. **1:30–3:30 · Datos y calidad.** Mostrar granularidad, meses cubiertos, 139 filas de causas inconsistentes, 7,959 operaciones sin categoría y resúmenes desconectados. Explicar por qué se retiró el cruce día×hora.
3. **3:30–5:00 · Panorama.** Explicar 79.34% de puntualidad global y el mix. Aclarar que 2026 no es un año completo.
4. **5:00–7:00 · Evidencia temporal.** Comparar meses equivalentes y discutir el mínimo de julio en la estacionalidad agregada. Señalar valores mensuales extremos que requieren cotejo.
5. **7:00–8:30 · Operadores e incertidumbre.** Mostrar ranking, N e intervalos Wilson. El operador EM tiene N=112: una tasa alta no prueba superioridad general.
6. **8:30–10:00 · Geografía.** Mostrar aeropuertos del resumen; explicar que no son un mapa estatal ni responden al filtro de año.
7. **10:00–11:30 · Causas y decisiones.** Priorizar diagnóstico de aeronave previa en el subconjunto conciliado; no extrapolar sin verificar las filas excluidas.
8. **11:30–13:00 · Comparación técnica.** Explicar cocientes de sumas, paridad HTML/Python, modelo Power BI y diferencias de representación de Wilson.
9. **13:00–14:00 · Recomendaciones y límites.** Cerrar con conciliación de datos, comparación de períodos equivalentes y necesidad de microdatos antes de análisis causal o predictivo.

## Preguntas de defensa

- ¿Por qué no promediar porcentajes? Porque los agregados tienen diferente número de operaciones; se calcula Σontime / Σops.
- ¿Por qué no filtrar hubs por aerolínea? No existe esa clave en el resumen; el cruce sería ficticio.
- ¿Por qué retirar el heatmap? No hay tabla conjunta día×hora; fabricarlo produciría evidencia inexistente.
- ¿Qué significa Wilson? Precisión de modelo bajo supuestos binomiales, no confiabilidad del dato ni predicción futura.
- ¿Por qué el 80%? Es una referencia interna ajustable, no una meta normativa confirmada.
- ¿Por qué conservar el residuo? Para mantener conciliación y trazabilidad sin inventar una clasificación.
