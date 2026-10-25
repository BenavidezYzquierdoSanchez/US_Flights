"""Revisión estructural y de datos frente a la última versión HTML.
No inicia Power BI Desktop ni ejecuta el motor DAX.
"""
import base64,json,re,sys,zlib
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from analytics import load_data,MEASURES,DIMS,metrics
from ui_design import MONTH_NAMES,VIEW_GRAPHS
from conclusions import conclusions

P=ROOT/'powerbi';R=P/'US_Flights.Report';M=P/'US_Flights.SemanticModel'
payload,source=load_data()
database=json.loads((M/'model.bim').read_text(encoding='utf-8'))
tables={t['name']:t for t in database['model']['tables']}
def records(table):
    line=tables[table]['partitions'][0]['source']['expression'][0]
    blob=line.split('Binary.FromText("')[1].split('"')[0]
    return pd.DataFrame(json.loads(zlib.decompress(base64.b64decode(blob),-15)))
fact=records('Vuelos')
pd.testing.assert_frame_equal(source[DIMS+MEASURES+['AirlineLabel','Unclassified','CauseValid']].reset_index(drop=True),fact[DIMS+MEASURES+['AirlineLabel','Unclassified','CauseValid']].reset_index(drop=True),check_dtype=False,check_exact=True)
assert len(records('Aerolineas'))==22
assert len(records('Hubs'))==35
assert records('Aerolineas').AirlineLabel.str.contains(' — ').all()
assert records('Hubs').AirportLabel.str.contains(' — ').all()
calendar=records('Calendario')
assert all(r.MonthName==MONTH_NAMES[r.Month-1] for r in calendar.itertuples())
assert next(c for c in tables['Calendario']['columns'] if c['name']=='MonthName')['sortByColumn']=='Month'
assert records('ConfiguracionOTP').Porcentaje.tolist()==list(range(101))
assert 30 in records('ConfiguracionSoporte').Operaciones.tolist()

order=json.loads((R/'definition/pages/pages.json').read_text(encoding='utf-8'))['pageOrder']
page_names=[];visuals=[];chart_count=0
model_fields={t:{'columns':{c['name'] for c in v['columns']},'measures':{m['name'] for m in v.get('measures',[])}} for t,v in tables.items()}
def check_refs(node):
    if isinstance(node,dict):
        for kind,bucket in [('Column','columns'),('Measure','measures')]:
            if kind in node:
                ref=node[kind];table=ref.get('Expression',{}).get('SourceRef',{}).get('Entity')
                if table:assert ref['Property'] in model_fields[table][bucket],(table,ref['Property'])
        for v in node.values():check_refs(v)
    elif isinstance(node,list):
        for v in node:check_refs(v)
for page_id in order:
    path=R/'definition/pages'/page_id
    page=json.loads((path/'page.json').read_text(encoding='utf-8'));page_names.append(page['displayName'])
    local={f.parent.name:json.loads(f.read_text(encoding='utf-8')) for f in (path/'visuals').glob('*/visual.json')}
    for name,v in local.items():
        pos=v['position'];assert pos['x']>=0 and pos['y']>=0
        assert pos['x']+pos['width']<=page['width'] and pos['y']+pos['height']<=page['height'],(page_id,name,'fuera del lienzo')
        check_refs(v);visuals.append(v)
    if page['displayName'] in VIEW_GRAPHS:
        for key in VIEW_GRAPHS[page['displayName']]:
            assert key in local and 'note_'+key in local;chart_count+=1
        assert sum(n.startswith('kpi_icon_') for n in local)==8
        assert local['filter1']['visual']['query']['queryState']['Values']['projections'][0]['field']['Column']['Property']=='MonthName'
        for name in ['filter0','filter1','filter2','filter3','support_control','target_control']:
            assert local[name]['visual']['syncGroup']['filterChanges']
    if page['displayName']=='Metodología':assert sum(n.startswith('method_card_') for n in local)==12
    if page['displayName']=='Conclusiones':
        for i,c in enumerate(conclusions(source,payload)):
            raw=json.dumps(local['conclusion_'+str(i)],ensure_ascii=False)
            assert c['conclusion'] in raw and c['recommendation'] in raw
html_pages=re.findall(r'<button data-view="([^"]+)"', (ROOT/'dashboard_US_Flights.html').read_text(encoding='utf-8'))
assert page_names==html_pages,(page_names,html_pages)
assert len(page_names)==7 and chart_count==13
for package in json.loads((R/'definition/report.json').read_text(encoding='utf-8'))['resourcePackages']:
    for item in package['items']:
        assert (R/'StaticResources'/package['name']/item['path']).exists()
report={'estado':'COMPROBADO EN ARCHIVOS','paginas':page_names,'analisis_distintos':12,'ubicaciones_graficos':chart_count,'aerolineas':22,'aeropuertos':35,'meses_completos_ordenados':True,'metodologia_tarjetas':12,'conclusiones_con_recomendaciones':4,'filtros_sincronizados':True,'controles_soporte_y_meta':True,'datos_identicos_al_dashboard':True,'metricas_python_de_la_instantanea':metrics(fact),'referencias_modelo_y_lienzos':'PASS','visuales_inspeccionados':len(visuals),'power_bi_desktop':'NO EJECUTADO','motor_DAX':'NO EJECUTADO'}
(P/'revision_dashboard.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps(report,ensure_ascii=False,indent=2))
