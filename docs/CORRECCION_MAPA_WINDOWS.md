# Corrección del mapa en Windows

El error `UnicodeDecodeError: charmap` ocurría al leer JavaScript UTF-8 con la codificación predeterminada cp1252. Se añadió `encoding="utf-8"` en las lecturas de recursos del mapa, estilos y catálogos, y en las herramientas de construcción y validación.

Para una instalación existente, detener Streamlit con Ctrl+C, copiar los archivos de la carpeta US_Flights del parche sobre la carpeta local del proyecto y volver a iniciar `python -m streamlit run app.py` con el intérprete del entorno instalado. No es necesario reinstalar dependencias por esta corrección.

El mapa de calles y satélite requiere Internet; la vista vectorial está incluida como alternativa.

Prueba de regresión: `python tests/verify_windows_encoding.py`. Exige codificación explícita al leer recursos del proyecto y genera el mapa de los 35 aeropuertos.
