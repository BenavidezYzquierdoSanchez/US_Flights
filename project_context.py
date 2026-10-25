"""Marco de diseño AeroPulse adaptado al cubo agregado 2021-2026."""
import html
from analytics import metrics,grouped,audit,fmt

def project_context(d,payload):
    a=audit(d,payload);m=metrics(d)
    annual=grouped(d,'Year')
    annual['months']=annual.Year.map(d.groupby('Year').Month.nunique())
    title='Marco del proyecto'
    sections=[
      {'title':'Problema y usuario objetivo','paragraphs':[
        'Los promedios de puntualidad ocultan diferencias entre períodos, operadores y radios de vuelo. El proyecto permite localizar deterioros del servicio y dimensionar incidencias antes de proponer cambios de capacidad, reserva de aeronaves o criterios contractuales.',
        'Usuario principal: analista de red e investigación de operaciones de una aerolínea. La evidencia apoya un diagnóstico operativo; la asignación final requiere información sobre rutas, recursos, costos y conexiones.']},
      {'title':'Objetivo y alcance actualizado','paragraphs':[
        'Comparar puntualidad, demoras, cancelaciones y desvíos en los agregados suministrados de 2021 a 2026, identificar segmentos para revisión y comunicar las limitaciones de cada fuente.',
        'El marco resume la base completa. Los KPI superiores siguen el filtro activo del dashboard; las cifras de referencia y el resumen anual de este módulo usan todos los registros. 2026 es un período parcial y no se compara como un año completo. La referencia OTP de 80% es interna, no una meta normativa verificada.']},
      {'title':'Cinco decisiones y evidencia necesaria','headers':['Decisión','Evidencia disponible','Condición para actuar'],'rows':[
        ['Revisar holgura operativa en períodos críticos','OTP y demoras por año y mes; contrastar el mismo mes entre años','Diagnosticar rutas, duración y costos antes de modificar block-time.'],
        ['Priorizar diagnóstico de hubs con volumen alto y OTP bajo','Resumen independiente de aeropuertos: flights, otp y cancel','No asignar reservas por mes o aerolínea: el resumen no contiene esas claves.'],
        ['Evaluar políticas de conexiones y rotación','Perfil horario global y OTP por radio, analizados por separado','No establecer conexiones mínimas de 45 minutos ni un corte a las 15:00: falta el cruce hora × radio × conexión.'],
        ['Gestionar cancelación y demora como incidencias distintas','Tasas sobre ops y composición de estados con residuo explícito','No tratar cancelados como demora cero ni sumar demora ≥60 a demora ≥15.'],
        ['Evaluar operadores por servicio y exposición','OTP, cancelación, desvíos, operaciones e incertidumbre Wilson','Controlar mezcla de rutas y períodos antes de contratar o sancionar.']]},
      {'title':'Preguntas que conectan el marco con las vistas','headers':['Pregunta','Variables','Vista y tarea'],'rows':[
        ['¿Cómo cambia OTP entre períodos equivalentes?','Year, Month, ontime, ops','Panorama y Estacionalidad · comparación temporal'],
        ['¿Qué meses requieren un diagnóstico prioritario?','Period, ontime, delayed15, ops','Estacionalidad · localizar mínimos y variación'],
        ['¿Predomina demora, cancelación o desvío?','delayed15, cancel, divert, Unclassified','Panorama · composición excluyente'],
        ['¿Qué radio presenta menor puntualidad?','Haul, ontime, ops','Panorama · comparación categórica'],
        ['¿Qué aeropuertos combinan escala y menor OTP?','Hubs: code, flights, otp, cancel; coordenadas','Geografía · localización y dispersión'],
        ['¿Qué operadores combinan menor OTP y más cancelación?','Airline, ontime, ops, cancel','Aerolíneas · ranking y dispersión'],
        ['¿Qué causa acumula más minutos conciliados?','Cinco causas, sumDelayMin, CauseValid','Aerolíneas · comparar minutos válidos'],
        ['¿Qué precisión tiene la comparación por operador?','Airline, ontime, ops','Estacionalidad · intervalo Wilson 95%']]},
      {'title':'Datos y modelo que sí están disponibles','headers':['Componente','Granularidad o campos','Regla de uso'],'rows':[
        ['Hecho principal','Year × Month × Airline × OriginState × Haul','Cada fila es un agregado; no un vuelo-día.'],
        ['Dimensiones conectadas','Calendario mensual, Aerolineas y Radios','Filtran conteos y minutos del cubo; tasas como cocientes de sumas.'],
        ['Origen geográfico','OriginState = US en todas las filas','No existe detalle estatal para construir un coroplético de desempeño.'],
        ['Resumen de hubs','code, flights, otp, cancel; coordenadas de referencia','Fuente desconectada del cubo: sin fecha ni aerolínea.'],
        ['Resumen horario','hour_block y avg_delay','No hay denominador ni cruce con radio o día.'],
        ['Microdatos ausentes','FlightDate, ArrDelay individual, Distance y conexiones','No se reconstruyen ni se sustituyen con valores artificiales.']]},
      {'title':'Control de calidad y lectura responsable','paragraphs':[
        'Se conservan las operaciones que no concilian con las categorías de resultado como Unclassified. Las filas con causas inconsistentes se mantienen en los KPI generales y se excluyen únicamente del gráfico de causas, con tolerancia de un minuto por agregado.',
        'El resumen semanal contiene una única fila con el total de operaciones; no sustenta un patrón semanal. No hay tabla conjunta día × hora. Los límites de distancia de corto, medio y largo no están documentados en el JSON y no se importan del documento de 2025 como si fueran comprobados.',
        'Los intervalos Wilson del 95% expresan precisión bajo un modelo binomial. No miden sesgo, dependencia entre vuelos ni desempeño futuro. Una tasa alta con poco volumen no demuestra superioridad general.']},
      {'title':'Diseño visual y recorrido de lectura','headers':['Zona','Contenido','Propósito'],'rows':[
        ['Barra lateral','Cuatro vistas analíticas, Marco del proyecto y Metodología; filtros','Orientar la navegación y definir el corte del cubo.'],
        ['Encabezado','Cobertura temporal, aviso de calidad y ocho KPI','Comunicar el alcance y la magnitud antes del detalle.'],
        ['Gráficos','Tendencias, composición, comparación, mapa e incertidumbre','Responder preguntas; acompañar cada figura con variables, propósito e interpretación.'],
        ['Contexto','Problema → evidencia → decisión → limitación','Permitir la sustentación académica y la revisión técnica.'],
        ['Color y accesibilidad','Fondo #070d18; tarjetas #10192b; acento #2ee6a6; turquesa #2ec4b6; dorado #f5b942; alerta #f07178; azul #5b8def','Mantener la paleta original; comunicar estado también mediante texto, etiquetas y leyendas.']]},
      {'title':'Qué se actualizó del documento de 2025','paragraphs':[
        'Se conserva la lógica de problema, usuario, decisiones, preguntas y jerarquía visual de AeroPulse. El período pasa a 2021–2026 y todas las cifras de referencia de este módulo proceden del JSON actual.',
        'La descripción de 12 CSV, 40 columnas y 7,001,619 filas corresponde a un extracto descrito en el documento anterior; no define los archivos disponibles en este proyecto. La unidad actual es el agregado mensual. Los 7,736,770 de 2025 se recalculan desde este cubo y no se presentan como una validación independiente de cifras oficiales.',
        'La recomendación de restringir conexiones de 45 minutos después de las 15:00 se conserva únicamente como pregunta de investigación, no como conclusión. El análisis por estado, día de semana o cruce radio-hora queda pendiente de microdatos.']}
    ]
    kpi_rows=[['Operaciones','Σops',fmt(m['ops'],0),'operaciones representadas'],
      ['Puntualidad OTP','100 × Σontime / Σops',fmt(m['otp'],2),'%'],
      ['Demora ≥15 min','100 × Σdelayed15 / Σops',fmt(m['delay15'],2),'%'],
      ['Demora ≥60 min','100 × Σdelayed60 / Σops',fmt(m['delay60'],2),'%'],
      ['Demora media condicionada','ΣsumDelayMin / Σdelayed15',fmt(m['avgDelay'],2),'min / llegada demorada'],
      ['Cancelación','100 × Σcancel / Σops',fmt(m['cancelRate'],2),'%'],
      ['Desvíos','100 × Σdivert / Σops',fmt(m['divertRate'],2),'%'],
      ['Cobertura de causas válidas','100 × Σops válidas / Σops',fmt(m['causeCoverage'],2),'% de operaciones']]
    baseline={'title':'Ocho KPI de referencia de la base completa','paragraphs':[f'Cobertura observada: {a["date_min"]} a {a["date_max"]}; {len(d):,} agregados y {a["months_observed"]} meses. Actualización por carga del JSON; frecuencia de observación mensual. Calidad: {a["invalid_cause_rows"]:,} filas excluidas del análisis de causas y {m["unclassified"]:,} operaciones sin categoría.'],
       'headers':['KPI','Fórmula','Valor','Unidad'],'rows':kpi_rows}
    annual_section={'title':'Evidencia anual recalculada 2021 a 2026','headers':['Año','Meses observados','Operaciones','OTP','Cancelación'],
       'rows':[[str(int(r.Year)),str(int(r.months)),fmt(r.ops,0),fmt(r.otp,2)+'%',fmt(r.cancelRate,2)+'%'] for r in annual.itertuples()],
       'paragraphs':['Los años completos y el período parcial de 2026 se identifican por meses observados. Las diferencias son descriptivas y pueden reflejar cambios de cobertura y composición; no prueban mejoras o deterioros causales.']}
    sections[2:2]=[baseline,annual_section]
    evidence=[]
    ref=d[d.Year==2025]
    if not ref.empty:
        g=grouped(ref,'Month');lo=g.loc[g.otp.idxmin()];hi=g.loc[g.otp.idxmax()];cancel=g.loc[g.cancelRate.idxmax()]
        evidence.append(f'En 2025, el menor OTP mensual es {lo.otp:.2f}% en el mes {int(lo.Month):02d}; el mayor es {hi.otp:.2f}% en el mes {int(hi.Month):02d}. La mayor tasa de cancelación mensual es {cancel.cancelRate:.2f}% en el mes {int(cancel.Month):02d}. Estos cortes orientan el diagnóstico temporal; no justifican por sí solos cambios de capacidad.')
    last=int(d.Year.max());prior=last-1
    common=sorted(set(d.loc[d.Year==last,'Month']) & set(d.loc[d.Year==prior,'Month']))
    if common:
        latest=metrics(d[(d.Year==last)&d.Month.isin(common)]);previous=metrics(d[(d.Year==prior)&d.Month.isin(common)])
        evidence.append(f'Comparación con meses coincidentes ({", ".join(f"{m:02d}" for m in common)}): OTP {prior} = {previous["otp"]:.2f}%; OTP {last} = {latest["otp"]:.2f}%; diferencia {latest["otp"]-previous["otp"]:+.2f} puntos porcentuales. Cancelación: {previous["cancelRate"]:.2f}% frente a {latest["cancelRate"]:.2f}%. La comparación iguala los meses, pero no controla la mezcla de operadores ni de radios.')
    sections.insert(4,{'title':'Hallazgos que orientan la priorización','paragraphs':evidence})
    return {'title':title,'source':'Adaptación del marco AeroPulse 2025 al JSON suministrado 2021–2026.','sections':sections}

def to_markdown(context):
    lines=['# '+context['title'],'',context['source'],'']
    for s in context['sections']:
        lines+=['## '+s['title'],'']+sum(([p,''] for p in s.get('paragraphs',[])),[])
        if 'headers' in s:
            lines+=['| '+' | '.join(s['headers'])+' |','| '+' | '.join(['---']*len(s['headers']))+' |']
            lines+=['| '+' | '.join(str(c).replace('|','/') for c in row)+' |' for row in s['rows']];lines+=['']
    return '\n'.join(lines)

def to_html(context):
    e=html.escape;out=f'<p class="live">{e(context["source"])}</p>'
    for s in context['sections']:
        out+=f'<article class="card project-card"><h3>{e(s["title"])}</h3><div class="project-body">'
        for p in s.get('paragraphs',[]):out+='<p>'+e(p)+'</p>'
        if 'headers' in s:
            out+='<div class="project-table"><table><thead><tr>'+''.join('<th scope="col">'+e(c)+'</th>' for c in s['headers'])+'</tr></thead><tbody>'
            out+=''.join('<tr>'+''.join('<td>'+e(str(c))+'</td>' for c in row)+'</tr>' for row in s['rows'])+'</tbody></table></div>'
        out+='</div></article>'
    return out
