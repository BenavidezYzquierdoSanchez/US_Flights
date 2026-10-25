"""Regenera exportaciones, documentación, HTML autónomo y notebook."""
import hashlib,html,json,platform
from pathlib import Path
import pandas as pd
import plotly
import streamlit
from plotly.offline import get_plotlyjs
from analytics import *
from charts import *
from project_context import project_context,to_html,to_markdown
from ui_design import ICONS,NAV_ICONS,CHART_ICONS,VIEW_GRAPHS,HEIGHTS,KPI_SPECS,KPI_CLASSES,icon
from labels import CARRIERS,AIRPORTS
from methodology import render_cards
from conclusions import conclusions,render_conclusions
import base64

payload,d=load_data();a=audit(d,payload);m=metrics(d)
(ROOT/'data_vuelos_2021_2026_con_nombres.json').write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8')
context=project_context(d,payload)
(ROOT/'docs/MARCO_PROYECTO_2021_2026.md').write_text(to_markdown(context),encoding='utf-8')
(ROOT/'data/project_context.json').write_text(json.dumps(context,ensure_ascii=False,indent=2),encoding='utf-8')
for folder in ['data','docs','web','powerbi']: (ROOT/folder).mkdir(exist_ok=True)
(ROOT/'data/audit.json').write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding='utf-8')
d.to_csv(ROOT/'data/vuelos_auditados.csv',index=False,encoding='utf-8-sig')
d.loc[~d.CauseValid].to_csv(ROOT/'data/causas_no_conciliadas.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(payload['hubs']).to_csv(ROOT/'data/hubs_resumen.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(payload['hourly']).to_csv(ROOT/'data/horarios_resumen.csv',index=False,encoding='utf-8-sig')

kpis=[
('Operaciones','Σops','vuelos representados','Contextual','Sin meta'),
('Puntualidad OTP','100 × Σontime / Σops','%','↑','80%: referencia interna, no norma oficial'),
('Demora ≥15','100 × Σdelayed15 / Σops','%','↓','Sin meta validada'),
('Demora ≥60','100 × Σdelayed60 / Σops','%','↓','Subconjunto de demora ≥15'),
('Demora media condicionada','ΣsumDelayMin / Σdelayed15','min / llegada demorada','↓','Según semántica declarada en HTML; confirmar con microdatos'),
('Cancelación','100 × Σcancel / Σops','%','↓','Sin meta validada'),
('Desvíos','100 × Σdivert / Σops','%','↓','Sin meta validada'),
('Cobertura de causas','100 × Σops con CauseValid / Σops','%','↑','100% deseable como calidad de datos')]
method='''# Metodología y decisiones de diseño

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
'''
(ROOT/'docs/METODOLOGIA.md').write_text(method,encoding='utf-8')

matrix='| Pregunta analítica | Variables | Tarea y gráfico | Decisión |\n|---|---|---|---|\n'
questions=[
('¿Cómo cambia la puntualidad entre años?','Year, ontime, ops','Comparar: línea anual','Revisar deterioros con cobertura comparable'),
('¿Qué proporción tiene cada estado operativo?','ontime, delayed15, cancel, divert, residuo','Composición: barras','Dimensionar incidentes y revisar clasificaciones'),
('¿Qué radio registra menor OTP?','Haul, ontime, ops','Comparar: barras','Revisar mezcla de rutas'),
('¿Cuándo se registraron los mínimos mensuales?','Year-Month, ontime, ops','Tendencia: línea','Priorizar revisión de períodos'),
('¿Qué meses concentran menor puntualidad?','Month, ontime, ops','Estacionalidad: línea','Planificar revisión estacional con cautela'),
('¿Con qué precisión se compara OTP?','Airline, ontime, ops','Incertidumbre: barras Wilson','Distinguir volumen y precisión de modelo'),
('¿Qué horarios tienen menor demora resumida?','hour_block, avg_delay','Perfil: línea independiente','Investigar origen y denominador'),
('¿Dónde se ubican hubs con menor OTP?','Lat, Lon, otp, flights','Geografía: mapa de puntos','Priorizar diagnóstico local'),
('¿Qué hubs combinan volumen y cancelación?','flights, otp, cancel','Relación: burbujas','Revisar exposición operativa'),
('¿Qué operadores combinan escala y menor OTP?','Airline, ops, OTP, cancelRate','Relación: dispersión','Seleccionar operadores para diagnóstico'),
('¿Qué operadores lideran OTP?','Airline, ontime, ops','Ordenar: ranking de barras','Comparar servicio sin atribuir causalidad'),
('¿Qué causas acumulan más minutos conciliados?','Cinco causas y CauseValid','Comparar: barras','Priorizar diagnóstico de causas válidas')]
for q,v,t,de in questions:matrix+=f'| {q} | {v} | {t} | {de} |\n'
(ROOT/'docs/MATRIZ_ANALITICA.md').write_text('# Preguntas, variables, tareas y decisiones\n\n'+matrix,encoding='utf-8')
kpitable='| KPI | Fórmula | Unidad | Dirección | Referencia |\n|---|---|---|---|---|\n'
for row in kpis:kpitable+='| '+' | '.join(row)+' |\n'
(ROOT/'docs/DICCIONARIO_KPI.md').write_text('# Diccionario de KPI\n\nFrecuencia: actualización por cada carga del JSON; fecha de observación mensual para el cubo. No hay refresco automático del origen. Todas las divisiones sin denominador devuelven vacío.\n\n'+kpitable,encoding='utf-8')

results='# Hallazgos e interpretaciones de la carga inicial\n\nLos resultados siguientes corresponden al archivo completo; las aplicaciones recalculan la narrativa al filtrar.\n\n'
for key,section,title,variables,why in CATALOG:
    f,n=make_chart(key,d,payload)
    results+=f'## {title}\n\n**Variables:** {variables}.\n\n**Justificación:** {why}\n\n**Interpretación:** {n}\n\n'
results+='## Recomendaciones y límites\n\n1. Conciliar causas y estados sin clasificar con el productor del dataset.\n2. Priorizar revisión operativa de julio y de operadores con menor OTP, controlando diferencias de cobertura y mezcla de rutas.\n3. Usar comparaciones del mismo mes para años incompletos.\n4. Solicitar microdatos con fecha, aeropuerto, estado, hora y banderas de incidencias antes de construir análisis conjunto semanal, causal o predictivo.\n5. Validar el resumen independiente de hubs antes de asignar recursos.\n'
(ROOT/'docs/HALLAZGOS.md').write_text(results,encoding='utf-8')
pd.DataFrame([{'KPI':k,'Valor':v} for k,v in m.items()]).to_csv(ROOT/'data/kpi_referencia_python.csv',index=False)

# HTML autónomo: datos, librería de gráficos y geometría incluidos.
style=(ROOT/'web/style.css').read_text(encoding='utf-8').split('/* APP EXTRAS */')[0]
style+='\n/* APP EXTRAS */\n.card{margin-bottom:20px}.kpi{min-height:112px}.interp{line-height:1.7}input{background:#10192b;color:#e8eef8;border:1px solid #35465e;padding:7px;border-radius:6px;width:100%}pre{white-space:pre-wrap;line-height:1.7;color:#c5d0dc}button:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid #2ee6a6;outline-offset:3px}.plot:empty{display:none}@media print{.sidebar{display:none}.shell{display:block}.card{break-inside:avoid}}'
style+='\n.kpis{grid-template-columns:repeat(4,minmax(0,1fr))}.kpi .v{font-size:clamp(22px,2vw,32px)}.sidebar-actions button{background:#121c30;color:#d5deea;border:1px solid rgba(148,163,184,.3);border-radius:10px;padding:10px 12px;font:inherit;font-size:12px;cursor:pointer}#export{border-color:#2ec4b6;color:#2ec4b6}.sidebar-actions label{font-size:12px;color:#8b97ab}.plot{align-self:stretch}@media(max-width:1050px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.kpis{grid-template-columns:1fr}}'
style+='\n'+(ROOT/'web/project.css').read_text(encoding='utf-8')
style+='\n'+(ROOT/'web/kpi.css').read_text(encoding='utf-8')
style+='\n'+(ROOT/'web/methodology.css').read_text(encoding='utf-8')+'\n'+(ROOT/'web/leaflet.css').read_text(encoding='utf-8')
font=ROOT/'web/fonts/Manrope.ttf'
font_styles=''
if font.exists():font_styles='\n@font-face{font-family:Manrope;src:url(data:font/ttf;base64,'+base64.b64encode(font.read_bytes()).decode()+') format("truetype");font-weight:200 800;font-display:swap;}'
(ROOT/'web/font.css').write_text(font_styles)
style+=font_styles
(ROOT/'web/style.css').write_text(style)
safe=lambda x:json.dumps(x,ensure_ascii=False).replace('</','<\\/')
selectors=''.join(f'<label class="f">{label}<select id="{key}" aria-label="{label}"></select></label>' for key,label in [('Year','Año'),('Month','Mes'),('Airline','Aerolínea'),('Haul','Radio')])
nav=''.join(f'<button data-view="{s}">{icon(NAV_ICONS[s],"nav-icon")}{s}</button>' for s in ['Panorama','Estacionalidad','Geografía','Aerolíneas','Marco del proyecto','Metodología','Conclusiones'])
body=f'''<div class="shell"><aside class="sidebar"><div class="brand"><strong>US_Flights</strong><span>Puntualidad aérea</span></div><nav class="side">{nav}</nav><div class="filters-title">Filtros del cubo mensual</div><div class="filters">{selectors}<label class="f">Soporte mínimo (operaciones)<input id="support" type="number" min="30" step="10" value="30"></label><label class="f">Referencia interna OTP (%)<input id="target" type="range" min="0" max="100" value="80"></label><label class="f">Aeropuerto · resumen independiente<select id="airport"></select></label></div><div class="sidebar-actions"><button id="reset">Restablecer filtros</button><button id="export">Exportar CSV filtrado</button><label>Cargar otro JSON<input type="file" accept=".json" id="file"></label></div></aside><main class="content"><div class="top"><div><h1>Puntualidad aérea de EE. UU.</h1><p class="lede">Cubo agregado suministrado · 2021-01 a 2026-05 · 4 vistas analíticas</p></div><span class="status-badge">Datos integrados · sin instalación</span></div><div class="live" id="quality" role="status"></div><div class="kpis" id="kpis"></div><h2 id="heading">Panorama</h2><p class="live" id="scope"></p><div id="plots"></div><section id="methodology" hidden><div class="card"><h3>Metodología y alcance</h3><pre style="padding:20px">{html.escape(method)}</pre></div></section><footer>US_Flights · Tasas calculadas como cocientes de sumas · Referencia interna, sin certificación DOT</footer></main></div>'''
body=body.replace('<p class="lede">','<p class="lede" id="coverage">')
old='<section id="methodology" hidden><div class="card"><h3>Metodología y alcance</h3><pre style="padding:20px">'+html.escape(method)+'</pre></div></section>'
body=body.replace(old,'<section id="methodology" hidden>'+render_cards(d,payload)+'</section>')
body=body.replace('Restablecer filtros</button>',icon('reset','action-icon')+'Restablecer filtros</button>').replace('Exportar CSV filtrado</button>',icon('download','action-icon')+'Exportar CSV filtrado</button>')
body=body.replace('<label>Cargar otro JSON', '<button id="fullscreen">'+icon('expand','action-icon')+'Pantalla completa</button><label>'+icon('document','action-icon')+'Cargar otro JSON')
body=body.replace('<section id="methodology"', '<section id="project-context" hidden>'+to_html(context)+'</section><section id="methodology"')
body=body.replace('<footer>','<section id="conclusions" hidden>'+render_conclusions(d,payload)+'</section><footer>')
data_tags=''.join(f'<script type="application/json" id="{name}">{safe(value)}</script>' for name,value in [('dataset',payload),('coords',json.loads((ROOT/'data/airport_coords.json').read_text(encoding='utf-8'))),('catalog',CATALOG),('icons',ICONS),('names',dict(carriers=CARRIERS,airports=AIRPORTS)),('ui-config',dict(charts=CHART_ICONS,views=VIEW_GRAPHS,heights=HEIGHTS,kpis=KPI_SPECS,classes=KPI_CLASSES))])
head='<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>US_Flights · Análisis e interpretación</title>'
topo_path=ROOT/'data/usa_110m.json'
topo=f'<script>window.PlotlyGeoAssets={{topojson:{{usa_110m:{topo_path.read_text(encoding='utf-8')}}}}};</script>' if topo_path.exists() else ''
js=(ROOT/'web/dashboard.js').read_text(encoding='utf-8')
runtime_js=(ROOT/'web/leaflet.js').read_text(encoding='utf-8')+'\n'+(ROOT/'web/real_map.js').read_text(encoding='utf-8')+'\n'+js
standalone=f'<!doctype html><html lang="es"><head>{head}<style>{style}</style><script>{get_plotlyjs()}</script>{topo}</head><body>{body}{data_tags}<script>{runtime_js}</script></body></html>'
(ROOT/'dashboard_US_Flights.html').write_text(standalone,encoding='utf-8')
(ROOT/'web/plotly.min.js').write_text(get_plotlyjs())
modular=f'<!doctype html><html lang="es"><head>{head}<link rel="stylesheet" href="style.css"><script src="plotly.min.js"></script><script src="leaflet.js"></script><script src="real_map.js"></script>{topo}</head><body>{body}{data_tags}<script src="dashboard.js"></script></body></html>'
(ROOT/'web/index.html').write_text(modular,encoding='utf-8')

# Notebook reproducible; las figuras usan exactamente el mismo motor de Streamlit.
import nbformat as nb
cells=[nb.v4.new_markdown_cell('# US_Flights · análisis reproducible\n\nEjecutar desde la carpeta extraída. No se usan microdatos ni ejemplos de demostración. Las interpretaciones y variables acompañan cada figura.'),
nb.v4.new_code_cell('from pathlib import Path\nimport sys\nROOT = Path.cwd()\nif not (ROOT / "analytics.py").exists():\n    raise RuntimeError("Abre este notebook desde la carpeta US_Flights")\nsys.path.insert(0, str(ROOT))\nfrom analytics import *\nfrom charts import *\npayload, df = load_data()\naudit(df, payload)'),
nb.v4.new_markdown_cell('## Métricas y control de calidad\n\nLas tasas son cocientes de sumas. Se conservan residuos y se excluyen las causas no conciliadas solo de su propia distribución.'),
nb.v4.new_code_cell('import pandas as pd\npd.DataFrame([metrics(df)])'),
nb.v4.new_code_cell('df.loc[~df.CauseValid, ["Year", "Month", "Airline", "CauseGap"]].head(10)')]
cells.append(nb.v4.new_markdown_cell('## KPI con iconos y catálogos completos\n\nLas tarjetas y etiquetas se generan con los mismos componentes de la versión final del dashboard.'))
cells.append(nb.v4.new_code_cell('from notebook_ui import show, panel, map_view\nfrom ui_design import kpis_html\nshow(panel(kpis_html(metrics(df))))\ndf[["Airline", "AirlineName", "AirlineLabel"]].drop_duplicates().sort_values("Airline")'))
for key,section,title,variables,why in CATALOG:
    cells.append(nb.v4.new_markdown_cell(f'## {title}\n\n**Variables:** {variables}\n\n**Justificación:** {why}'))
    cells.append(nb.v4.new_code_cell(f'figure, interpretation = make_chart("{key}", df, payload)\nprint(interpretation)\nfigure.show() if figure is not None else None'))
cells.append(nb.v4.new_markdown_cell('## Mapa real de calles y satélite\n\nRequiere Internet para el fondo cartográfico. La opción sin conexión usa geometría local. Ambos muestran el resumen independiente de aeropuertos. Confía en el notebook para ejecutar los contenidos interactivos.'))
cells.append(nb.v4.new_code_cell('map_figure, map_note = make_chart("map", df, payload)\nprint(map_note)\nshow(map_view(map_figure, payload["hubs"]))'))
cells.append(nb.v4.new_markdown_cell('## Marco del proyecto actualizado\n\nSíntesis del documento AeroPulse con referencias calculadas para la base completa 2021–2026.'))
cells.append(nb.v4.new_code_cell('from project_context import project_context, to_markdown\nprint(to_markdown(project_context(df, payload)))'))
cells.append(nb.v4.new_markdown_cell('## Metodología en doce tarjetas\n\nObjetivo, cobertura, nombres, KPI, filtros, calidad, comparación temporal, incertidumbre, mapas, límites, diseño y trazabilidad.'))
cells.append(nb.v4.new_code_cell('from methodology import render_cards\nshow(panel(render_cards(df, payload)))'))
cells.append(nb.v4.new_markdown_cell('## Cuatro conclusiones y recomendaciones\n\nSíntesis de la base completa, sin aplicar filtros de las vistas.'))
cells.append(nb.v4.new_code_cell('from conclusions import conclusions\nfor card in conclusions(df,payload):\n    print(card["title"])\n    print("Conclusión:",card["conclusion"])\n    print("Recomendación:",card["recommendation"],"\\n")'))
cells.append(nb.v4.new_code_cell('from conclusions import render_conclusions\nshow(panel(render_conclusions(df, payload)))'))
cells.append(nb.v4.new_markdown_cell('## Reproducibilidad e IA\n\nConsultar docs/METODOLOGIA.md, HALLAZGOS.md y VALIDACION.md. Los intervalos Wilson son de modelo; no incorporan dependencia ni sesgo. No hay datos para un cruce día×hora. No se publicó la app ni se verificó el proyecto en Power BI Desktop.'))
notebook=nb.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})
# Ejecuta cada celda y captura salidas de texto y las figuras como MIME Plotly.
import contextlib,io
env={'__name__':'__main__'}
orig=go.Figure.show
import notebook_ui
orig_show_html=notebook_ui.show
def record_html(content):
    current.outputs.append(nb.v4.new_output('display_data',data={'text/html':content,'text/plain':'Panel interactivo del dashboard US_Flights'},metadata={}))
notebook_ui.show=record_html
def record(fig,*args,**kwargs):
    current.outputs.append(nb.v4.new_output('display_data',data={'application/vnd.plotly.v1+json':json.loads(fig.to_json()),'text/plain':repr(fig)},metadata={}))
go.Figure.show=record
try:
    count=0
    for current in notebook.cells:
        if current.cell_type!='code':continue
        count+=1;current.execution_count=count;current.outputs=[];buff=io.StringIO()
        with contextlib.redirect_stdout(buff):
            # Captura la última expresión para celdas de tabla/auditoría.
            import ast
            tree=ast.parse(current.source);tail=tree.body[-1] if tree.body else None
            if isinstance(tail,ast.Expr):
                tree.body=tree.body[:-1];exec(compile(tree,'<notebook>','exec'),env)
                value=eval(compile(ast.Expression(tail.value),'<notebook>','eval'),env)
                if value is not None:print(value)
            else:exec(current.source,env)
        if buff.getvalue():current.outputs.insert(0,nb.v4.new_output('stream',name='stdout',text=buff.getvalue()))
finally:
    go.Figure.show=orig
    notebook_ui.show=orig_show_html
nb.write(notebook,ROOT/'analisis_US_Flights.ipynb')
pd.DataFrame([{'archivo':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (ROOT/'data').glob('*.json')]).to_csv(ROOT/'docs/hashes_fuentes.csv',index=False)
(ROOT/'docs/entorno.json').write_text(json.dumps({'python':platform.python_version(),'streamlit':streamlit.__version__,'pandas':pd.__version__,'plotly':plotly.__version__},indent=2))
print('HTML, notebook ejecutado, datos, auditoría y documentos generados.')
