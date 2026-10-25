"""Cuatro conclusiones y recomendaciones basadas en la base completa."""
import html
from analytics import metrics,CAUSES
from ui_design import icon

def conclusions(d,payload):
    m=metrics(d)
    last=int(d.Year.max());previous=last-1
    common=sorted(set(d.loc[d.Year==last,'Month'])&set(d.loc[d.Year==previous,'Month']))
    latest=metrics(d[(d.Year==last)&d.Month.isin(common)])
    prior=metrics(d[(d.Year==previous)&d.Month.isin(common)])
    valid=d[d.CauseValid];causes=valid[list(CAUSES)].sum().sort_values(ascending=False)
    dominant=CAUSES[causes.index[0]] if causes.sum() else 'Sin causas conciliadas'
    share=100*causes.iloc[0]/causes.sum() if causes.sum() else 0
    if common and prior['otp'] is not None and latest['otp'] is not None:
        period=', '.join(f'{v:02d}' for v in common)
        comparison=f'En los meses coincidentes ({period}), el OTP pasa de {prior["otp"]:.2f}% en {previous} a {latest["otp"]:.2f}% en {last}: {latest["otp"]-prior["otp"]:+.2f} puntos porcentuales. La cancelación pasa de {prior["cancelRate"]:.2f}% a {latest["cancelRate"]:.2f}%. La composición de operadores y radios puede variar.'
    else:
        comparison='No hay meses coincidentes suficientes entre los dos últimos años para una comparación equivalente.'
    return [
      {'title':'1. La puntualidad requiere atención','color':'#2ee6a6','icon':'clock',
       'conclusion':f'El {m["otp"]:.2f}% de {m["ops"]:,} operaciones llega a tiempo y el {m["delay15"]:.2f}% registra demora ≥15 minutos. La puntualidad global queda {80-m["otp"]:.2f} puntos porcentuales por debajo de la referencia interna del 80%.',
       'recommendation':'Priorizar el diagnóstico de los períodos y operadores con menor OTP, considerando su volumen, cancelaciones y mezcla de rutas antes de cambiar capacidad o comprometer metas.'},
      {'title':'2. Comparar períodos equivalentes','color':'#5b8def','icon':'calendar','conclusion':comparison,
       'recommendation':f'Comparar los mismos meses de {previous} y {last}; revisar los segmentos con mayor deterioro y contrastar la mezcla de aerolíneas y radios. No presentar el período parcial de {last} como un año completo.'},
      {'title':'3. Revisar la rotación de aeronaves','color':'#f5b942','icon':'plane',
       'conclusion':f'{dominant} reúne el {share:.2f}% de los minutos por causa en las filas conciliadas. Este subconjunto cubre el {m["causeCoverage"]:.2f}% de las operaciones; el hallazgo no se extrapola automáticamente a toda la base.',
       'recommendation':'Investigar los tiempos de rotación, la propagación de demoras y la disponibilidad de reserva. Validar con microdatos de rutas y horarios antes de atribuir causalidad o modificar conexiones.'},
      {'title':'4. Conciliar los datos antes de decidir','color':'#f07178','icon':'shield',
       'conclusion':f'{int((~d.CauseValid).sum()):,} filas no concilian sus minutos por causa y {m["unclassified"]:,} operaciones carecen de categoría de resultado. Los hubs y horarios son resúmenes independientes y el cubo no permite análisis estatal ni semanal válidos.',
       'recommendation':'Conciliar las inconsistencias con la fuente, conservar el residuo sin clasificar y solicitar microdatos con fecha, aeropuerto y hora. Mantener visibles las exclusiones, la cobertura y el alcance de los filtros.'}
    ]

def render_conclusions(d,payload):
    out='<div class="method-intro"><h2>Conclusiones y recomendaciones</h2><p>Síntesis de la base completa 2021–2026. Cada hallazgo se vincula con una acción y sus límites.</p></div><div class="method-grid conclusions-grid">'
    for c in conclusions(d,payload):
        out+=f'<article class="method-card conclusion-card" style="--method-color:{c["color"]}"><div class="method-heading">{icon(c["icon"],"chart-icon")}<span>Hallazgo y acción</span></div><h3>{html.escape(c["title"])}</h3><p><strong style="color:{c["color"]}">Conclusión</strong><br>{html.escape(c["conclusion"])}</p><p style="margin-top:18px"><strong style="color:{c["color"]}">Recomendación</strong><br>{html.escape(c["recommendation"])}</p></article>'
    return out+'</div>'
