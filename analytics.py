"""Métricas auditables sobre el cubo agregado; no reconstruye vuelos individuales."""
from pathlib import Path
import json
import math
import pandas as pd
from labels import enrich

ROOT = Path(__file__).resolve().parent
DIMS = ['Year', 'Month', 'Airline', 'OriginState', 'Haul']
MEASURES = ['ops','ontime','delayed15','delayed60','cancel','divert','sumDelayMin',
            'carrierDelay','weatherDelay','nasDelay','secDelay','lateAirDelay']
CAUSES = {'carrierDelay':'Aerolínea','weatherDelay':'Clima','nasDelay':'Sistema aéreo (NAS)',
          'secDelay':'Seguridad','lateAirDelay':'Aeronave previa'}
COLORS = ['#2ee6a6','#2ec4b6','#f5b942','#f07178','#5b8def']

def load_data(path=None):
    payload = enrich(json.loads(Path(path or ROOT/'data/source.json').read_text(encoding='utf-8')))
    d = pd.DataFrame(payload['cube'])
    required = set(DIMS + MEASURES)
    if not required.issubset(d):
        raise ValueError(f'Faltan campos: {required-set(d)}')
    for col in MEASURES+['Year','Month']:
        d[col] = pd.to_numeric(d[col], errors='raise')
    if d[DIMS+MEASURES].isna().any().any() or (d[MEASURES]<0).any().any():
        raise ValueError('Hay valores nulos o negativos: revisar antes de analizar.')
    if d.duplicated(DIMS).any():
        raise ValueError('Existen claves de agregado duplicadas.')
    if not d.Month.between(1,12).all() or (d.delayed60>d.delayed15).any():
        raise ValueError('Mes o jerarquía de demoras inválidos.')
    for c in ['ops','ontime','delayed15','delayed60','cancel','divert']:
        if (d[c] % 1 != 0).any():
            raise ValueError(f'{c} debe contener conteos enteros.')
    d['Unclassified'] = d.ops-d[['ontime','delayed15','cancel','divert']].sum(axis=1)
    if (d.Unclassified<0).any():
        raise ValueError('Los estados de vuelo superan el total de operaciones.')
    d['CauseGap'] = d[list(CAUSES)].sum(axis=1)-d.sumDelayMin
    d['CauseValid'] = d.CauseGap.abs() <= 1  # tolerancia de un minuto por agregado
    d['Period'] = d.Year.astype(str)+'-'+d.Month.astype(str).str.zfill(2)
    d['RowId'] = range(1,len(d)+1)
    return payload,d

def subset(d, filters=None):
    out=d
    for col,value in (filters or {}).items():
        if value is not None and value != 'Todos':
            out=out[out[col]==value]
    return out.copy()

def ratio(a,b,scale=100):
    return float(a)/float(b)*scale if b else None

def metrics(d):
    s=d[MEASURES+['Unclassified']].sum()
    return {'ops':int(s.ops),'otp':ratio(s.ontime,s.ops),
            'delay15':ratio(s.delayed15,s.ops),'delay60':ratio(s.delayed60,s.ops),
            'cancelRate':ratio(s.cancel,s.ops),'divertRate':ratio(s.divert,s.ops),
            'avgDelay':ratio(s.sumDelayMin,s.delayed15,1),
            'unclassified':int(s.Unclassified),'causeCoverage':ratio(d.loc[d.CauseValid,'ops'].sum(),s.ops)}

def grouped(d,key):
    g=d.groupby(key,as_index=False,observed=True)[MEASURES+['Unclassified']].sum().sort_values(key)
    g['otp']=100*g.ontime/g.ops.replace(0,float('nan'))
    g['cancelRate']=100*g.cancel/g.ops.replace(0,float('nan'))
    g['delayRate']=100*g.delayed15/g.ops.replace(0,float('nan'))
    return g

def wilson(successes,n,z=1.96):
    if not n:
        return None,None
    p=successes/n
    center=(p+z*z/(2*n))/(1+z*z/n)
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return 100*(center-half),100*(center+half)

def audit(d,payload):
    m=metrics(d)
    return {'rows':len(d),'date_min':d.Period.min(),'date_max':d.Period.max(),
            'months_observed':int(d.Period.nunique()),'metrics':m,
            'duplicates':int(d.duplicated(DIMS).sum()),'nulls':int(d[DIMS+MEASURES].isna().sum().sum()),
            'invalid_cause_rows':int((~d.CauseValid).sum()),
            'unclassified_rows':int((d.Unclassified>0).sum()),
            'states':sorted(d.OriginState.unique().tolist()),
            'weekly_rows':len(payload.get('dow',[])),
            'year_coverage':d.groupby('Year').Month.nunique().to_dict()}

def fmt(v,dec=1):
    return 'Sin datos' if v is None or pd.isna(v) else f'{v:,.{dec}f}'
