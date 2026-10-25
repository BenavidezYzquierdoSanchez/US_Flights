# Revisión de Power BI frente al dashboard actualizado

Se revisó el proyecto PBIP y se regeneró desde el mismo JSON y los mismos catálogos que el dashboard HTML. La comparación de la instantánea se hizo fila por fila, incluyendo dimensiones, conteos, minutos, etiquetas, banderas de calidad y operaciones sin clasificar.

## Contenido comprobado

| Elemento | Resultado |
|---|---|
| Páginas | Panorama, Estacionalidad, Geografía, Aerolíneas, Marco del proyecto, Metodología y Conclusiones |
| Datos | 3,344 agregados; 38,382,189 operaciones; enero de 2021 a mayo de 2026 |
| Aerolíneas | 22, con código y nombre completo |
| Aeropuertos | 35, con código y nombre completo y coordenadas |
| Filtro de meses | Enero a Diciembre, ordenado por número de mes |
| KPI | Ocho por página analítica, con iconos y colores asociados |
| Gráficos | Doce análisis en trece ubicaciones, con variables, propósito e interpretación |
| Marco del proyecto | Problema, usuario, decisiones, preguntas y referencias actualizadas |
| Metodología | Doce paneles con colores |
| Conclusiones | Cuatro paneles con conclusión y recomendación |

## Diferencias corregidas

- Se agregaron controles nativos para referencia OTP y soporte mínimo; las medidas, los rankings, el intervalo Wilson y el estado del KPI de puntualidad siguen esas selecciones.
- Se sincronizaron los filtros de año, mes, aerolínea, radio y ambos controles entre las cuatro vistas analíticas. El aeropuerto mantiene un alcance independiente.
- Se actualizaron colores de iconos y fondos de los KPI para respetar la paleta del HTML.
- Se protegió el cálculo Wilson cuando el denominador es cero.
- Se usan nombres completos de meses también en el gráfico mensual y su narrativa.
- Se agregó una tabla de aeropuertos en Geografía para consultar datos cuando el fondo cartográfico no esté disponible.
- Se corrigieron las instrucciones para incluir los siete módulos y el CSV de referencia dentro del paquete exclusivo de Power BI.

## Diferencias propias de las plataformas

Power BI usa visuales nativos y Azure Maps; HTML y Streamlit usan Plotly y Leaflet con cartografía de Esri. En Power BI se puede cambiar el estilo del mapa desde sus controles cuando esté habilitado el servicio. El mapa vectorial sin conexión continúa en HTML/Streamlit; Power BI conserva la tabla geográfica como alternativa sin fondo. Los intervalos Wilson son tres series en Power BI y barras de error en las otras dos versiones.

Power BI usa Segoe UI y fondos de tarjetas planos; el HTML incorpora Manrope y degradados CSS. El soporte de Power BI se selecciona entre valores predefinidos, mientras que HTML/Streamlit permiten escribirlo. La equivalencia comprobada es de datos, métricas, módulos y organización; no implica identidad de cada píxel ni del motor cartográfico.

## Abrir y comprobar en Desktop

1. Extraer todo el archivo ZIP en una carpeta.
2. Abrir US_Flights.pbip y pulsar Actualizar. No mover por separado las carpetas Report y SemanticModel.
3. Revisar las siete páginas y probar los filtros sincronizados. Sin selección de parámetros, la referencia es 80% y el soporte es 30.
4. Ejecutar consulta_validacion.dax y comparar con kpi_referencia_python.csv. Las tasas de esa consulta se expresan en escala 0–100 para compararlas con Python.
5. Revisar mapas, intervalos, etiquetas largas y textos; guardar como PBIX si se necesita ese formato.

**Límite de esta revisión:** se comprobaron archivos, referencias, límites del lienzo, recursos, esquemas y coincidencia de datos. No se dispone aquí de Power BI Desktop ni de su motor DAX. La apertura, el refresco nativo, el comportamiento de sincronización y el renderizado de visuales necesitan verificación final en Desktop. No se entrega un PBIX binario.

El resultado automático de la auditoría está en revision_dashboard.json. Esta revisión no certifica la procedencia de los microdatos originales.
