# Abrir el proyecto Power BI

1. Extrae el ZIP completo. Conserva juntas las carpetas US_Flights.Report y US_Flights.SemanticModel junto al archivo US_Flights.pbip.
2. En Power BI Desktop reciente abre US_Flights.pbip o US_Flights.Report/definition.pbir. Si tu versión no admite proyectos, habilita la característica correspondiente o actualiza Desktop.
3. Pulsa Actualizar: el modelo importa la instantánea de datos incluida en las consultas M comprimidas. No necesita una ruta de archivo, gateway, cuenta Kaggle ni credenciales del origen. No hay caché de datos precargada.
4. Revisa las siete páginas: Panorama, Estacionalidad, Geografía, Aerolíneas, Marco del proyecto, Metodología y Conclusiones. Las cuatro páginas analíticas incluyen ocho KPI con iconos, filtros sincronizados, soporte mínimo y referencia OTP ajustables, y lecturas por gráfico. Las tablas de interpretaciones permiten ampliar la columna si Desktop la presenta demasiado estrecha. Azure Maps puede requerir habilitación del administrador y conexión a Internet; la tabla geográfica sigue disponible sin fondo cartográfico.
5. Ejecuta consulta_validacion.dax en la vista de consultas DAX. Compara los nueve valores con kpi_referencia_python.csv (las tasas se convierten a escala 0-100 en la consulta). Tolerancia recomendada: 1e-8. Prueba además un mismo filtro de año, mes, aerolínea y radio en ambas plataformas.
6. Guarda como .pbix desde Desktop si necesitas ese formato. No se entrega un PBIX binario ni se ha abierto este proyecto en Desktop en este entorno.

## Qué está implementado
Modelo en model.bim (TMSL), datos embebidos mediante M, relaciones de una dirección desde Calendario/Aerolineas/Radios al cubo, DAX documentado, siete páginas con doce análisis (trece ubicaciones de gráficos), interpretaciones dinámicas y paleta original. Nombres completos para 22 aerolíneas y 35 aeropuertos; meses de Enero a Diciembre ordenados por número. Metodología: doce tarjetas. Conclusiones: cuatro tarjetas con sus recomendaciones. Marco y conclusiones describen la base completa 2021-2026, sin depender de los filtros de las páginas analíticas.

Hubs y Horarios están desconectados porque no tienen claves de fecha/aerolínea. Las tablas Causas y Estados son selectores de medidas SWITCH, intencionalmente desconectados. No conectarlas artificialmente por US.

## Diferencias de presentación
En Power BI el intervalo Wilson se muestra con tres series (OTP, límite inferior y límite superior) en un gráfico nativo. En HTML/Streamlit se usan barras de error. El mapa usa Azure Maps con coordenadas y volumen como tamaño; OTP y cancelación están en el tooltip. HTML/Streamlit codifican OTP con color. La equivalencia es de variables y métricas, no de identidad entre motores gráficos.

Los filtros de año, mes, aerolínea, radio y los dos controles se sincronizan entre las cuatro páginas analíticas. Aeropuerto solo afecta el resumen geográfico. La referencia admite enteros de 0 a 100; sin selección usa 80%. El soporte permite 30, 50, 100, 500, 1000, 5000, 10000, 50000, 100000 y 1000000 operaciones; sin selección usa 30. HTML/Streamlit permiten escribir otros soportes, mientras que Power BI usa estas opciones predefinidas. El estado del KPI OTP y las series de referencia siguen la selección. Los intervalos Wilson y rankings usan el soporte seleccionado. La validación de ejecución DAX y de renderizado en Desktop queda pendiente y debe realizarse antes de una entrega académica final.

## Actualizar los datos
El PBIP es una instantánea reproducible. Para otro JSON, reemplaza data/source.json y ejecuta python build_assets.py y python build_powerbi.py; cierra Desktop antes de regenerar. Alternativamente usa PowerQuery_fuente_local.m creando el parámetro RutaJSON y actualiza las dimensiones y los resúmenes respectivos. No hay actualización programada ni conexión automática a Kaggle.

Documentación de formato: https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report y https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset .
