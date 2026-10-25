"""Regresiones de datos, denominadores, exclusiones y paridad JS/Python.
Uso: python tests/verify_project.py [--browser RUTA_AL_EJECUTABLE_CHROMIUM]
Para la parte web se requiere playwright y un navegador instalado.
"""
import argparse,base64,json,math,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from analytics import *
from charts import CATALOG,make_chart
from project_context import project_context,to_markdown

parser=argparse.ArgumentParser();parser.add_argument('--browser');args=parser.parse_args()
payload,d=load_data();a=audit(d,payload);m=metrics(d)
assert len(d)==3344 and m['ops']==38382189
assert d.AirlineLabel.str.contains(' — ').all()
assert d.AirlineName.nunique()==22
assert all(h['AirportLabel'].startswith(h['code']+' — ') for h in payload['hubs'])
assert len({h['AirportName'] for h in payload['hubs']})==35
assert int(d.ontime.sum())==30452745
assert int(d.delayed15.sum())==7185900
assert int(d.delayed60.sum())==2502912
assert m['unclassified']==7959 and a['invalid_cause_rows']==139
assert math.isclose(m['otp'],79.34082394310549,abs_tol=1e-10)
assert math.isclose(m['avgDelay'],508544837/7185900,abs_tol=1e-10)
assert not metrics(d.iloc[0:0])['otp'] and metrics(d.iloc[0:0])['avgDelay'] is None
assert len(d[d.CauseValid])==3205
context=project_context(d,payload);context_md=to_markdown(context)
assert '38,382,189' in context_md and '3,185,124' in context_md
assert '2026 es un período parcial' in context_md
assert len(next(s for s in context['sections'] if s['title']=='Cinco decisiones y evidencia necesaria')['rows'])==5
assert len(next(s for s in context['sections'] if s['title']=='Preguntas que conectan el marco con las vistas')['rows'])==8
assert math.isclose(d.loc[d.CauseValid,'ops'].sum()/d.ops.sum()*100,92.43502500599952)
for n in [30,112,10000,38382189]:
    lo,hi=wilson(n*.8,n);assert 0<=lo<=80<=hi<=100
for key,*_ in CATALOG:
    for data in [d,subset(d,{'Year':2026,'Month':12}),subset(d,{'Year':2025,'Airline':'DL'})]:
        f,note=make_chart(key,data,payload)
        assert note and (f is not None or key not in ['map','hubs','hourly'])

# La instantánea importada por Power Query coincide con cada exportación auditada.
model=json.loads((ROOT/'powerbi/US_Flights.SemanticModel/model.bim').read_text(encoding='utf-8'))
for t in model['model']['tables']:
    line=t['partitions'][0]['source']['expression'][0]
    encoded=line.split('Binary.FromText("')[1].split('"')[0]
    records=json.loads(zlib.decompress(base64.b64decode(encoded),-15))
    if t['name']=='Vuelos':
        assert len(records)==len(d)
        for k in MEASURES+['Unclassified']:
            assert sum(r[k] for r in records)==d[k].sum()
        assert sum(r['CauseValid'] for r in records)==3205

results={'python_data_checks':'PASS','powerbi_embedded_snapshot':'PASS','charts_python':len(CATALOG),
         'powerbi_desktop':'NOT_RUN','dax_engine':'NOT_RUN'}
if args.browser:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b=pw.chromium.launch(executable_path=args.browser,headless=True,args=['--no-sandbox'])
        page=b.new_page(viewport={'width':1440,'height':1000});page.add_init_script('window.FLIGHTS_OFFLINE=true');errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        # El HTML autónomo no solicita red, ni siquiera para la geometría del mapa.
        external=[]
        def block(route):
            external.append(route.request.url);route.abort()
        page.route('https://**',block);page.route('http://**',block)
        page.goto((ROOT/'dashboard_US_Flights.html').as_uri())
        page.wait_for_function('window.USFlights && document.querySelectorAll(".js-plotly-plot").length === 4')
        assert page.evaluate('''()=>{const p=document.querySelector('.js-plotly-plot');return p._fullLayout.width>p.parentElement.clientWidth*.9}''')
        assert page.locator('.kpi .ico svg').count()==8
        assert page.locator('.kpi .badge').count()==8
        assert page.locator('.kpi .meter').count()==8
        assert page.locator('nav .nav-icon svg').count()==7
        assert page.locator('#Month option').all_text_contents()==['Todos','Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        assert 'AA — American Airlines' in page.locator('#Airline').inner_text()
        assert 'ATL — Hartsfield' in page.locator('#airport').inner_text()
        assert page.locator('#plot-mix').evaluate('(p)=>p.data[0].type')=='pie'
        assert page.locator('#plot-annual').evaluate('(p)=>p.data[0].type')=='bar'
        assert page.locator('#plots .grid-2').count()==1
        assert page.locator('#plot-season').bounding_box()['x'] < page.locator('#plot-mix').bounding_box()['x']
        assert page.locator('#plot-mix').bounding_box()['y'] < page.locator('#plot-haul').bounding_box()['y']
        cases=[{}, {'Year':2026},{'Month':7},{'Airline':'EM'},{'Haul':'largo'},
               {'Year':2025,'Month':3,'Airline':'DL'}, {'Year':2026,'Month':12}]
        cases += [{'Year':y,'Airline':air} for y in [2021,2023,2026] for air in ['AA','DL','WN','B6']]
        for filters in cases:
            expected=metrics(subset(d,filters))
            got=page.evaluate('''f=>USFlights.aggregate(USFlights.getRows().filter(r=>Object.entries(f).every(([k,v])=>r[k]===v)))''',filters)
            for k,v in expected.items():
                assert got[k] is None if v is None else math.isclose(got[k],v,abs_tol=1e-8), (filters,k,v,got.get(k))
        for view,count in [('Estacionalidad',4),('Geografía',2),('Aerolíneas',3),('Panorama',4)]:
            page.get_by_role('button',name=view,exact=True).click()
            page.wait_for_function('(n)=>document.querySelectorAll(".js-plotly-plot").length===n',arg=count)
            page.wait_for_timeout(150)
            assert page.locator('.interp').count()==count
            assert all('Variables:' in t and 'Interpretación' in t for t in page.locator('.interp').all_text_contents())
        page.get_by_role('button',name='Metodología',exact=True).click()
        page.wait_for_function('!document.getElementById("methodology").hidden')
        assert page.locator('#methodology .method-card').count()==12
        assert page.locator('#methodology pre').count()==0
        page.screenshot(path=str(ROOT/'docs/vista_metodologia_tarjetas.png'),full_page=True)
        page.get_by_role('button',name='Conclusiones',exact=True).click()
        page.wait_for_function('!document.getElementById("conclusions").hidden')
        assert page.locator('#conclusions .conclusion-card').count()==4
        assert page.locator('#conclusions').inner_text().count('Recomendación')==4
        page.get_by_role('button',name='Marco del proyecto',exact=True).click()
        page.wait_for_function('!document.getElementById("project-context").hidden')
        assert '38,382,189' in page.locator('#project-context').inner_text()
        assert '3,185,124' in page.locator('#project-context').inner_text()
        assert page.locator('#project-context table').count()>=5
        assert 'Cinco decisiones' in page.locator('#project-context').inner_text()
        page.screenshot(path=str(ROOT/'docs/vista_marco_proyecto.png'),full_page=True)
        page.get_by_role('button',name='Panorama',exact=True).click()
        # Filtros reales, descarga y ausencia de ceros engañosos al vaciar el corte.
        page.select_option('#Year','2026');page.select_option('#Month','12')
        page.wait_for_function('document.querySelector("#kpis").textContent.includes("Sin datos")')
        assert 'No hay operaciones' in page.locator('#plots').inner_text()
        page.click('#reset');page.select_option('#Year','2025')
        page.wait_for_function('document.querySelector("#plots .interp").textContent.includes("2025")')
        with page.expect_download() as download:page.click('#export')
        csv=pd.read_csv(download.value.path());assert len(csv)==len(d[d.Year==2025])
        assert set(csv.Year)=={2025}
        page.click('#reset');page.wait_for_timeout(200)
        page.screenshot(path=str(ROOT/'docs/vista_panorama.png'),full_page=True)
        page.get_by_role('button',name='Geografía',exact=True).click();page.wait_for_timeout(500)
        assert page.locator('.geo').count()==1
        assert page.locator('.scattergeo .point').count()==35
        page.screenshot(path=str(ROOT/'docs/vista_geografia.png'),full_page=True)
        # Validación de un corte de aeropuerto y mapa independiente del cubo.
        page.select_option('#airport','ATL');page.select_option('#Year','2026')
        page.wait_for_timeout(400);assert page.locator('.scattergeo .point').count()==1
        page.select_option('#airport','Todos');page.select_option('#Year','Todos')
        page.wait_for_timeout(400)
        page.set_viewport_size({'width':390,'height':844});page.wait_for_timeout(800)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+2')
        page.screenshot(path=str(ROOT/'docs/vista_movil.png'),full_page=True)
        assert not errors,errors
        assert not external,external
        b.close()
    results['javascript_python_parity_cases']=len(cases)
    results['html_ui_filters_download_offline_geo_mobile']='PASS'
(ROOT/'docs/test_results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
