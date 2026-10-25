/* Mapa de calles con Leaflet. La alternativa vectorial no necesita red. */
(function(){
 const maps=[];
 function mount(plot,options){
  const card=plot.parentElement,controls=document.createElement('div');controls.className='map-controls';
  const online=document.createElement('button'),offline=document.createElement('button');
  online.textContent='Mapa real · calles';offline.textContent='Mapa sin conexión';
  const provider=document.createElement('select');provider.setAttribute('aria-label','Fondo cartográfico');provider.style.width='auto';provider.add(new Option('Satelital · Esri','dark'));provider.add(new Option('Calles · Esri','streets'));provider.value=window.FLIGHT_BASEMAP||'streets';
  controls.append(online,offline,provider);card.insertBefore(controls,plot);
  const panel=document.createElement('div');panel.className='real-map';panel.style.height=(options.height||440)+'px';card.insertBefore(panel,plot);
  const status=document.createElement('p');status.className='map-status';status.setAttribute('role','status');card.insertBefore(status,plot);
  let map,loaded=0,errors=0,mode='offline',dark,streets;
  function choose(real){
   panel.classList.remove('dark-tiles');
   mode=real?'real':'offline';online.classList.toggle('active',real);offline.classList.toggle('active',!real);
   online.setAttribute('aria-pressed',String(real));offline.setAttribute('aria-pressed',String(!real));
   panel.hidden=!real;plot.hidden=real;plot.style.display=real?'none':'block';
   if(!real){status.textContent='Mapa vectorial local: disponible sin Internet. Nombre completo al pasar el cursor.';if(window.Plotly)Plotly.Plots.resize(plot);return;}
   if(!window.L){choose(false);status.textContent='No se pudo iniciar el mapa de calles. Se muestra el mapa sin conexión.';return;}
   if(map&&!loaded){errors=0;map.eachLayer(layer=>{if(layer instanceof L.TileLayer)layer.redraw();});status.textContent='Reintentando cargar la cartografía; se necesita Internet.';}
   if(map&&loaded)status.textContent='Mapa real activo: acerca el zoom y pulsa un aeropuerto para ver su nombre e indicadores.';
   if(!map){
    status.textContent='Cargando calles y ciudades. Esta capa requiere Internet.';
    map=L.map(panel,{scrollWheelZoom:false});maps.push(map);
    const attribution='&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors';
    dark=L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',{maxZoom:19,attribution:'Tiles &copy; Esri — Source: Esri, Vantor, Earthstar Geographics, GIS User Community'});
    streets=L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',{maxZoom:19,attribution:'Tiles &copy; Esri — Sources: Esri, HERE, Garmin, USGS, Intermap, INCREMENT P, NRCan, Esri Japan, METI, Esri China, Esri Korea, Esri Thailand, NGCC, OpenStreetMap contributors, GIS User Community'});
    function loadedTile(){loaded++;if(mode==='real')status.textContent='Mapa real activo: acerca el zoom y pulsa un aeropuerto para ver su nombre e indicadores.';}
    function failedTile(){errors++;if(errors>=3&&!loaded&&mode==='real'){choose(false);status.textContent='Sin acceso a las teselas de calles. Se mantiene el mapa sin conexión; puedes volver a intentar “Mapa real”.';}}
    for(const layer of [dark,streets])layer.on('tileload',loadedTile).on('tileerror',failedTile);
    (provider.value==='streets'?streets:dark).addTo(map);L.control.layers({'Satelital · Esri':dark,'Calles · Esri':streets},null,{collapsed:true}).addTo(map);
    map.on('baselayerchange',event=>{provider.value=event.layer===dark?'dark':'streets';window.FLIGHT_BASEMAP=provider.value;panel.classList.remove('dark-tiles');});
    const valid=(options.hubs||[]).filter(h=>options.coords[h.code]);const max=Math.max(1,...valid.map(h=>h.flights));
    for(const h of valid){
     const location=options.coords[h.code],label=h.code+' — '+(options.names[h.code]||'Nombre no disponible');
     const v=Math.max(0,Math.min(1,(h.otp-60)/40)),stops=v<.5?[[240,113,120],[245,185,66],v*2]:[[245,185,66],[46,230,166],(v-.5)*2];
     const color='rgb('+stops[0].map((x,i)=>Math.round(x+(stops[1][i]-x)*stops[2])).join(',')+')';
     const marker=L.circleMarker(location,{radius:5+15*Math.sqrt(h.flights/max),color:'#e8eef8',weight:1,fillColor:color,fillOpacity:.85}).addTo(map);
     marker.bindTooltip(label);
     const content=document.createElement('div'),title=document.createElement('strong');title.textContent=label;content.append(title);
     for(const line of ['Operaciones: '+Number(h.flights).toLocaleString('es-PE'),'Puntualidad: '+h.otp.toFixed(1)+'%','Cancelación: '+h.cancel.toFixed(2)+'%','Resumen independiente: sin fecha ni aerolínea.']){const p=document.createElement('div');p.textContent=line;content.append(p);}
     if(options.onSelect){const button=document.createElement('button');button.textContent='Filtrar este aeropuerto';button.onclick=()=>options.onSelect(h.code);content.append(button);}
     marker.bindPopup(content,{maxWidth:330});
    }
    if(valid.length===1)map.setView(options.coords[valid[0].code],10);
    else if(valid.length>1)map.fitBounds(valid.map(h=>options.coords[h.code]),{padding:[25,25],maxZoom:5});
    else map.setView([37,-103],4);
    const legend=L.control({position:'bottomleft'});legend.onAdd=()=>{const div=L.DomUtil.create('div','map-legend');div.innerHTML='<b>OTP (%)</b><br><span style="background:#f07178"></span>60 <span style="background:#f5b942;margin-left:10px"></span>80 <span style="background:#2ee6a6;margin-left:10px"></span>100<br>Tamaño: operaciones';return div;};legend.addTo(map);
   }
   setTimeout(()=>map.invalidateSize(),50);
  }
  provider.onchange=()=>{window.FLIGHT_BASEMAP=provider.value;loaded=0;errors=0;if(map){map.removeLayer(dark);map.removeLayer(streets);(provider.value==='streets'?streets:dark).addTo(map);}choose(true);};
  online.onclick=()=>choose(true);offline.onclick=()=>choose(false);choose(!options.offlineOnly);
  return {choose,map:()=>map};
 }
 window.FlightMap={mount,disposeAll(){for(const m of maps.splice(0))try{m.remove();}catch{}}};
})();
