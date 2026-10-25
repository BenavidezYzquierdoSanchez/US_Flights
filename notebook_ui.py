"""Presentación del notebook usando las mismas tarjetas del dashboard."""
import html
from analytics import ROOT
from map_widget import map_html

def panel(content):
    css='\n'.join((ROOT/'web'/name).read_text(encoding='utf-8') for name in ['font.css','kpi.css','methodology.css','project.css'])
    css+='\n.notebook-dashboard .kpis{grid-template-columns:repeat(2,minmax(0,1fr))}'
    return '<style>'+css+'</style><div class="notebook-dashboard" style="background:#070d18;color:#e8eef8;padding:22px;font-family:Manrope,Arial,sans-serif">'+content+'</div>'

def map_view(figure,hubs):
    doc=map_html(figure,hubs)
    return '<iframe title="Mapa real y vectorial de aeropuertos" style="width:100%;height:580px;border:0" srcdoc="'+html.escape(doc,quote=True)+'"></iframe>'

def show(content):
    from IPython.display import HTML,display
    display(HTML(content))
