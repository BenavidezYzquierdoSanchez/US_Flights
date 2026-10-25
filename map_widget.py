"""Mapa portátil para el iframe de Streamlit; comparte el motor web."""
import json
from analytics import ROOT
from labels import AIRPORTS
def map_html(figure,hubs,airport='Todos'):
    safe=lambda x:json.dumps(x,ensure_ascii=False).replace('</','<\\/')
    doc=figure.to_html(include_plotlyjs=True,full_html=True)
    marker=doc.rfind('Plotly.newPlot(')
    doc=doc[:marker]+'window.PlotlyGeoAssets={topojson:{usa_110m:'+(ROOT/'data/usa_110m.json').read_text(encoding='utf-8')+'}};'+doc[marker:]
    # Plotly genera el identificador de la figura; el contenedor se localiza por clase.
    selected=[h for h in hubs if airport=='Todos' or h['code']==airport]
    options={'hubs':selected,'coords':json.loads((ROOT/'data/airport_coords.json').read_text(encoding='utf-8')),'names':AIRPORTS,'height':440}
    style=(ROOT/'web/leaflet.css').read_text(encoding='utf-8')+(ROOT/'web/methodology.css').read_text(encoding='utf-8')+'body{margin:0;background:#10192b;font-family:Arial,sans-serif;color:#e8eef8}'
    extra='<style>'+style+'</style><script>'+(ROOT/'web/leaflet.js').read_text(encoding='utf-8')+'</script><script>'+(ROOT/'web/real_map.js').read_text(encoding='utf-8')+'</script>'
    script='<script>setTimeout(()=>FlightMap.mount(document.querySelector(".plotly-graph-div"),'+safe(options)+'),100);</script>'
    return doc.replace('</head>',extra+'</head>').replace('</body>',script+'</body>')
