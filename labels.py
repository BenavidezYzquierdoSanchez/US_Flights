"""Catálogos descriptivos: los códigos originales continúan siendo las claves."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
CARRIERS=json.loads((ROOT/'data/carrier_names.json').read_text(encoding='utf-8'))
AIRPORTS=json.loads((ROOT/'data/airport_names.json').read_text(encoding='utf-8'))
def airline_label(code):return f'{code} — {CARRIERS.get(code,"Nombre no disponible")}' if code!='Todos' else code
def airport_label(code):return f'{code} — {AIRPORTS.get(code,"Nombre no disponible")}' if code!='Todos' else code
def enrich(payload):
    for r in payload['cube']:
        r['AirlineName']=CARRIERS.get(r['Airline'],'Nombre no disponible')
        r['AirlineLabel']=airline_label(r['Airline'])
    for r in payload.get('hubs',[]):
        r['AirportName']=AIRPORTS.get(r['code'],'Nombre no disponible')
        r['AirportLabel']=airport_label(r['code'])
    return payload
