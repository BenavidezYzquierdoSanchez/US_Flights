"""Iconos SVG del HTML original y estructura visual compartida."""
import json,html
from analytics import ROOT,fmt

ICONS=json.loads((ROOT/'data/ui_icons.json').read_text(encoding='utf-8'))
MONTH_LABELS=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
MONTH_NAMES=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
def month_label(value):return value if value=='Todos' else MONTH_NAMES[int(value)-1]
CHART_ICONS={'annual':'chart','season':'calendar','timeline':'chart','mix':'pie','haul':'plane','uncertainty':'shield','hourly':'clock','map':'pin','hubs':'globe','tradeoff':'plane','ranking':'chart','causes':'alert'}
NAV_ICONS={'Panorama':'chart','Estacionalidad':'calendar','Geografía':'globe','Aerolíneas':'plane','Marco del proyecto':'document','Metodología':'shield','Conclusiones':'document'}
VIEW_GRAPHS={'Panorama':['annual','season','mix','haul'],'Estacionalidad':['timeline','uncertainty','hourly','season'],'Geografía':['map','hubs'],'Aerolíneas':['tradeoff','ranking','causes']}
HEIGHTS={'annual':280,'season':360,'mix':240,'haul':210,'timeline':300,'uncertainty':640,'hourly':420,'map':440,'hubs':440,'tradeoff':320,'ranking':640,'causes':500}
KPI_SPECS=[
 ('ops','Operaciones',0,'','plane','Cubo mensual','Operaciones representadas'),
 ('otp','Llegadas a tiempo',2,'%','clock','Referencia interna','Puntuales / operaciones'),
 ('delay15','Atraso ≥15 min',2,'%','alert','Demora','Llegadas demoradas / operaciones'),
 ('delay60','Atraso grave ≥60',2,'%','tri','Demora severa','Incluido en atraso ≥15 min'),
 ('avgDelay','Atraso medio | late',2,' min','sand','Solo demorados','Minutos / llegada ≥15 min'),
 ('cancelRate','Cancelación',2,'%','ban','Incidencia','Cancelados / operaciones'),
 ('divertRate','Desvíos',2,'%','fork','Incidencia','Desviados / operaciones'),
 ('causeCoverage','Cobertura causas válidas',2,'%','pie','Calidad de datos','Operaciones con causas conciliadas')]
KPI_CLASSES=[7,0,1,4,3,4,5,6]

def icon(key,css='ico'):
    return f'<span class="{css}" aria-hidden="true">{ICONS[key]}</span>'

def kpis_html(m,target=80):
    out='<section class="kpis">'
    for i,(key,label,dec,unit,ic,badge,foot) in enumerate(KPI_SPECS):
        val=m[key];value=fmt(val,dec)+(unit if val is not None else '')
        if key=='otp':badge='Sin datos' if val is None else f'{"Cumple" if val>=target else "Bajo"} ref. {target}%'
        width=max(0,min(100,val)) if val is not None and unit=='%' else 0
        out+=f'<article class="kpi t{KPI_CLASSES[i]}"><div class="kpi-h">{icon(ic)}<span class="badge">{html.escape(badge)}</span></div><div class="k">{html.escape(label)}</div><div class="v">{html.escape(value)}</div><div class="kpi-foot">{html.escape(foot)}</div><div class="meter" aria-hidden="true"><span style="width:{width:.2f}%"></span></div></article>'
    return out+'</section>'
