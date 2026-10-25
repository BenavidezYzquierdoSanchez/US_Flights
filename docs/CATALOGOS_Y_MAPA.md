# Nombres y cartografía

Los códigos siguen siendo las claves de filtrado y relación. La base enriquecida añade AirlineName y AirlineLabel al cubo; AirportName y AirportLabel al resumen de hubs. Formato de presentación: código — nombre completo. Ningún conteo, minuto o porcentaje se modifica.

## Fuentes de nombres

- Aerolíneas: catálogo CARRIER_NAMES del HTML original suministrado (22 códigos).
- Aeropuertos: catálogo OurAirports, archivo airports.csv del repositorio primario https://github.com/davidmegginson/ourairports-data (35 códigos del resumen). Diccionario: https://ourairports.com/help/data-dictionary.html . Consulta: 25 de octubre de 2026. Son nombres descriptivos de referencia; no reconstruyen los cambios de denominación histórica durante 2021–2026.
- Coordenadas: archivo airport_coords.json del proyecto, conservado. Los nombres nuevos no alteran las ubicaciones ni las métricas del resumen.

Los códigos desconocidos de otros archivos se muestran como “Nombre no disponible” y no se emparejan por semejanza. En gráficos de dispersión se conservan códigos compactos junto a los puntos; el nombre completo aparece en el tooltip. Rankings y filtros muestran código y nombre completo.

## Mapa real

Se incluye Leaflet 1.9.4 localmente. La capa predeterminada usa cartografía de calles de Esri World Street Map. El control de capas permite cambiar a Esri World Imagery (satelital). La atribución se mantiene visible. No requiere clave API; las teselas necesitan Internet y están sujetas a la disponibilidad del proveedor. No se descargan teselas masivamente ni se incluyen en el paquete.

Los círculos corresponden a los 35 aeropuertos del resumen. Su color codifica OTP en escala 60–100 y su tamaño aumenta con operaciones. El popup muestra código, nombre, volumen, puntualidad y cancelación. El mapa no permite atribuir estos resultados a un año o aerolínea porque el resumen no incluye esas claves.

La opción Mapa sin conexión conserva el mapa vectorial local con los mismos aeropuertos. Si las teselas no responden, el dashboard cambia a esa alternativa e informa al usuario. La presencia de calles o imágenes de fondo no aporta datos adicionales de rendimiento.

## Metodología

Doce tarjetas de colores explican objetivo, cobertura, nombres, KPI, filtros, calidad, comparación temporal, incertidumbre, mapa, límites, diseño y reproducibilidad. Los detalles técnicos completos se conservan en docs/METODOLOGIA.md y en el desplegable de Streamlit.

## Power BI

Se agregaron las columnas de nombres a las tablas y se usan etiquetas completas en segmentadores, categorías y narrativas. La cartografía nativa sigue usando Azure Maps. También se añade una página Metodología con paneles temáticos. La apertura y ejecución en Desktop no se han verificado en este entorno.

Servicios comprobados: https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer y https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer . Se conserva la atribución Esri y los proveedores indicados por cada servicio. Se retiraron proveedores que entregaron avisos de acceso en lugar de cartografía.
