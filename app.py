"""Ejecutar desde la carpeta del proyecto: python -m streamlit run app.py"""
import streamlit as st
from analytics import ROOT,load_data,subset,metrics,audit,fmt
from charts import CATALOG,make_chart
from ui_design import kpis_html,icon,CHART_ICONS,HEIGHTS,month_label
from project_context import project_context,to_markdown
from labels import airline_label,airport_label
from methodology import render_cards
from map_widget import map_html
from conclusions import render_conclusions

st.set_page_config(page_title='US_Flights · Puntualidad aérea',page_icon='✈',layout='wide')
st.markdown('''<style>.stApp{background:#070d18;color:#e8eef8}
[data-testid="stSidebar"]{background:#0a101c} h1,h2,h3{color:#e8eef8}
[data-testid="stMetric"]{background:#10192b;border:1px solid #25413f;border-radius:14px;padding:16px}
.analysis{background:#10192b;border-left:3px solid #2ee6a6;border-radius:10px;padding:16px;margin-bottom:24px;line-height:1.6}
.analysis b{color:#2ee6a6}</style>''',unsafe_allow_html=True)

@st.cache_data
def read():return load_data()

st.markdown('<style>'+ (ROOT/'web/kpi.css').read_text(encoding='utf-8') + '</style>',unsafe_allow_html=True)
st.markdown('<style>'+ (ROOT/'web/methodology.css').read_text(encoding='utf-8') + '</style>',unsafe_allow_html=True)
st.markdown('<style>'+ (ROOT/'web/font.css').read_text(encoding='utf-8') + '.stApp,h1,h2,h3,input,button{font-family:Manrope,system-ui,sans-serif}</style>',unsafe_allow_html=True)
payload,df=read()
report=audit(df,payload)
st.sidebar.title('US_Flights')
st.sidebar.caption('INTELIGENCIA DE PUNTUALIDAD AÉREA')
view=st.sidebar.radio('Vista',['Panorama','Estacionalidad','Geografía','Aerolíneas','Marco del proyecto','Metodología','Conclusiones'])
st.sidebar.caption('Filtros del cubo mensual')
filters={}
for col,label in [('Year','Año'),('Month','Mes'),('Airline','Aerolínea'),('Haul','Radio')]:
    filters[col]=st.sidebar.selectbox(label,['Todos']+sorted(df[col].unique().tolist()),key=col,format_func=airline_label if col=='Airline' else month_label if col=='Month' else str)
min_ops=st.sidebar.number_input('Soporte mínimo (operaciones)',min_value=30,value=30,step=10)
target=st.sidebar.slider('Referencia interna OTP (%)',0,100,80)
airport=st.sidebar.selectbox('Aeropuerto · solo resumen geográfico',['Todos']+sorted(h['code'] for h in payload.get('hubs',[])),format_func=airport_label)
if st.sidebar.button('Restablecer filtros'):
    for c in filters:del st.session_state[c]
    st.rerun()
d=subset(df,filters);m=metrics(d)
st.title('Puntualidad aérea de EE. UU.')
st.caption(f'{report["date_min"]} → {report["date_max"]} · Cubo agregado suministrado · 4 vistas analíticas')
st.warning(f'Calidad: {report["invalid_cause_rows"]:,} filas no concilian causas y {report["metrics"]["unclassified"]:,} operaciones carecen de categoría. Los aeropuertos y horarios son resúmenes independientes. La referencia OTP es interna.')
st.markdown(kpis_html(m,target),unsafe_allow_html=True)
if view=='Geografía':st.info('El selector de aeropuerto solo filtra esta vista. Año, mes, aerolínea y radio afectan los KPI del cubo; no afectan los resúmenes geográficos.')
if view=='Estacionalidad':st.info('El perfil horario es global. No se incluye día de semana ni matriz día×hora: el archivo no contiene el detalle necesario.')
if view=='Marco del proyecto':
    st.info('Este módulo resume la base completa 2021–2026. Los KPI superiores conservan los filtros activos; las tablas del marco presentan referencias globales.')
    st.markdown(to_markdown(project_context(df,payload)))
elif view=='Conclusiones':
    st.info('Estas cuatro conclusiones describen la base completa. Los KPI superiores conservan el filtro activo.')
    st.markdown(render_conclusions(df,payload),unsafe_allow_html=True)
elif view=='Metodología':
    st.markdown(render_cards(df,payload),unsafe_allow_html=True)
    with st.expander('Ver auditoría técnica completa'):
        st.json(audit(df,payload))
        st.markdown((ROOT/'docs/METODOLOGIA.md').read_text(encoding='utf-8'))
else:
    def show_chart(key):
        _,section,title,variables,why=next(c for c in CATALOG if c[0]==key)
        fig,note=make_chart(key,d,payload,min_ops,airport,target)
        with st.container(border=True):
            st.markdown('<h3>'+icon(CHART_ICONS[key],'chart-icon')+title+'</h3>',unsafe_allow_html=True)
            st.caption(variables)
            if fig is None:
                st.info(note)
                return
            fig.update_layout(height=HEIGHTS[key])
            if key=='map':
                st.iframe(map_html(fig,payload.get('hubs',[]),airport),height=HEIGHTS[key]+120)
            else:
                st.plotly_chart(fig,width='stretch',theme=None,key=key)
            st.markdown(f'<div class="analysis"><b>Variables:</b> {variables}<br><b>¿Por qué este gráfico?</b> {why}<br><b>Interpretación y decisión:</b> {note}</div>',unsafe_allow_html=True)
    if view=='Panorama':
        show_chart('annual')
        left,right=st.columns([1.4,1])
        with left:show_chart('season')
        with right:
            show_chart('mix')
            show_chart('haul')
    elif view=='Estacionalidad':
        show_chart('timeline')
        left,right=st.columns([1.4,1])
        with left:show_chart('uncertainty')
        with right:show_chart('hourly')
        show_chart('season')
    elif view=='Geografía':
        left,right=st.columns([1.4,1])
        with left:show_chart('map')
        with right:show_chart('hubs')
    elif view=='Aerolíneas':
        show_chart('tradeoff')
        left,right=st.columns([1.4,1])
        with left:show_chart('ranking')
        with right:show_chart('causes')
st.download_button('Descargar agregados filtrados (CSV)',d.to_csv(index=False).encode('utf-8-sig'),'vuelos_filtrados.csv','text/csv')
with st.expander('Ver datos agregados y trazabilidad'):st.dataframe(d,width='stretch')
