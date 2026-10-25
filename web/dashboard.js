/* Métricas equivalentes a analytics.py. No usa caché ni datos de demostración. */
'use strict';
const M=['ops','ontime','delayed15','delayed60','cancel','divert','sumDelayMin','carrierDelay','weatherDelay','nasDelay','secDelay','lateAirDelay'];
const causes={carrierDelay:'Aerolínea',weatherDelay:'Clima',nasDelay:'Sistema aéreo (NAS)',secDelay:'Seguridad',lateAirDelay:'Aeronave previa'};
const palette=['#2ee6a6','#2ec4b6','#f5b942','#f07178','#5b8def'];
let DATA=JSON.parse(document.getElementById('dataset').textContent);
const COORDS=JSON.parse(document.getElementById('coords').textContent);
const CATALOG=JSON.parse(document.getElementById('catalog').textContent);
const NAMES=JSON.parse(document.getElementById('names').textContent);
const airLabel=c=>c+' — '+(NAMES.carriers[c]||'Nombre no disponible');
const portLabel=c=>c+' — '+(NAMES.airports[c]||'Nombre no disponible');
const ICONS=JSON.parse(document.getElementById('icons').textContent);
const UI=JSON.parse(document.getElementById('ui-config').textContent);
const MONTHS=['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
const MONTH_NAMES=['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
const icon=(name,cls='ico')=>`<span class="${cls}" aria-hidden="true">${ICONS[name]}</span>`;
let currentView='Panorama';
const $=s=>document.getElementById(s);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=(n,k=2)=>n===null||!Number.isFinite(n)?'Sin datos':n.toLocaleString('es-PE',{maximumFractionDigits:k,minimumFractionDigits:k});
const ratio=(a,b,s=100)=>b?a/b*s:null;
function prepare(payload){
 if(!Array.isArray(payload.cube)||!payload.cube.length)throw Error('Falta el cubo de datos.');
 const seen=new Set();
 return payload.cube.map((row,i)=>{
  const r={...row};
  for(const k of [...M,'Year','Month'])if(typeof r[k]!=='number'||!Number.isFinite(r[k])||r[k]<0)throw Error('Campo numérico inválido: '+k);
  for(const k of ['Airline','OriginState','Haul'])if(typeof r[k]!=='string'||!r[k])throw Error('Dimensión inválida: '+k);
  if(!Number.isInteger(r.Month)||r.Month<1||r.Month>12||!Number.isInteger(r.Year)||r.delayed60>r.delayed15)throw Error('Mes, año o jerarquía de demora inválidos.');
  for(const k of ['ops','ontime','delayed15','delayed60','cancel','divert'])if(!Number.isInteger(r[k]))throw Error('Conteo no entero: '+k);
  const id=[r.Year,r.Month,r.Airline,r.OriginState,r.Haul].join('|');if(seen.has(id))throw Error('Claves de agregado duplicadas.');seen.add(id);
  r.Unclassified=r.ops-r.ontime-r.delayed15-r.cancel-r.divert;
  if(r.Unclassified<0)throw Error('Categorías superiores a operaciones.');
  r.CauseGap=Object.keys(causes).reduce((s,k)=>s+r[k],0)-r.sumDelayMin;r.CauseValid=Math.abs(r.CauseGap)<=1;
  r.Period=`${r.Year}-${String(r.Month).padStart(2,'0')}`;r.RowId=i+1;r.AirlineName=NAMES.carriers[r.Airline]||'Nombre no disponible';r.AirlineLabel=airLabel(r.Airline);return r;
 });
}
let ROWS=prepare(DATA);
function aggregate(rows){
 const s=Object.fromEntries([...M,'Unclassified'].map(k=>[k,0]));let good=0;
 rows.forEach(r=>{Object.keys(s).forEach(k=>s[k]+=r[k]);if(r.CauseValid)good+=r.ops;});
 return {...s,otp:ratio(s.ontime,s.ops),delay15:ratio(s.delayed15,s.ops),delay60:ratio(s.delayed60,s.ops),cancelRate:ratio(s.cancel,s.ops),divertRate:ratio(s.divert,s.ops),avgDelay:ratio(s.sumDelayMin,s.delayed15,1),unclassified:s.Unclassified,causeCoverage:ratio(good,s.ops)};
}
function filtered(){return ROWS.filter(r=>['Year','Month','Airline','Haul'].every(k=>$(k).value==='Todos'||String(r[k])===$(k).value));}
function grouped(rows,key){return [...new Set(rows.map(r=>r[key]))].sort((a,b)=>typeof a==='number'?a-b:String(a).localeCompare(String(b))).map(v=>({[key]:v,...aggregate(rows.filter(r=>r[key]===v))}));}
function wilson(k,n){if(!n)return [null,null];const z=1.96,p=k/n,den=1+z*z/n,c=(p+z*z/(2*n))/den,h=z*Math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den;return [100*(c-h),100*(c+h)];}
const base={autosize:true,paper_bgcolor:'#10192b',plot_bgcolor:'#10192b',font:{color:'#e8eef8',family:'Manrope,system-ui,sans-serif',size:12},margin:{t:28,b:85,l:65,r:40},height:360,colorway:palette,showlegend:false,xaxis:{gridcolor:'rgba(148,163,184,.12)'},yaxis:{gridcolor:'rgba(148,163,184,.12)'},legend:{orientation:'h',y:-.2}};
function chart(key,rows){
 const stats=aggregate(rows),min=Number($('support').value)||30,target=Number($('target').value),ap=$('airport').value;
 const obj={traces:[],layout:structuredClone(base),note:''};
 const axes=(x,y)=>{obj.layout.xaxis.title={text:x};obj.layout.yaxis.title={text:y};};
 if(['map','hubs'].includes(key)){
  let h=(DATA.hubs||[]).filter(r=>ap==='Todos'||r.code===ap);if(!h.length)return {...obj,empty:true,note:'No hay aeropuertos en el resumen.'};
  const worst=[...h].sort((a,b)=>a.otp-b.otp)[0];
  obj.note=`${portLabel(worst.code)} presenta la menor puntualidad del resumen: ${fmt(worst.otp)}%. Priorizar su diagnóstico junto con volumen y cancelación. Resumen independiente, sin fecha ni aerolínea: los filtros del cubo no se aplican y sus totales no se concilian con él.`;
  if(key==='map'){
   const missing=h.filter(r=>!COORDS[r.code]);h=h.filter(r=>COORDS[r.code]);
   obj.traces=[{type:'scattergeo',lat:h.map(r=>COORDS[r.code][0]),lon:h.map(r=>COORDS[r.code][1]),text:h.map(r=>portLabel(r.code)),customdata:h.map(r=>[r.otp,r.flights]),mode:'markers',marker:{size:h.map(r=>8+20*Math.sqrt(r.flights/Math.max(...h.map(r=>r.flights)))),color:h.map(r=>r.otp),cmin:60,cmax:100,colorscale:[[0,palette[3]],[.5,palette[2]],[1,palette[0]]],colorbar:{title:'OTP %'},line:{width:1,color:'#e8eef8'}},hovertemplate:'%{text}<br>OTP %{customdata[0]:.1f}%<br>Operaciones %{customdata[1]:,.0f}<extra></extra>'}];
   obj.layout.geo={scope:'usa',projection:{type:'albers usa'},showland:true,landcolor:'#162033',bgcolor:'#10192b',showlakes:false};obj.layout.height=460;
   if(missing.length)obj.note+=' Sin coordenadas: '+missing.map(r=>r.code).join(', ')+'.';
  }else{
   obj.traces=[{type:'scatter',mode:'markers+text',x:h.map(r=>r.flights),y:h.map(r=>r.otp),text:h.map(r=>r.code),hovertext:h.map(r=>portLabel(r.code)),textposition:'top center',customdata:h.map(r=>r.cancel),marker:{size:h.map(r=>r.cancel),sizemode:'area',sizeref:2*Math.max(...h.map(r=>r.cancel))/(42*42),sizemin:5,color:palette[1],opacity:.7,line:{color:'#e8eef8',width:1}},hovertemplate:'%{hovertext}<br>N %{x:,.0f}<br>OTP %{y:.2f}%<br>Cancelación %{customdata:.2f}%<extra></extra>'}];axes('Operaciones del resumen','OTP (%)');
  }return obj;
 }
 if(key==='hourly'){
  const h=[...(DATA.hourly||[])].sort((a,b)=>a.hour_block-b.hour_block);if(!h.length)return {...obj,empty:true,note:'No se proporcionó resumen horario.'};
  const lo=[...h].sort((a,b)=>a.avg_delay-b.avg_delay)[0],hi=[...h].sort((a,b)=>b.avg_delay-a.avg_delay)[0];
  obj.traces=[{type:'scatter',mode:'lines+markers',x:h.map(r=>r.hour_block),y:h.map(r=>r.avg_delay),line:{color:palette[1]}}];axes('Hora de salida (bloque)','Demora media del resumen (min)');
  obj.note=`El menor promedio es ${fmt(lo.avg_delay,1)} min a las ${lo.hour_block}:00 y el mayor ${fmt(hi.avg_delay,1)} min a las ${hi.hour_block}:00. Este perfil no demuestra un efecto cascada. No hay conteos ni período documentados: no ponderar ni cruzar con el cubo.`;return obj;
 }
 if(!stats.ops)return {...obj,empty:true,note:'No hay operaciones para esta combinación. Cambia o restablece los filtros.'};
 if(['annual','timeline','season'].includes(key)){
  const dim={annual:'Year',timeline:'Period',season:'Month'}[key],g=grouped(rows,dim);
  let xx=g.map(r=>String(r[dim])),yy=g.map(r=>r.otp);
  if(key==='season')xx=g.map(r=>MONTHS[r.Month-1]);
  if(key==='timeline'){
   const original=new Map(g.map(r=>[r.Period,r.otp]));xx=[];let [y,m]=g[0].Period.split('-').map(Number);const end=g[g.length-1].Period;
   while(`${y}-${String(m).padStart(2,'0')}`<=end){xx.push(`${y}-${String(m).padStart(2,'0')}`);m++;if(m===13){m=1;y++;}}
   yy=xx.map(p=>original.get(p)??null);
  }
  obj.traces=[{type:'scatter',mode:'lines+markers',x:xx,y:yy,connectgaps:false,line:{color:palette[0]},name:'OTP'}];
  if(key==='annual'){
   obj.traces=[{type:'bar',x:xx,y:g.map(r=>r.ops),name:'Operaciones',yaxis:'y2',marker:{color:palette[1]},opacity:.65},{...obj.traces[0],line:{color:palette[2],width:3}}];
   obj.layout.yaxis2={title:{text:'Operaciones'},overlaying:'y',side:'right',showgrid:false};obj.layout.yaxis.range=[0,100];obj.layout.showlegend=true;obj.layout.margin.r=65;
  }
  if(key==='season'){
   const years=[...new Set(rows.map(r=>r.Year))].sort((a,b)=>a-b);
   if(years.length>1)obj.traces=years.map((y,i)=>{const sub=grouped(rows.filter(r=>r.Year===y),'Month');return {type:'scatter',mode:'lines+markers',x:sub.map(r=>MONTHS[r.Month-1]),y:sub.map(r=>r.otp),connectgaps:false,name:String(y),line:{color:[...palette,'#b07cff'][i%6],width:2.5}};});
   else{
    obj.traces=[{type:'bar',x:xx,y:g.map(r=>r.ops),name:'Operaciones',yaxis:'y2',marker:{color:palette[1]},opacity:.5},{...obj.traces[0],line:{color:palette[2],width:3}},{type:'scatter',x:xx,y:g.map(r=>r.cancelRate),name:'Cancelación (%)',line:{color:palette[3],dash:'dot'}}];
    obj.layout.yaxis2={title:{text:'Operaciones'},overlaying:'y',side:'right',showgrid:false};obj.layout.yaxis.range=[0,100];obj.layout.margin.r=65;
   }obj.layout.showlegend=true;
  }
  obj.layout.shapes=[{type:'line',xref:'paper',x0:0,x1:1,y0:target,y1:target,line:{dash:'dash',color:palette[2]}}];
  obj.layout.annotations=[{xref:'paper',x:0,y:target,text:`Referencia interna ${target}%`,showarrow:false,yshift:12,font:{color:palette[2]}}];axes({Year:'Año',Month:'Mes',Period:'Período'}[dim],'OTP (%)');
  const sorted=[...g].sort((a,b)=>a.otp-b.otp),lo=sorted[0],hi=sorted[sorted.length-1];
  obj.note=(key==='season'?'Lectura del agregado filtrado por mes: ':'')+`La mayor puntualidad es ${fmt(hi.otp)}% (${hi[dim]}) y la menor ${fmt(lo.otp)}% (${lo[dim]}): brecha de ${fmt(hi.otp-lo.otp)} puntos porcentuales. Revisar capacidad en los períodos bajos. Cobertura desigual: 2026 llega a mayo; filtra el mismo mes para comparar años.`;return obj;
 }
 if(key==='mix'){
  const cols=['ontime','delayed15','cancel','divert','Unclassified'];obj.traces=[{type:'pie',hole:.62,labels:['Puntuales','Demora ≥15','Cancelados','Desviados','Sin clasificar'],values:cols.map(k=>stats[k]),marker:{colors:[palette[0],palette[2],palette[3],palette[4],'#94a3b8']},textinfo:'percent',textposition:'inside',sort:false}];obj.layout.showlegend=true;obj.layout.legend={orientation:'v',x:1,y:.5,font:{size:10}};obj.layout.margin={l:8,r:110,t:15,b:15};
  obj.note=`${fmt(stats.otp)}% de las operaciones son puntuales. Se conservan ${fmt(stats.Unclassified,0)} operaciones sin clasificar. No sumar demora ≥60 a ≥15: son categorías superpuestas. Revisar incidencias antes de asignar recursos.`;return obj;
 }
 if(key==='haul'){
  const g=grouped(rows,'Haul').filter(r=>r.ops>=min);if(!g.length)return {...obj,empty:true,note:'Ningún radio alcanza el soporte mínimo.'};
  const sorted=[...g].sort((a,b)=>a.otp-b.otp),lo=sorted[0],hi=sorted[sorted.length-1];
  obj.traces=[{type:'bar',x:g.map(r=>r.Haul),y:g.map(r=>r.otp),marker:{color:palette}}];axes('Radio declarado','OTP (%)');
  obj.note=`${hi.Haul} registra ${fmt(hi.otp)}% y ${lo.Haul} ${fmt(lo.otp)}%. Investigar rutas y operadores antes de atribuir la diferencia al radio. Soporte: ≥${fmt(min,0)} operaciones.`;return obj;
 }
 if(['tradeoff','ranking','uncertainty'].includes(key)){
  const g=grouped(rows,'Airline').filter(r=>r.ops>=min).sort((a,b)=>a.otp-b.otp);if(!g.length)return {...obj,empty:true,note:'Ninguna aerolínea alcanza el soporte mínimo.'};
  const hi=g[g.length-1],lo=g[0];obj.note=`${airLabel(hi.Airline)} lidera con ${fmt(hi.otp)}% (N=${fmt(hi.ops,0)}); ${airLabel(lo.Airline)} registra ${fmt(lo.otp)}% (N=${fmt(lo.ops,0)}). Investigar mezcla de rutas y períodos: el ranking no ajusta confusores. Soporte mínimo: ${fmt(min,0)} operaciones.`;
  if(key==='tradeoff'){
   obj.traces=[{type:'scatter',mode:'markers+text',x:g.map(r=>r.ops),y:g.map(r=>r.otp),text:g.map(r=>r.Airline),hovertext:g.map(r=>airLabel(r.Airline)),textposition:'top center',customdata:g.map(r=>r.cancelRate),marker:{size:g.map(r=>r.cancelRate),sizemode:'area',sizeref:2*Math.max(.001,...g.map(r=>r.cancelRate))/(42*42),sizemin:5,color:palette[1],opacity:.7,line:{color:'#e8eef8',width:1}},hovertemplate:'%{hovertext}<br>N %{x:,.0f}<br>OTP %{y:.2f}%<br>Cancelación %{customdata:.2f}%<extra></extra>'}];axes('Operaciones','OTP (%)');obj.note+=' La escala no demuestra resiliencia causal.';
  }else{
   const t={type:'bar',orientation:'h',x:g.map(r=>r.otp),y:g.map(r=>airLabel(r.Airline)),marker:{color:palette[0]}};
   if(key==='uncertainty'){const intervals=g.map(r=>wilson(r.ontime,r.ops));t.error_x={type:'data',symmetric:false,array:intervals.map((v,i)=>v[1]-g[i].otp),arrayminus:intervals.map((v,i)=>g[i].otp-v[0])};obj.note+=' IC Wilson 95% bajo independencia binomial. No cuantifica sesgo, correlación entre vuelos ni desempeño futuro; puede ser muy estrecho con grandes volúmenes.';}
   obj.traces=[t];obj.layout.height=640;obj.layout.margin.l=190;axes('OTP (%)','Aerolínea');
  }return obj;
 }
 if(key==='causes'){
  const valid=rows.filter(r=>r.CauseValid),s=aggregate(valid),v=Object.keys(causes).map(k=>({k,v:s[k]})).sort((a,b)=>b.v-a.v),total=v.reduce((a,r)=>a+r.v,0);
  if(!total)return {...obj,empty:true,note:'No hay minutos por causa en registros conciliados.'};
  obj.traces=[{type:'bar',x:v.map(r=>causes[r.k]),y:v.map(r=>r.v),marker:{color:palette}}];axes('Causa reportada','Minutos de demora');
  obj.note=`${causes[v[0].k]} concentra ${fmt(100*v[0].v/total)}% de los minutos conciliados. Priorizar su diagnóstico. Se excluyen ${rows.length-valid.length} filas; cobertura de operaciones ${fmt(stats.causeCoverage)}%. Describe únicamente el subconjunto válido.`;return obj;
 }
 throw Error('Gráfico desconocido: '+key);
}
function populate(){
 for(const key of ['Year','Month','Airline','Haul']){
  $(key).replaceChildren(new Option('Todos','Todos'));
  [...new Set(ROWS.map(r=>r[key]))].sort((a,b)=>typeof a==='number'?a-b:String(a).localeCompare(String(b))).forEach(v=>$(key).add(new Option(key==='Airline'?airLabel(v):key==='Month'?MONTH_NAMES[Number(v)-1]:String(v),String(v))));
 }
 $('airport').replaceChildren(new Option('Todos','Todos'));(DATA.hubs||[]).forEach(h=>$('airport').add(new Option(portLabel(h.code),h.code)));
 const nbad=ROWS.filter(r=>!r.CauseValid).length,un=aggregate(ROWS).Unclassified;
 $('quality').textContent=`Calidad: ${nbad} filas no concilian causas; ${fmt(un,0)} operaciones sin categoría. No se cruza el resumen semanal u horario con el cubo. La referencia OTP es interna y modificable.`;
 const periods=ROWS.map(r=>r.Period).sort();$('coverage').textContent=`Cubo agregado suministrado · ${periods[0]} a ${periods[periods.length-1]} · 4 vistas analíticas`;
}
let renderTask=Promise.resolve();
async function draw(){
 if(window.FlightMap)FlightMap.disposeAll();
 const rows=filtered(),s=aggregate(rows);
 for(const key of ['Airline','airport'])$(key).title=$(key).selectedOptions[0]?.textContent||'';
 $('kpis').innerHTML=UI.kpis.map(([key,label,dec,unit,ic,badge,foot],i)=>{
  const v=s[key],width=v!==null&&unit==='%'?Math.max(0,Math.min(100,v)):0;
  if(key==='otp')badge=v===null?'Sin datos':`${v>=Number($('target').value)?'Cumple':'Bajo'} ref. ${$('target').value}%`;
  return `<article class="kpi t${UI.classes[i]}"><div class="kpi-h">${icon(ic)}<span class="badge">${esc(badge)}</span></div><div class="k">${esc(label)}</div><div class="v">${fmt(v,dec)}${v===null?'':unit}</div><div class="kpi-foot">${esc(foot)}</div><div class="meter" aria-hidden="true"><span style="width:${width}%"></span></div></article>`;
 }).join('');
 $('scope').textContent=currentView==='Geografía'?'Aeropuertos: resumen independiente. Solo se aplica el selector de aeropuerto; no se cruzan año, mes, aerolínea ni radio.':currentView==='Estacionalidad'?'Series del cubo filtrado. El perfil horario es independiente y conserva el resumen global.':'KPI y gráficos del cubo se recalculan con los filtros. Soporte mínimo afecta rankings, radios e intervalos.';
 $('heading').textContent=currentView;document.querySelectorAll('nav button').forEach(b=>b.classList.toggle('active',b.dataset.view===currentView));
 $('plots').innerHTML='';$('methodology').hidden=currentView!=='Metodología';
 $('conclusions').hidden=currentView!=='Conclusiones';
 $('project-context').hidden=currentView!=='Marco del proyecto';
 if(currentView==='Conclusiones'){
  $('scope').textContent='Cuatro conclusiones y recomendaciones de la base completa de la carga inicial 2021–2026. Los KPI superiores conservan el filtro activo; al cambiar el JSON, regenera esta síntesis para actualizarla.';
  return;
 }
 if(currentView==='Marco del proyecto'){
  $('scope').textContent='Marco AeroPulse actualizado a la carga inicial 2021–2026: referencias de la base completa, independientes de los filtros. Los KPI superiores sí responden al corte activo. Si cargas otro JSON, consulta sus KPI y regenera el marco para actualizar estas referencias.';
  return;
 }
 if(currentView==='Metodología')return;
 const slot=k=>`<div data-slot="${k}"></div>`;
 const layouts={Panorama:slot('annual')+`<div class="grid-2">${slot('season')}<div>${slot('mix')}${slot('haul')}</div></div>`,Estacionalidad:slot('timeline')+`<div class="grid-2">${slot('uncertainty')}${slot('hourly')}</div>`+slot('season'),Geografía:`<div class="grid-2">${slot('map')}${slot('hubs')}</div>`,Aerolíneas:slot('tradeoff')+`<div class="grid-2">${slot('ranking')}${slot('causes')}</div>`};
 $('plots').innerHTML=layouts[currentView]||'';
 for(const key of UI.views[currentView]||[]){
  const [,section,title,variables,why]=CATALOG.find(c=>c[0]===key);
  const result=chart(key,rows),article=document.createElement('article');article.className='card';
  article.innerHTML=`<h3>${icon(UI.charts[key],'chart-icon')}${esc(title)}</h3><p class="note">${esc(variables)}</p><div class="plot" id="plot-${key}"></div><p class="interp"><strong>Variables:</strong> ${esc(variables)}<br><strong>¿Por qué este gráfico?</strong> ${esc(why)}<br><strong>Interpretación y decisión:</strong> ${esc(result.note)}</p>`;$('plots').querySelector(`[data-slot="${key}"]`).appendChild(article);
  if(!result.empty){
   result.layout.width=article.clientWidth-12;result.layout.height=UI.heights[key];
   await Plotly.newPlot(`plot-${key}`,result.traces,result.layout,{responsive:true,displaylogo:false,toImageButtonOptions:{format:'png',scale:2}});
   if(key==='map'&&window.FlightMap)FlightMap.mount($(`plot-${key}`),{hubs:(DATA.hubs||[]).filter(h=>$('airport').value==='Todos'||h.code===$('airport').value),coords:COORDS,names:NAMES.airports,height:UI.heights.map,offlineOnly:window.FLIGHTS_OFFLINE===true,onSelect:code=>{$('airport').value=code;render();}});
   $(`plot-${key}`).on('plotly_click',event=>{
    const p=event.points[0];let field,value;
    if(key==='annual'){field='Year';value=p.x;}
    if(key==='season'){field='Month';value=MONTHS.indexOf(p.x)+1;}
    if(key==='ranking'){field='Airline';value=String(p.y).split(' — ')[0];}
    if(key==='haul'){field='Haul';value=p.x;}
    if(key==='map'||key==='hubs'){field='airport';value=String(p.text).split(' — ')[0];}
    if(field&&[...$(field).options].some(o=>o.value===String(value))){$(field).value=String(value);render();}
   });
  }
 }
}
function render(){renderTask=renderTask.catch(()=>{}).then(draw).catch(e=>{$('quality').textContent='Error de visualización: '+e.message;console.error(e);});return renderTask;}
document.querySelectorAll('nav button').forEach(b=>b.onclick=()=>{currentView=b.dataset.view;render();});
document.querySelectorAll('select,input[type=number],input[type=range]').forEach(el=>el.onchange=render);
$('reset').onclick=()=>{['Year','Month','Airline','Haul','airport'].forEach(k=>$(k).value='Todos');$('support').value=30;$('target').value=80;render();};
$('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();}catch(e){$('quality').textContent='El navegador no permite pantalla completa en este contexto.';}};
$('export').onclick=()=>{
 const rows=filtered();if(!rows.length){alert('No hay filas para exportar.');return;}const fields=Object.keys(rows[0]);
 const csv='\uFEFF'+fields.join(',')+'\n'+rows.map(r=>fields.map(k=>JSON.stringify(r[k])).join(',')).join('\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'})),a=document.createElement('a');a.href=url;a.download='vuelos_filtrados.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
};
$('file').onchange=async e=>{try{const payload=JSON.parse(await e.target.files[0].text()),rows=prepare(payload);DATA=payload;ROWS=rows;populate();await render();}catch(err){alert('Archivo rechazado: '+err.message);}};
window.USFlights={aggregate,grouped,wilson,prepare,chart,getRows:()=>ROWS,getFiltered:filtered};
let resizeTimer;window.addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>document.querySelectorAll('.js-plotly-plot').forEach(p=>{if(p._fullLayout&&p._fullLayout._size&&p.clientWidth>0)Plotly.relayout(p,{width:p.clientWidth});}),150);});
populate();render();
