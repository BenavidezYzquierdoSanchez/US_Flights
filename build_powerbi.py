"""Construye un proyecto PBIP/PBIR editable; requiere validación final en Desktop."""
import base64,json,zlib,uuid
import pandas as pd
from analytics import *
from charts import CATALOG,make_chart
from project_context import project_context
from methodology import cards as methodology_cards
from conclusions import conclusions
from ui_design import MONTH_NAMES
from ui_design import ICONS,VIEW_GRAPHS,CHART_ICONS,KPI_SPECS,KPI_CLASSES
import math

P=ROOT/'powerbi';P.mkdir(exist_ok=True)
MODEL=P/'US_Flights.SemanticModel';REPORT=P/'US_Flights.Report'
MODEL.mkdir(exist_ok=True);REPORT.mkdir(exist_ok=True)
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

payload,d=load_data()
coords=json.loads((ROOT/'data/airport_coords.json').read_text(encoding='utf-8'))
h=pd.DataFrame(payload['hubs']);h['Latitude']=h.code.map(lambda c:coords.get(c,[None,None])[0]);h['Longitude']=h.code.map(lambda c:coords.get(c,[None,None])[1])
tables={
 'Vuelos':d,
 'Calendario':d[['Period','Year','Month']].drop_duplicates().sort_values('Period'),
 'Aerolineas':d[['Airline','AirlineName','AirlineLabel']].drop_duplicates().sort_values('Airline'),
 'Radios':d[['Haul']].drop_duplicates(),
 'Hubs':h,
 'Horarios':pd.DataFrame(payload['hourly']),
 'Causas':pd.DataFrame([{'Campo':k,'Causa':v} for k,v in CAUSES.items()]),
 'Estados':pd.DataFrame({'Estado':['Puntuales','Demora ≥15','Cancelados','Desviados','Sin clasificar']})
}
tables['ConfiguracionOTP']=pd.DataFrame({'Porcentaje':list(range(101))})
tables['ConfiguracionSoporte']=pd.DataFrame({'Operaciones':[30,50,100,500,1000,5000,10000,50000,100000,1000000]})
tables['Calendario']['MonthName']=tables['Calendario'].Month.map(lambda m:MONTH_NAMES[int(m)-1])
measures={
 'Soporte minimo':('SELECTEDVALUE(ConfiguracionSoporte[Operaciones], 30)','#,0'),
 'Meta OTP':('DIVIDE(SELECTEDVALUE(ConfiguracionOTP[Porcentaje], 80), 100)','0%'),
 'Estado OTP':('IF(ISBLANK([OTP]), "Sin datos", IF([OTP] >= [Meta OTP], "Cumple", "Bajo") & " ref. " & FORMAT([Meta OTP], "0%"))',''),
 'Operaciones':('SUM(Vuelos[ops])','#,0'),
 'Puntuales':('SUM(Vuelos[ontime])','#,0'),
 'Demorados 15':('SUM(Vuelos[delayed15])','#,0'),
 'Demorados 60':('SUM(Vuelos[delayed60])','#,0'),
 'OTP':('DIVIDE([Puntuales], [Operaciones])','0.00%'),
 'Tasa demora 15':('DIVIDE([Demorados 15], [Operaciones])','0.00%'),
 'Tasa demora 60':('DIVIDE([Demorados 60], [Operaciones])','0.00%'),
 'Tasa cancelacion':('DIVIDE(SUM(Vuelos[cancel]), [Operaciones])','0.00%'),
 'Tasa desvios':('DIVIDE(SUM(Vuelos[divert]), [Operaciones])','0.00%'),
 'Demora media':('DIVIDE(SUM(Vuelos[sumDelayMin]), [Demorados 15])','0.00'),
 'Sin clasificar':('SUM(Vuelos[Unclassified])','#,0'),
 'Filas causas excluidas':('COUNTROWS(FILTER(Vuelos, NOT(Vuelos[CauseValid])))','#,0'),
 'Cobertura causas':('DIVIDE(CALCULATE([Operaciones], Vuelos[CauseValid] = TRUE()), [Operaciones])','0.00%'),
 'OTP soporte':('IF([Operaciones] >= [Soporte minimo], [OTP])','0.00%'),
 'Operaciones soporte':('IF([Operaciones] >= [Soporte minimo], [Operaciones])','#,0'),
 'Cancelacion soporte':('IF([Operaciones] >= [Soporte minimo], [Tasa cancelacion])','0.00%'),
 'Referencia OTP':('IF([Operaciones] > 0, [Meta OTP])','0.00%'),
 'Wilson inferior':('VAR n = [Operaciones] RETURN IF(n >= [Soporte minimo] && n > 0, VAR p = [OTP] VAR z = 1.96 VAR den = 1 + z*z/n VAR c = (p + z*z/(2*n))/den VAR h = z*SQRT(p*(1-p)/n + z*z/(4*n*n))/den RETURN c-h)','0.00%'),
 'Wilson superior':('VAR n = [Operaciones] RETURN IF(n >= [Soporte minimo] && n > 0, VAR p = [OTP] VAR z = 1.96 VAR den = 1 + z*z/n VAR c = (p + z*z/(2*n))/den VAR h = z*SQRT(p*(1-p)/n + z*z/(4*n*n))/den RETURN c+h)','0.00%'),
 'Operaciones por estado':('SWITCH(SELECTEDVALUE(Estados[Estado]), "Puntuales", [Puntuales], "Demora ≥15", [Demorados 15], "Cancelados", SUM(Vuelos[cancel]), "Desviados", SUM(Vuelos[divert]), "Sin clasificar", [Sin clasificar])','#,0'),
 'Minutos causa':('VAR campo = SELECTEDVALUE(Causas[Campo]) RETURN SWITCH(campo, "carrierDelay", CALCULATE(SUM(Vuelos[carrierDelay]), Vuelos[CauseValid]=TRUE()), "weatherDelay", CALCULATE(SUM(Vuelos[weatherDelay]), Vuelos[CauseValid]=TRUE()), "nasDelay", CALCULATE(SUM(Vuelos[nasDelay]), Vuelos[CauseValid]=TRUE()), "secDelay", CALCULATE(SUM(Vuelos[secDelay]), Vuelos[CauseValid]=TRUE()), "lateAirDelay", CALCULATE(SUM(Vuelos[lateAirDelay]), Vuelos[CauseValid]=TRUE()))','#,0'),
 'Total minutos conciliados':('SUMX(ALL(Causas), [Minutos causa])','#,0'),
}
hub_measures={
 'Vuelos hub':('SUM(Hubs[flights])','#,0'),
 'OTP hub':('IF(HASONEVALUE(Hubs[code]), DIVIDE(MAX(Hubs[otp]),100))','0.00%'),
 'Cancelacion hub':('IF(HASONEVALUE(Hubs[code]), DIVIDE(MAX(Hubs[cancel]),100))','0.00%'),
 'Latitud hub':('MAX(Hubs[Latitude])','0.0000'),
 'Longitud hub':('MAX(Hubs[Longitude])','0.0000')
}
hour_measures={'Demora horaria':('IF(HASONEVALUE(Horarios[hour_block]), MAX(Horarios[avg_delay]))','0.0')}

def literal(s):return '"'+s.replace('"','""')+'"'
def narrative_core(key):
    # Se ejecuta dentro del contexto de filtros y selección de cada página.
    if key in ['annual','timeline','season']:
        category={'annual':'Calendario[Year]','timeline':'Calendario[Period]','season':'Calendario[MonthName]'}[key]
        return f'''VAR tab = FILTER(ADDCOLUMNS(VALUES({category}), "pct", [OTP]), NOT ISBLANK([pct]))
VAR hi = TOPN(1, tab, [pct], DESC, {category}, ASC)
VAR lo = TOPN(1, tab, [pct], ASC, {category}, ASC)
RETURN IF([Operaciones]=0, "Sin datos para el filtro.", "Mayor OTP: " & CONCATENATEX(hi, {category} & " (" & FORMAT([pct], "0.00%") & ")") & "; menor: " & CONCATENATEX(lo, {category} & " (" & FORMAT([pct], "0.00%") & ")") & ". Revisar períodos bajos. Comparar coberturas equivalentes: 2026 termina en mayo.")'''
    if key=='mix':return '''RETURN IF([Operaciones]=0, "Sin datos para el filtro.", "Puntualidad: " & FORMAT([OTP], "0.00%") & "; operaciones sin categoría: " & FORMAT([Sin clasificar], "#,0") & ". Conservar el residuo y revisar incidencias; demora >=60 es parte de >=15.")'''
    if key in ['ranking','tradeoff','uncertainty','haul']:
        cat='Radios[Haul]' if key=='haul' else 'Aerolineas[AirlineLabel]'
        extra=' Wilson 95% supone independencia binomial; no cuantifica sesgo ni dependencia.' if key=='uncertainty' else ' La comparación no controla la mezcla de rutas y períodos ni demuestra causalidad.'
        return f'''VAR tab = FILTER(ADDCOLUMNS(VALUES({cat}), "pct", [OTP], "n", [Operaciones]), [n]>=[Soporte minimo])
VAR hi = TOPN(1, tab, [pct], DESC, {cat}, ASC)
VAR lo = TOPN(1, tab, [pct], ASC, {cat}, ASC)
RETURN IF(COUNTROWS(tab)=0,"Sin categorías con el soporte seleccionado.", "Mayor OTP: " & CONCATENATEX(hi, {cat} & " (" & FORMAT([pct], "0.00%") & ", N=" & FORMAT([n],"#,0") & ")") & "; menor: " & CONCATENATEX(lo, {cat} & " (" & FORMAT([pct], "0.00%") & ")") & ". Priorizar diagnóstico.{extra}")'''
    if key=='causes':return '''VAR tab = ADDCOLUMNS(ALL(Causas), "mins", [Minutos causa]) VAR topcause=TOPN(1,tab,[mins],DESC,Causas[Causa],ASC) RETURN IF([Total minutos conciliados]=0,"Sin minutos por causa conciliados.","Causa dominante: " & CONCATENATEX(topcause,Causas[Causa] & " (" & FORMAT(DIVIDE([mins],[Total minutos conciliados]),"0.00%") & ")") & ". Priorizar su diagnóstico. Filas excluidas: " & FORMAT([Filas causas excluidas],"#,0") & "; cobertura de operaciones: " & FORMAT([Cobertura causas],"0.00%") & ". Hallazgo del subconjunto conciliado.")'''
    if key in ['map','hubs']:return '''VAR tab=ADDCOLUMNS(VALUES(Hubs[AirportLabel]),"pct",CALCULATE(MAX(Hubs[otp]))) VAR lo=TOPN(1,tab,[pct],ASC,Hubs[AirportLabel],ASC) RETURN "Menor OTP del resumen mostrado: " & CONCATENATEX(lo,Hubs[AirportLabel] & " (" & FORMAT([pct]/100,"0.00%") & ")") & ". Priorizar diagnóstico con volumen y cancelación. Resumen independiente sin fecha ni aerolínea; los filtros del cubo no se aplican."'''
    if key=='hourly':return '''VAR tab=ADDCOLUMNS(VALUES(Horarios[hour_block]),"mins",CALCULATE(MAX(Horarios[avg_delay]))) VAR hi=TOPN(1,tab,[mins],DESC,Horarios[hour_block],ASC) VAR lo=TOPN(1,tab,[mins],ASC,Horarios[hour_block],ASC) RETURN "Mínimo horario: " & CONCATENATEX(lo,FORMAT(Horarios[hour_block],"00") & ":00, " & FORMAT([mins],"0.0") & " min") & "; máximo: " & CONCATENATEX(hi,FORMAT(Horarios[hour_block],"00") & ":00, " & FORMAT([mins],"0.0") & " min") & ". Resumen global: no tiene denominador ni período y no demuestra efecto cascada."'''

for key,section,title,variables,why in CATALOG:
    # Las tablas de narrativa conservan un prefijo explícito con variables y tarea.
    expression=narrative_core(key)
    prefix=f'Variables: {variables}. Propósito: {why} Interpretación: '
    split=expression.rfind('RETURN ')
    # rfind permite conservar bloques VAR y envuelve la expresión final.
    expression=expression[:split]+'RETURN '+literal(prefix)+' & ('+expression[split+7:]+')'
    measures['Lectura '+key]=(expression,'')

def m_partition(frame):
    records=json.loads(frame.to_json(orient='records',force_ascii=False))
    raw=json.dumps(records,ensure_ascii=False,separators=(',',':')).encode()
    compressor=zlib.compressobj(level=9,wbits=-15)
    encoded=base64.b64encode(compressor.compress(raw)+compressor.flush()).decode()
    types=[]
    for col in frame:
        dtype=frame[col].dtype
        typ='type logical' if pd.api.types.is_bool_dtype(dtype) else 'Int64.Type' if pd.api.types.is_integer_dtype(dtype) else 'type number' if pd.api.types.is_numeric_dtype(dtype) else 'type text'
        types.append('{'+literal(col)+', '+typ+'}')
    return [f'let Source = Json.Document(Binary.Decompress(Binary.FromText("{encoded}", BinaryEncoding.Base64), Compression.Deflate)),',
            'Rows = Table.FromRecords(Source),',
            'Typed = Table.TransformColumnTypes(Rows, {'+', '.join(types)+'}) in Typed']

model_tables=[]
for name,frame in tables.items():
    cols=[]
    for c in frame:
        dtype=frame[c].dtype
        datatype='boolean' if pd.api.types.is_bool_dtype(dtype) else 'int64' if pd.api.types.is_integer_dtype(dtype) else 'double' if pd.api.types.is_numeric_dtype(dtype) else 'string'
        col={'name':c,'dataType':datatype,'sourceColumn':c,'summarizeBy':'none' if datatype in ['string','boolean'] or c in ['Year','Month','RowId','Latitude','Longitude','hour_block'] else 'sum'}
        if c in ['Latitude','Longitude']:col['dataCategory']=c
        if name.startswith('Configuracion'):col['summarizeBy']='none'
        if name=='Calendario' and c=='MonthName':col['sortByColumn']='Month'
        if name=='Vuelos' and c in DIMS+['Period','RowId','CauseGap','CauseValid']:col['isHidden']=True
        cols.append(col)
    md=measures if name=='Vuelos' else hub_measures if name=='Hubs' else hour_measures if name=='Horarios' else {}
    model_tables.append({'name':name,'columns':cols,'partitions':[{'name':name,'mode':'import','source':{'type':'m','expression':m_partition(frame)}}],
                         'measures':[{'name':n,'expression':expr.splitlines(),'formatString':fmt,'displayFolder':'Interpretaciones' if n.startswith('Lectura') else 'KPI'} for n,(expr,fmt) in md.items()]})
relationships=[{'name':str(uuid.uuid5(uuid.NAMESPACE_DNS,'usflights-'+col)),'fromTable':'Vuelos','fromColumn':col,'toTable':table,'toColumn':col,'crossFilteringBehavior':'oneDirection'} for col,table in [('Period','Calendario'),('Airline','Aerolineas'),('Haul','Radios')]]
write(MODEL/'model.bim',{'name':'US_Flights','compatibilityLevel':1600,'model':{'culture':'en-US','defaultPowerBIDataSourceVersion':'powerBI_V3','tables':model_tables,'relationships':relationships,'annotations':[{'name':'PBI_QueryOrder','value':json.dumps(list(tables))}]}})
write(MODEL/'definition.pbism',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'4.0','settings':{}})
write(P/'US_Flights.pbip',{'version':'1.0','artifacts':[{'report':{'path':'US_Flights.Report'}}],'settings':{'enableAutoRecovery':True}})
write(REPORT/'definition.pbir',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../US_Flights.SemanticModel'}}})

theme={'name':'US_Flights','dataColors':COLORS+['#b07cff','#94a3b8'],'background':'#070d18','foreground':'#e8eef8','tableAccent':'#2ee6a6',
 'textClasses':{'label':{'color':'#e8eef8','fontFace':'Segoe UI'},'callout':{'color':'#e8eef8','fontFace':'Segoe UI'},'title':{'color':'#e8eef8','fontFace':'Segoe UI'},'header':{'color':'#e8eef8','fontFace':'Segoe UI'}},
 'visualStyles':{'*':{'*':{'background':[{'show':True,'color':{'solid':{'color':'#10192b'}},'transparency':0}],
                         'title':[{'color':{'solid':{'color':'#e8eef8'}},'fontSize':14,'fontFamily':'Segoe UI'}],
                         'categoryAxis':[{'labelColor':{'solid':{'color':'#e8eef8'}}}],
                         'valueAxis':[{'labelColor':{'solid':{'color':'#e8eef8'}}}],
                         'legend':[{'labelColor':{'solid':{'color':'#e8eef8'}}}]}}}}
write(P/'tema_US_Flights.json',theme)
write(REPORT/'StaticResources/RegisteredResources/US_Flights.json',theme)
url='https://developer.microsoft.com/json-schemas/fabric/item/report/definition/'
write(REPORT/'definition/version.json',{'$schema':url+'versionMetadata/1.0.0/schema.json','version':'2.0.0'})
write(REPORT/'definition/report.json',{'$schema':url+'report/3.0.0/schema.json','themeCollection':{'customTheme':{'name':'US_Flights','reportVersionAtImport':{'visual':'1.8.0','page':'2.0.0','report':'3.0.0'},'type':'RegisteredResources'}},'resourcePackages':[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':'US_Flights','path':'US_Flights.json','type':'CustomTheme'}]}]})
resources=json.loads((REPORT/'definition/report.json').read_text(encoding='utf-8'))
for name,svg in ICONS.items():
    filename=f'icon_{name}_20261025.svg'
    ink={'plane':'#94a3b8','clock':'#2ee6a6','alert':'#5b8def','tri':'#f07178','sand':'#f5b942','ban':'#f07178','fork':'#b07cff','pie':'#2ec4b6'}.get(name,'#2ee6a6')
    svg=svg.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" ').replace('currentColor',ink)
    (REPORT/'StaticResources/RegisteredResources'/filename).write_text(svg)
    resources['resourcePackages'][0]['items'].append({'name':filename,'path':filename,'type':'Image'})
write(REPORT/'definition/report.json',resources)

def expr(v):
    val='true' if v is True else 'false' if v is False else str(v)+'D' if isinstance(v,(float,int)) else "'"+str(v).replace("'","''")+"'"
    return {'expr':{'Literal':{'Value':val}}}
def color(v):return {'solid':{'color':expr(v)}}
def projection(table,field,measure=False):
    return {'field':{'Measure' if measure else 'Column':{'Expression':{'SourceRef':{'Entity':table}},'Property':field}},'queryRef':table+'.'+field,'nativeQueryRef':field,'active':True}
def visual(page,name,typ,x,y,w,h,roles=None,title=None,objects=None):
    v={'visualType':typ}
    if typ=='slicer' and (name.startswith('filter') or name in ['support_control','target_control']):
        v['syncGroup']={'groupName':'US_Flights_'+name,'fieldChanges':True,'filterChanges':True}
    if roles:
        v['query']={'queryState':{r:{'projections':p} for r,p in roles.items()}}
        if name in ['ranking','causes']:
            v['query']['sortDefinition']={'sort':[{'field':roles['Y'][0]['field'],'direction':'Descending'}],'isDefaultSort':False}
        elif name in ['annual','timeline','season','hourly','uncertainty']:
            v['query']['sortDefinition']={'sort':[{'field':roles['Category'][0]['field'],'direction':'Ascending'}],'isDefaultSort':False}
    v['visualContainerObjects']={'background':[{'properties':{'show':expr(True),'color':color('#10192b'),'transparency':expr(0)}}]}
    if title:v['visualContainerObjects']['title']=[{'properties':{'show':expr(True),'text':expr(title),'fontColor':color('#e8eef8'),'fontSize':expr(14)}}]
    if objects:v['objects']=objects
    write(page/'visuals'/name/'visual.json',{'$schema':url+'visualContainer/2.4.0/schema.json','name':name,'position':{'x':x,'y':y,'z':len(list((page/'visuals').glob('*'))) if (page/'visuals').exists() else 0,'width':w,'height':h,'tabOrder':int(y+x)},'visual':v})

def text(page,name,text,x,y,w,h,size=12):
    paragraphs=[{'textRuns':[{'value':line,'textStyle':{'fontSize':f'{size}pt','fontFamily':'Segoe UI','color':'#e8eef8'}}]} for line in text.split('\n')]
    visual(page,name,'textbox',x,y,w,h,objects={'general':[{'properties':{'paragraphs':paragraphs}}]})

def image_icon(page,name,kind,x,y):
    filename=f'icon_{kind}_20261025.svg'
    visual(page,name,'image',x,y,30,30,objects={'general':[{'properties':{'imageUrl':{'expr':{'ResourcePackageItem':{'PackageName':'RegisteredResources','PackageType':1,'ItemName':filename}}}}}]})

spec={
 'annual':('lineClusteredColumnComboChart',{'Category':[projection('Calendario','Year')],'ColumnY':[projection('Vuelos','Operaciones',True)],'LineY':[projection('Vuelos','OTP',True),projection('Vuelos','Referencia OTP',True)]}),
 'mix':('donutChart',{'Category':[projection('Estados','Estado')],'Y':[projection('Vuelos','Operaciones por estado',True)]}),
 'haul':('clusteredColumnChart',{'Category':[projection('Radios','Haul')],'Y':[projection('Vuelos','OTP soporte',True)]}),
 'timeline':('lineChart',{'Category':[projection('Calendario','Period')],'Y':[projection('Vuelos','OTP',True),projection('Vuelos','Referencia OTP',True)]}),
 'season':('lineChart',{'Category':[projection('Calendario','MonthName')],'Series':[projection('Calendario','Year')],'Y':[projection('Vuelos','OTP',True)]}),
 'uncertainty':('lineChart',{'Category':[projection('Aerolineas','AirlineLabel')],'Y':[projection('Vuelos','OTP soporte',True),projection('Vuelos','Wilson inferior',True),projection('Vuelos','Wilson superior',True)]}),
 'hourly':('lineChart',{'Category':[projection('Horarios','hour_block')],'Y':[projection('Horarios','Demora horaria',True)]}),
 'map':('azureMap',{'Category':[projection('Hubs','AirportLabel')],'X':[projection('Hubs','Longitud hub',True)],'Y':[projection('Hubs','Latitud hub',True)],'Size':[projection('Hubs','Vuelos hub',True)],'Tooltips':[projection('Hubs','OTP hub',True),projection('Hubs','Cancelacion hub',True)]}),
 'hubs':('scatterChart',{'Category':[projection('Hubs','AirportLabel')],'X':[projection('Hubs','Vuelos hub',True)],'Y':[projection('Hubs','OTP hub',True)],'Size':[projection('Hubs','Cancelacion hub',True)]}),
 'tradeoff':('scatterChart',{'Category':[projection('Aerolineas','AirlineLabel')],'X':[projection('Vuelos','Operaciones soporte',True)],'Y':[projection('Vuelos','OTP soporte',True)],'Size':[projection('Vuelos','Cancelacion soporte',True)]}),
 'ranking':('clusteredBarChart',{'Category':[projection('Aerolineas','AirlineLabel')],'Y':[projection('Vuelos','OTP soporte',True)]}),
 'causes':('clusteredBarChart',{'Category':[projection('Causas','Causa')],'Y':[projection('Vuelos','Minutos causa',True)]})
}
pages=[]
for i,section in enumerate(['Panorama','Estacionalidad','Geografía','Aerolíneas']):
    name=f'page{i+1}';pages.append(name);page=REPORT/'definition/pages'/name
    cats=[next(c for c in CATALOG if c[0]==k) for k in VIEW_GRAPHS[section]]
    placements={
      'Panorama':{'annual':(20,495,1240,280,180),'season':(20,990,710,650,400),'mix':(750,990,510,240,260),'haul':(750,1510,510,210,300)},
      'Estacionalidad':{'timeline':(20,495,1240,300,200),'uncertainty':(20,1020,710,420,350),'hourly':(750,1020,510,420,350),'season':(20,1820,1240,360,220)},
      'Geografía':{'map':(20,495,710,440,300),'hubs':(750,495,510,440,300)},
      'Aerolíneas':{'tradeoff':(20,495,1240,320,220),'ranking':(20,1060,710,500,350),'causes':(750,1060,510,500,350)}}[section]
    page_height=max(y+h+note+140 for x,y,w,h,note in placements.values())
    if section=='Geografía':page_height+=470
    write(page/'page.json',{'$schema':url+'page/2.0.0/schema.json','name':name,'displayName':section,'displayOption':'FitToWidth','width':1280,'height':page_height,'objects':{'background':[{'properties':{'color':color('#070d18'),'transparency':expr(0)}}]}})
    text(page,'header','US_Flights | '+section+' | 2021-01 a 2026-05',20,10,1240,55,22)
    text(page,'quality','139 filas con causas no conciliadas; 7,959 operaciones sin categoría. Referencia OTP interna ajustable. Hubs y horarios independientes.',20,65,1240,45,11)
    for j,(table,col,label) in enumerate([('Calendario','Year','Año'),('Calendario','MonthName','Mes'),('Aerolineas','AirlineLabel','Aerolínea'),('Radios','Haul','Radio')]):
        visual(page,'filter'+str(j),'slicer',20+j*250,115,235,65,{'Values':[projection(table,col)]},label)
    if section=='Geografía':visual(page,'airport','slicer',1020,115,235,65,{'Values':[projection('Hubs','AirportLabel')]},'Aeropuerto (resumen)')
    # Controles nativos equivalentes a los ajustes del dashboard web.
    visual(page,'support_control','slicer',20,478,290,65,{'Values':[projection('ConfiguracionSoporte','Operaciones')]},'Soporte mínimo · predeterminado 30',{'selection':[{'properties':{'singleSelect':expr(True)}}]})
    visual(page,'target_control','slicer',330,478,290,65,{'Values':[projection('ConfiguracionOTP','Porcentaje')]},'Referencia OTP · predeterminada 80%',{'selection':[{'properties':{'singleSelect':expr(True)}}]})
    for j,(field,label) in enumerate([('Operaciones','Operaciones'),('OTP','Puntualidad'),('Tasa demora 15','Demora ≥15'),('Tasa demora 60','Demora ≥60'),('Demora media','Minutos / demorado'),('Tasa cancelacion','Cancelación'),('Tasa desvios','Desvíos'),('Cobertura causas','Cobertura causas')]):
        x=20+(j%4)*312;ky=185+(j//4)*145
        visual(page,'kpi'+str(j),'card',x,ky+35,300,100,{'Values':[projection('Vuelos',field,True)]},label,
               {'labels':[{'properties':{'fontSize':expr(20),'color':color('#e8eef8')}}],'categoryLabels':[{'properties':{'show':expr(False)}}]})
        image_icon(page,'kpi_icon_'+str(j),KPI_SPECS[j][4],x+12,ky+3)
        if field=='OTP':
            visual(page,'kpi_badge_'+str(j),'card',x+65,ky+3,230,30,{'Values':[projection('Vuelos','Estado OTP',True)]},objects={'labels':[{'properties':{'fontSize':expr(10),'color':color('#2ee6a6')}}],'categoryLabels':[{'properties':{'show':expr(False)}}]})
        else:text(page,'kpi_badge_'+str(j),KPI_SPECS[j][5],x+65,ky+3,230,30,10)
        fill=['#172033','#103228','#122a50','#3d1b28','#332a14','#3d1b28','#2a1c43','#10323a'][j]
        for visual_name in ['kpi'+str(j),'kpi_icon_'+str(j),'kpi_badge_'+str(j)]:
            path=page/'visuals'/visual_name/'visual.json';content=json.loads(path.read_text(encoding='utf-8'))
            content['visual']['visualContainerObjects']['background'][0]['properties']['color']=color(fill)
            write(path,content)
    for j,(key,_,title,variables,why) in enumerate(cats):
        x,y,w,h,note_h=placements[key];y+=80;typ,roles=spec[key]
        if key=='uncertainty':title='OTP y límites Wilson 95% por aerolínea'
        objects={}
        if key=='map':objects={'bubbleLayer':[{'properties':{'show':expr(True),'sizeByValue':expr(True)}}]}
        if key=='annual':objects={'valueAxis':[{'properties':{'secShow':expr(True)}}]}
        visual(page,key,typ,x,y,w,h,roles,'      '+title,objects)
        image_icon(page,'chart_icon_'+key,CHART_ICONS[key],x+5,y+5)
        visual(page,'note_'+key,'tableEx',x,y+h+5,w,note_h,{'Values':[projection('Vuelos','Lectura '+key,True)]},'Variables, propósito e interpretación',
               {'values':[{'properties':{'fontSize':expr(11),'fontColorPrimary':color('#e8eef8'),'wordWrap':expr(True)}}],
                'columnHeaders':[{'properties':{'wordWrap':expr(True),'fontSize':expr(10),'fontColor':color('#2ee6a6')}}],
                'total':[{'properties':{'totals':expr(False)}}],
                'grid':[{'properties':{'rowPadding':expr(8),'gridVertical':expr(False),'gridHorizontal':expr(False)}}]})
    if section=='Geografía':
        text(page,'map_help','Azure Maps ofrece estilos de calles y satélite desde sus controles. Si no hay conexión o el mapa está deshabilitado, utiliza la tabla inferior.',20,page_height-475,1240,55,11)
        visual(page,'airport_data','tableEx',20,page_height-410,1240,385,{'Values':[projection('Hubs','AirportLabel'),projection('Hubs','Vuelos hub',True),projection('Hubs','OTP hub',True),projection('Hubs','Cancelacion hub',True),projection('Hubs','Latitud hub',True),projection('Hubs','Longitud hub',True)]},'Aeropuertos · datos disponibles sin fondo cartográfico')
# Módulo editorial y referencias de la base completa. Sin segmentadores locales.
context=project_context(d,payload);name='project_context';pages.append(name)
page=REPORT/'definition/pages'/name
text(page,'context_header','US_Flights | Marco del proyecto | 2021-2026',20,10,1240,65,22)
text(page,'context_scope','Síntesis AeroPulse actualizada con el cubo completo. Referencias globales; 2026 cubre enero-mayo. Sin filtros locales en esta página.',20,80,1240,60,12)
y=160
for index,s in enumerate(context['sections']):
    text(page,'context_title_'+str(index),s['title'],20,y,1240,45,17);y+=50
    lines=list(s.get('paragraphs',[]))
    if 'rows' in s:
        lines+=[' | '.join(s['headers'])]
        lines+=[' · '.join(row) for row in s['rows']]
    content='\n\n'.join(lines)
    height=max(100,sum(max(1,math.ceil(len(line)/135)) for line in content.split('\n'))*24+35)
    text(page,'context_body_'+str(index),content,20,y,1240,height,12);y+=height+25
visual(page,'annual_evidence','tableEx',20,y,1240,330,{'Values':[projection('Calendario','Year'),projection('Vuelos','Operaciones',True),projection('Vuelos','OTP',True),projection('Vuelos','Tasa cancelacion',True)]},'Referencia anual del modelo semántico')
write(page/'page.json',{'$schema':url+'page/2.0.0/schema.json','name':name,'displayName':'Marco del proyecto','displayOption':'FitToWidth','width':1280,'height':y+350,'objects':{'background':[{'properties':{'color':color('#070d18'),'transparency':expr(0)}}]}})
name='methodology';pages.append(name);page=REPORT/'definition/pages'/name
text(page,'method_header','Metodología paso a paso',20,10,1240,60,22)
text(page,'method_lead','Qué analizamos, cómo calculamos y hasta dónde permiten concluir los datos.',20,75,1240,50,12)
for index,c in enumerate(methodology_cards(d,payload)):
    if index==8:
        c=dict(c,text='El mapa nativo usa Azure Maps con coordenadas de los 35 aeropuertos. Sus controles permiten estilos de calles y satélite cuando el servicio está disponible. El color/tamaño y los tooltips describen los hubs, sin fecha ni aerolínea. Sin conexión se conserva la tabla de aeropuertos; el mapa vectorial sin conexión permanece en HTML y Streamlit.')
    x=20+(index%2)*630;y=140+(index//2)*350
    text(page,'method_card_'+str(index),c['tag']+'\n\n'+c['title']+'\n\n'+c['text'],x,y,610,330,12)
    path=page/'visuals'/('method_card_'+str(index))/'visual.json'
    content=json.loads(path.read_text(encoding='utf-8'));runs=content['visual']['objects']['general'][0]['properties']['paragraphs']
    runs[0]['textRuns'][0]['textStyle']['color']=c['color'];runs[2]['textRuns'][0]['textStyle']['fontSize']='15pt'
    write(path,content)
write(page/'page.json',{'$schema':url+'page/2.0.0/schema.json','name':name,'displayName':'Metodología','displayOption':'FitToWidth','width':1280,'height':2260,'objects':{'background':[{'properties':{'color':color('#070d18'),'transparency':expr(0)}}]}})
name='conclusions';pages.append(name);page=REPORT/'definition/pages'/name
text(page,'conclusions_header','Conclusiones y recomendaciones',20,10,1240,60,22)
text(page,'conclusions_scope','Cuatro hallazgos de la base completa 2021-2026 con recomendaciones. Referencias globales, independientes de los filtros de otras páginas.',20,75,1240,60,12)
for index,c in enumerate(conclusions(d,payload)):
    x=20+(index%2)*630;y=150+(index//2)*460
    text(page,'conclusion_'+str(index),c['title']+'\n\nConclusión\n'+c['conclusion']+'\n\nRecomendación\n'+c['recommendation'],x,y,610,435,12)
    path=page/'visuals'/('conclusion_'+str(index))/'visual.json';content=json.loads(path.read_text(encoding='utf-8'))
    paragraph=content['visual']['objects']['general'][0]['properties']['paragraphs'][0]
    paragraph['textRuns'][0]['textStyle'].update({'color':c['color'],'fontSize':'16pt'})
    write(path,content)
write(page/'page.json',{'$schema':url+'page/2.0.0/schema.json','name':name,'displayName':'Conclusiones','displayOption':'FitToWidth','width':1280,'height':1080,'objects':{'background':[{'properties':{'color':color('#070d18'),'transparency':expr(0)}}]}})
write(REPORT/'definition/pages/pages.json',{'$schema':url+'pagesMetadata/1.0.0/schema.json','pageOrder':pages,'activePageName':pages[0]})

(P/'medidas_DAX.txt').write_text('\n\n'.join(f'-- Tabla: {table}\n{name} =\n{expr}\n-- Formato: {fmt}' for table,md in [('Vuelos',measures),('Hubs',hub_measures),('Horarios',hour_measures)] for name,(expr,fmt) in md.items()),encoding='utf-8')
(P/'consulta_validacion.dax').write_text('''EVALUATE
ROW("ops", [Operaciones], "otp", [OTP]*100,
    "delay15", [Tasa demora 15]*100, "delay60", [Tasa demora 60]*100,
    "cancelRate", [Tasa cancelacion]*100, "divertRate", [Tasa desvios]*100,
    "avgDelay", [Demora media], "unclassified", [Sin clasificar],
    "causeCoverage", [Cobertura causas]*100)
''',encoding='utf-8')
pd.DataFrame([{'KPI':k,'Valor':v} for k,v in metrics(d).items()]).to_csv(P/'kpi_referencia_python.csv',index=False)

# Alternativa Power Query desde archivo local, para cambiar de fuente sin regenerar el proyecto.
mcode='''// Crear parámetro RutaJSON con la ruta completa al JSON; cambiar Section para cada tabla.
let
    Source = Json.Document(File.Contents(RutaJSON)),
    Section = Source[cube],
    Rows = Table.FromRecords(Section),
    Numeric = Table.TransformColumnTypes(Rows, {{"Year",Int64.Type},{"Month",Int64.Type},{"ops",Int64.Type},{"ontime",Int64.Type},{"delayed15",Int64.Type},{"delayed60",Int64.Type},{"cancel",Int64.Type},{"divert",Int64.Type},{"sumDelayMin",type number},{"carrierDelay",type number},{"weatherDelay",type number},{"nasDelay",type number},{"secDelay",type number},{"lateAirDelay",type number}}),
    Gap = Table.AddColumn(Numeric,"CauseGap", each [carrierDelay]+[weatherDelay]+[nasDelay]+[secDelay]+[lateAirDelay]-[sumDelayMin],type number),
    Valid = Table.AddColumn(Gap,"CauseValid",each Number.Abs([CauseGap])<=1,type logical),
    Residual = Table.AddColumn(Valid,"Unclassified",each [ops]-[ontime]-[delayed15]-[cancel]-[divert],Int64.Type),
    Period = Table.AddColumn(Residual,"Period",each Text.From([Year])&"-"&Text.PadStart(Text.From([Month]),2,"0"),type text),
    Index = Table.AddIndexColumn(Period,"RowId",1,1,Int64.Type)
in Index
'''
(P/'PowerQuery_fuente_local.m').write_text(mcode,encoding='utf-8')
(P/'LEEME_POWER_BI.md').write_text('''# Abrir el proyecto Power BI

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
''',encoding='utf-8')
print('Proyecto PBIP actualizado: 7 páginas, nombres completos, meses, controles, metodología y conclusiones.')
