"""Figuras e interpretaciones que se recalculan con los filtros del cubo."""
import json
import pandas as pd
import plotly.graph_objects as go
from analytics import ROOT,CAUSES,COLORS,grouped,metrics,wilson,fmt
from ui_design import MONTH_LABELS
from labels import airline_label,airport_label

CATALOG = [
 ('annual','Panorama','Tendencia histórica de operaciones y puntualidad','Year; ops (barras); ontime / ops (%) (línea)','Barras y línea comparan volumen y nivel de servicio en ejes distintos. Comparar períodos equivalentes: 2026 termina en mayo.'),
 ('mix','Panorama','Composición del resultado operativo','ontime, delayed15, cancel, divert, Unclassified (conteos)','La dona representa proporciones de categorías excluyentes y conserva el residuo sin clasificar. delayed60 es subconjunto de delayed15.'),
 ('haul','Panorama','Puntualidad por radio de vuelo','Haul (categoría); ontime / ops (%)','Comparar radios orienta la asignación de recursos; los límites de distancia del radio no están documentados en el JSON.'),
 ('timeline','Estacionalidad','Evolución mensual observada','Year-Month; ontime / ops (%)','El orden cronológico distingue cambios en el tiempo. Los meses sin observación son huecos, nunca ceros.'),
 ('season','Estacionalidad','Evolución mensual y comparación interanual','Year, Month; ops; Σontime / Σops; cancel / ops (%)','Las curvas comparan los años por mes; con un año seleccionado se combina volumen, OTP y cancelación. La composición de aerolíneas y la cobertura pueden cambiar.'),
 ('uncertainty','Estacionalidad','Puntualidad e intervalo Wilson del 95%','Airline; ontime; ops; límite inferior y superior (%)','Las barras de error expresan precisión bajo un modelo binomial. No cuantifican sesgo ni dependencia entre vuelos.'),
 ('hourly','Estacionalidad','Demora por bloque horario · resumen independiente','hour_block (hora); avg_delay (minutos)','La línea compara el resumen horario suministrado. No hay conteos ni claves para ponderarlo o filtrarlo con el cubo.'),
 ('map','Geografía','Aeropuertos · ubicación y puntualidad','Latitud, longitud (coordenadas); otp (%); flights (conteo)','La ubicación permite explorar concentraciones espaciales. Son aeropuertos seleccionados; no se deriva un mapa estatal.'),
 ('hubs','Geografía','Aeropuertos · volumen, puntualidad y cancelación','flights (X); otp (Y, %); cancel (tamaño, %)','La dispersión compara escala y servicio; el área de burbuja aumenta con la tasa de cancelación.'),
 ('tradeoff','Aerolíneas','Aerolíneas · escala y puntualidad','Airline; ops (X); OTP (Y, %); cancelRate (tamaño, %)','Permite localizar operadores con gran exposición y menor puntualidad. Una asociación no demuestra causalidad.'),
 ('ranking','Aerolíneas','Ranking de puntualidad por aerolínea','Airline (categoría); Σontime / Σops (%)','Las barras ordenadas facilitan comparaciones. Son tasas ponderadas por operaciones; no promedios simples de porcentajes.'),
 ('causes','Aerolíneas','Minutos por causa · solo registros conciliados','carrierDelay, weatherDelay, nasDelay, secDelay, lateAirDelay (minutos)','Comparar minutos identifica focos de intervención en el subconjunto consistente. Se excluyen filas cuya suma de causas no coincide con sumDelayMin (tolerancia 1 minuto).')
]

def base(fig,x=None,y=None):
    fig.update_layout(template='plotly_dark',paper_bgcolor='#10192b',plot_bgcolor='#10192b',
                      font=dict(color='#e8eef8',family='Manrope, Arial',size=12),colorway=COLORS,
                      margin=dict(l=55,r=25,t=25,b=65),height=360,
                      legend=dict(orientation='h',y=-.22),
                      xaxis=dict(title=x,gridcolor='rgba(148,163,184,.12)'),
                      yaxis=dict(title=y,gridcolor='rgba(148,163,184,.12)'))
    return fig

def make_chart(key,d,payload,min_ops=30,airport='Todos',target=80):
    m=metrics(d)
    if key in ['map','hubs']:
        h=pd.DataFrame(payload.get('hubs',[]))
        if airport!='Todos':h=h[h.code==airport]
        if h.empty:return None,'No hay aeropuertos en el resumen.'
        worst=h.sort_values('otp').iloc[0]
        note=f'{airport_label(worst.code)} presenta la menor puntualidad del resumen mostrado: {worst.otp:.1f}%. Priorizar su diagnóstico junto con volumen y cancelación. Resumen independiente: sin fecha ni aerolínea; los filtros del cubo no se aplican y sus totales no se concilian con él.'
        if key=='map':
            coords=json.loads((ROOT/'data/airport_coords.json').read_text(encoding='utf-8'))
            h['lat']=h.code.map(lambda c:coords.get(c,[None,None])[0]);h['lon']=h.code.map(lambda c:coords.get(c,[None,None])[1])
            missing=h[h.lat.isna()].code.tolist();h=h.dropna(subset=['lat','lon'])
            f=go.Figure(go.Scattergeo(lat=h.lat,lon=h.lon,text=h.code.map(airport_label),customdata=h[['otp','flights']].values,
                mode='markers',marker=dict(size=8+20*(h.flights/h.flights.max())**.5,color=h.otp,cmin=60,cmax=100,
                colorscale=[[0,'#f07178'],[.5,'#f5b942'],[1,'#2ee6a6']],colorbar=dict(title='OTP %'),line=dict(width=1,color='#e8eef8')),
                hovertemplate='%{text}<br>OTP %{customdata[0]:.1f}%<br>Operaciones %{customdata[1]:,.0f}<extra></extra>'))
            f.update_geos(scope='usa',projection_type='albers usa',showland=True,landcolor='#162033',bgcolor='#10192b',showlakes=False)
            if missing:note+=' Sin coordenadas: '+', '.join(missing)+'.'
            return base(f),note
        f=go.Figure(go.Scatter(x=h.flights,y=h.otp,text=h.code,hovertext=h.code.map(airport_label),mode='markers+text',textposition='top center',
           customdata=h.cancel,marker=dict(size=h.cancel,sizeref=2*h.cancel.max()/(42**2),sizemin=5,color=COLORS[1],opacity=.7,line=dict(color='#e8eef8',width=1),sizemode='area'),
           hovertemplate='%{hovertext}<br>Operaciones %{x:,.0f}<br>OTP %{y:.1f}%<br>Cancelación %{customdata:.2f}%<extra></extra>'))
        return base(f,'Operaciones del resumen','OTP (%)'),note
    if key=='hourly':
        h=pd.DataFrame(payload.get('hourly',[]))
        if h.empty:return None,'No se proporcionó resumen horario.'
        h=h.sort_values('hour_block');lo=h.loc[h.avg_delay.idxmin()];hi=h.loc[h.avg_delay.idxmax()]
        note=f'El menor promedio es {lo.avg_delay:.1f} min a las {lo.hour_block:02.0f}:00 y el mayor {hi.avg_delay:.1f} min a las {hi.hour_block:02.0f}:00. El perfil no demuestra un efecto cascada. El denominador y el período del resumen no están documentados; no usarlo como promedio del cubo.'
        return base(go.Figure(go.Scatter(x=h.hour_block,y=h.avg_delay,mode='lines+markers',line_color=COLORS[1])),'Hora de salida (bloque)','Demora media del resumen (min)'),note
    if not m['ops']:return None,'No hay operaciones para esta combinación de filtros. Cambia o restablece los filtros.'
    f=go.Figure()
    if key in ['annual','timeline','season']:
        dim={'annual':'Year','timeline':'Period','season':'Month'}[key];g=grouped(d,dim)
        x=g[dim].astype(str).tolist()
        if key=='season':x=[MONTH_LABELS[int(v)-1] for v in g.Month]
        if key=='timeline':
            complete=pd.period_range(d.Period.min(),d.Period.max(),freq='M').astype(str)
            g=g.set_index('Period').reindex(complete);x=list(complete)
        if key=='annual':
            f.add_trace(go.Bar(x=x,y=g.ops,name='Operaciones',yaxis='y2',marker_color=COLORS[1],opacity=.65))
        if key=='season' and d.Year.nunique()>1:
            for i,year in enumerate(sorted(d.Year.unique())):
                yy=grouped(d[d.Year==year],'Month')
                f.add_trace(go.Scatter(x=[MONTH_LABELS[int(v)-1] for v in yy.Month],y=yy.otp,mode='lines+markers',connectgaps=False,name=str(year),line_color=(COLORS+['#b07cff'])[i%6]))
        else:
            if key=='season':
                f.add_trace(go.Bar(x=x,y=g.ops,name='Operaciones',yaxis='y2',marker_color=COLORS[1],opacity=.5))
                f.add_trace(go.Scatter(x=x,y=g.cancelRate,name='Cancelación (%)',line=dict(color=COLORS[3],dash='dot')))
            f.add_trace(go.Scatter(x=x,y=g.otp,mode='lines+markers',connectgaps=False,name='OTP',line_color=COLORS[2] if key in ['annual','season'] else COLORS[0]))
        f.add_hline(y=target,line_dash='dash',line_color=COLORS[2],annotation_text=f'Referencia interna {target}%')
        low=g.otp.idxmin();high=g.otp.idxmax()
        lowlabel=x[list(g.index).index(low)];highlabel=x[list(g.index).index(high)]
        note=f'La mayor puntualidad es {g.otp.max():.2f}% ({highlabel}) y la menor {g.otp.min():.2f}% ({lowlabel}): brecha de {g.otp.max()-g.otp.min():.2f} puntos porcentuales. Revisar capacidad en los períodos más bajos. Los años tienen cobertura desigual (2026: enero-mayo); filtra el mismo mes para comparar años.'
        if key=='season':note='Lectura del agregado filtrado por mes: '+note
        f=base(f,{'Year':'Año','Month':'Mes','Period':'Período'}[dim],'OTP (%)')
        if key in ['annual','season']:
            f.update_layout(showlegend=True,legend=dict(orientation='h',y=-.25),margin=dict(l=50,r=65,t=30,b=85))
        if key=='annual' or (key=='season' and d.Year.nunique()==1):
            f.update_layout(yaxis2=dict(title='Operaciones',overlaying='y',side='right',showgrid=False),yaxis=dict(range=[0,100]))
        return f,note
    if key=='mix':
        names=['Puntuales','Demora ≥15 min','Cancelados','Desviados','Sin clasificar'];cols=['ontime','delayed15','cancel','divert','Unclassified'];v=d[cols].sum()
        f.add_trace(go.Pie(labels=names,values=v,hole=.62,marker_colors=[COLORS[0],COLORS[2],COLORS[3],COLORS[4],'#94a3b8'],textinfo='percent',textposition='inside',sort=False))
        note=f'{fmt(m["otp"],2)}% de las operaciones son puntuales. Hay {int(v.iloc[-1]):,} operaciones sin clasificar; se conservan explícitamente. No sumar demora ≥60 a ≥15 porque se superponen. Decisión: revisar incidencias antes de asignar recursos.'
        return base(f).update_layout(showlegend=True,legend=dict(orientation='v',x=1,y=.5),margin=dict(l=8,r=110,t=15,b=15)),note
    if key=='haul':
        g=grouped(d,'Haul');g=g[g.ops>=min_ops]
        if g.empty:return None,'Ningún radio alcanza el soporte mínimo.'
        best=g.loc[g.otp.idxmax()];worst=g.loc[g.otp.idxmin()]
        f.add_trace(go.Bar(x=g.Haul,y=g.otp,marker_color=COLORS[:len(g)]))
        return base(f,'Radio declarado','OTP (%)'),f'{best.Haul} registra {best.otp:.2f}% y {worst.Haul} {worst.otp:.2f}%. Investigar diferencias de rutas y operadores antes de atribuir el resultado al radio. Soporte: ≥{min_ops:,} operaciones.'
    if key in ['ranking','uncertainty','tradeoff']:
        g=grouped(d,'Airline');g=g[g.ops>=min_ops].sort_values('otp');g['AirlineLabel']=g.Airline.map(airline_label)
        if g.empty:return None,'Ninguna aerolínea alcanza el soporte mínimo.'
        best=g.iloc[-1];worst=g.iloc[0]
        note=f'{airline_label(best.Airline)} lidera con {best.otp:.2f}% (N={best.ops:,.0f}); {airline_label(worst.Airline)} registra {worst.otp:.2f}% (N={worst.ops:,.0f}). Investigar la mezcla de rutas y períodos: el ranking no ajusta confusores. Soporte mínimo: {min_ops:,} operaciones.'
        if key=='tradeoff':
            f.add_trace(go.Scatter(x=g.ops,y=g.otp,text=g.Airline,hovertext=g.AirlineLabel,mode='markers+text',textposition='top center',
                customdata=g.cancelRate,marker=dict(size=g.cancelRate,sizeref=2*max(.001,g.cancelRate.max())/(42**2),sizemin=5,color=COLORS[1],opacity=.7,line=dict(color='#e8eef8',width=1),sizemode='area'),
                hovertemplate='%{hovertext}<br>N %{x:,.0f}<br>OTP %{y:.2f}%<br>Cancelación %{customdata:.2f}%<extra></extra>'))
            return base(f,'Operaciones','OTP (%)'),note+' La escala no demuestra resiliencia causal.'
        errors=None
        if key=='uncertainty':
            intervals=[wilson(r.ontime,r.ops) for r in g.itertuples()]
            errors=dict(type='data',symmetric=False,array=[hi-p for (lo,hi),p in zip(intervals,g.otp)],arrayminus=[p-lo for (lo,hi),p in zip(intervals,g.otp)])
            note+=' IC Wilson 95% bajo independencia binomial; estos agregados no permiten estimar correlación por aeropuerto/día. No es un intervalo predictivo; con millones de vuelos puede ser muy estrecho.'
        f.add_trace(go.Bar(x=g.otp,y=g.AirlineLabel,orientation='h',marker_color=COLORS[0],error_x=errors))
        f.update_layout(height=500)
        return base(f,'OTP (%)','Aerolínea').update_layout(height=640,margin=dict(l=190,r=25,t=25,b=65)),note
    if key=='causes':
        valid=d[d.CauseValid];v=valid[list(CAUSES)].sum().sort_values(ascending=False)
        if not v.sum():return None,'No hay minutos por causa en registros conciliados.'
        f.add_trace(go.Bar(x=[CAUSES[c] for c in v.index],y=v.values,marker_color=COLORS))
        note=f'{CAUSES[v.index[0]]} concentra {100*v.iloc[0]/v.sum():.2f}% de los minutos conciliados. Priorizar el diagnóstico de esa causa. Se excluyen {(~d.CauseValid).sum():,} filas; cobertura de operaciones: {m["causeCoverage"]:.2f}%. El hallazgo solo describe el subconjunto válido, no todo el universo.'
        return base(f,None,'Minutos de demora'),note
    raise KeyError(key)
