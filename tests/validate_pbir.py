"""Valida las definiciones PBIR con los esquemas públicos de Microsoft.
Requiere jsonschema e Internet. No sustituye Power BI Desktop ni un motor DAX.
"""
import json,urllib.request
from pathlib import Path
from jsonschema import Draft7Validator,RefResolver
ROOT=Path(__file__).resolve().parents[1];cache={};validated=[]
def get(uri):
    url=uri.split('#')[0]
    if url in cache:return cache[url]
    try:
        raw=urllib.request.urlopen(url,timeout=20).read()
    except Exception:
        # Algunos esquemas públicos usan un $id con punto y URL con guion.
        if 'schema.embedded.json' not in url:raise
        raw=urllib.request.urlopen(url.replace('schema.embedded.json','schema-embedded.json'),timeout=20).read()
    v=json.loads(raw);cache[url]=v
    if '$id' in v:cache[v['$id']]=v
    return v
for path in sorted((ROOT/'powerbi').rglob('*.json')):
    obj=json.loads(path.read_text(encoding='utf-8'));uri=obj.get('$schema')
    if not uri:continue
    schema=get(uri)
    resolver=RefResolver(uri,schema,handlers={'https':get,'http':get},store=cache)
    errors=list(Draft7Validator(schema,resolver=resolver).iter_errors(obj))
    if errors:
        for err in errors[:3]:print(path,list(err.path),err.message)
        raise RuntimeError('Definición incompatible con el esquema')
    validated.append(str(path.relative_to(ROOT/'powerbi')))
result={'status':'PASS','files':len(validated),'schemas':list(cache),'desktop_execution':'NOT_RUN'}
(ROOT/'docs/schema_validation.json').write_text(json.dumps(result,indent=2))
print('PASS:',len(validated),'archivos de definición; no incluye ejecución Desktop/DAX.')
